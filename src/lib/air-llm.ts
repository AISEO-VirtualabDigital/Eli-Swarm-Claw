/**
 * Air LLM — Lightweight Gemini-powered retrieval + generation
 * 
 * Designed for the Obsidian micro-chunk engine:
 * - Takes a user query
 * - Retrieves relevant micro-chunks from the vault
 * - Builds a compact, chunk-aware prompt
 * - Calls Gemini for generation
 * - Returns response with source tracking
 * 
 * "Air" = lightweight, no heavy infrastructure
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { getVault, ObsidianVault } from './obsidian-chunk-engine';
import { getOmniRoute } from './omni-route';

export interface AirLLMResponse {
  response: string;
  provider: string;
  chunksUsed: number;
  skillsUsed: number;
  sources: Array<{ title: string; source: string; category: string }>;
  containmentHits?: number;
}

export interface AirLLMConfig {
  apiKey: string;
  model?: string;
  vaultPath?: string;
  maxChunks?: number;
  systemPrompt?: string;
}

const DEFAULT_MODEL = 'gemini-2.0-flash';

export class AirLLM {
  private genAI: GoogleGenerativeAI;
  private model: string;
  private vault: ObsidianVault;
  private maxChunks: number;
  private systemPrompt: string;
  private initialized = false;

  constructor(config: AirLLMConfig) {
    this.genAI = new GoogleGenerativeAI(config.apiKey);
    this.model = config.model || DEFAULT_MODEL;
    this.vault = getVault(config.vaultPath);
    this.maxChunks = config.maxChunks || 10;
    this.systemPrompt = config.systemPrompt || '';
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    await this.vault.init();
    this.initialized = true;
  }

  /**
   * Main entry point: query → retrieve → generate
   */
  async chat(
    message: string,
    history: Array<{ role: string; content: string }> = [],
    systemPromptOverride?: string
  ): Promise<AirLLMResponse> {
    await this.initialize();

    // 1. Retrieve micro-chunks from vault
    const { context, sources } = await this.vault.buildAirContext(message);

    // 2. Check containment (dissolved knowledge) for additional hits
    let containmentHits = 0;
    const containmentResults = await this.vault.searchContainment(message, { maxResults: 3 });
    const dissolvedContext = containmentResults
      .filter(r => r.dissolved)
      .map(r => r.chunk.content.slice(0, 200))
      .join('... ');
    containmentHits = containmentResults.filter(r => r.dissolved).length;

    // 3. Build the system message
    const systemPrompt = systemPromptOverride || this.systemPrompt;
    const systemContent = [
      systemPrompt,
      '',
      context,
      dissolvedContext ? `
---
CONTAINMENT MEMORY (${containmentHits} dissolved chunks recovered):
${dissolvedContext}
These are pattern memories from previously dissolved knowledge. Use them if relevant.
---` : '',
    ].join('\n');

    // 4. Build conversation
    const contents: Array<{ role: 'user' | 'model'; parts: Array<{ text: string }> }> = [];
    
    // Add recent history (last 6 turns)
    const recentHistory = history.slice(-6);
    for (const h of recentHistory) {
      contents.push({
        role: h.role === 'eli' ? 'model' : 'user',
        parts: [{ text: h.content }],
      });
    }

    // Add current message
    contents.push({
      role: 'user',
      parts: [{ text: message }],
    });

    // 5. Call Gemini
    try {
      const genModel = this.genAI.getGenerativeModel({
        model: this.model,
        systemInstruction: systemContent,
      });

      const result = await genModel.generateContent({ contents });
      const response = result.response.text();

      return {
        response,
        provider: `gemini-${this.model}`,
        chunksUsed: context ? this.maxChunks : 0,
        skillsUsed: 0,
        sources,
        containmentHits,
      };
    } catch (error) {
      console.error('Air LLM Gemini call failed:', error);
      
      // Fallback: return chunk-sourced context even without LLM
      if (context || dissolvedContext) {
        return {
          response: buildFallbackResponse(sources, containmentHits, message),
          provider: 'fallback-chunks',
          chunksUsed: sources.length,
          skillsUsed: 0,
          sources,
          containmentHits,
        };
      }

      return {
        response: 'I hit a wall — my knowledge engine is running but the LLM backend needs attention. Check the Gemini API key.',
        provider: 'error',
        chunksUsed: 0,
        skillsUsed: 0,
        sources: [],
      };
    }
  }

  /**
   * Skill-aware query: find the best matching skill pattern
   */
  async querySkill(skillName: string): Promise<{ id: string; name: string; pattern: string; strength: number } | null> {
    await this.initialize();
    const skills = await this.vault.getSkills();
    const lower = skillName.toLowerCase();
    return skills.find(s => s.name.toLowerCase().includes(lower)) || null;
  }

  /**
   * Get vault stats
   */
  async getStats(): Promise<{ index: any; activeSkills: number } | null> {
    await this.initialize();
    const index = await this.vault.getIndex();
    const skills = await this.vault.getSkills();
    return { index, activeSkills: skills.length };
  }
}

function buildFallbackResponse(
  sources: Array<{ title: string; source: string; category: string }>,
  containmentHits: number,
  query: string
): string {
  if (sources.length === 0 && containmentHits === 0) {
    return `Nothing in the vault matches "${query}" yet. Once we ingest more knowledge, I'll have sharper answers.`;
  }

  const parts: string[] = [];
  if (sources.length > 0) {
    parts.push(`Found ${sources.length} relevant source${sources.length > 1 ? 's' : ''} in the vault:`);
    parts.push(...sources.map((s, i) => `${i + 1}. **${s.title}** [${s.category}]`));
  }
  if (containmentHits > 0) {
    parts.push(`\nAlso recovered ${containmentHits} pattern${containmentHits > 1 ? 's' : ''} from containment memory.`);
  }
  parts.push('\n(Operating in chunk-retrieval mode — LLM generation is offline)');

  return parts.join('\n');
}

// ─── Singleton ──────────────────────────────────────────────────────

let airInstance: AirLLM | null = null;

/**
 * Create or recreate the AirLLM instance with the current omni key.
 * Called when omni injects a new key so AirLLM picks it up.
 */
export function resetAirLLM(systemPrompt?: string): AirLLM {
  const omni = getOmniRoute();
  const apiKey = omni.getGeminiKey();
  if (!apiKey || (apiKey.startsWith('Astralform') && !apiKey.startsWith('AQ.'))) {
    console.warn('[AirLLM] No valid Gemini key from omni — will operate in fallback mode');
    airInstance = new AirLLM({
      apiKey: 'fallback',
      systemPrompt: systemPrompt || '',
      vaultPath: process.env.OBSIDIAN_VAULT_PATH,
    });
    return airInstance;
  }
  airInstance = new AirLLM({
    apiKey,
    systemPrompt: systemPrompt || '',
    vaultPath: process.env.OBSIDIAN_VAULT_PATH,
  });
  return airInstance;
}

export function getAirLLM(systemPrompt?: string): AirLLM {
  if (!airInstance) {
    return resetAirLLM(systemPrompt);
  }
  return airInstance;
}