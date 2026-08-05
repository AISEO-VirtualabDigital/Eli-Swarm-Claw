# Skill and Harness Manager — Obsidian Plugin Reference

## Overview

The Skill and Harness Manager is an Obsidian plugin that consolidates, organizes, and runs AI skills directly from the Obsidian vault. It discovers SKILL.md files across multiple directories (.claude/, .codex/, .cursor/, .agents/, marketplace folders), lets users organize/filter/tag them, and makes each skill runnable with a click.

Key principle: No bundled model, no inference, no network calls. It finds, organizes, and launches. The actual AI work runs in whatever CLI you point it at (Claude Code, Codex, omnigent, or your own).

## Capabilities

- **Right-click a file** → run a skill targeting that file (reformat, transcribe, summarize)
- **Sidebar buttons** → pin any skill to its own ribbon icon with a custom Lucide icon
- **Command palette** → every pinned skill registers a command
- **Browser view** → Skills, Commands, Scripts, Sessions, Agents, Harnesses tabs
- **Launch modes**: Headless (background) or Terminal (visible, interactive)
- **Custom harnesses**: Add Claude Code, Codex, or any CLI as a launch target
- **Sessions**: Track launches, reconnect to running sessions
- **Bash scripts**: User-authored scripts with headless/terminal modes
- **Tag system**: Tags from frontmatter, description #hashtags, and folder-derived virtual tags
- **Hidden file support**: Reveal .claude/, .codex/ etc. in the file explorer

## Architecture

### Plugin Settings (SkillLayerSettings)

// Shared types for the Skill and Harness Manager plugin.

import type { CustomHarness, SkillAgent } from "./launch";
import type { LaunchedSession } from "./sessions";

/**
 * How a skill/command/script is launched:
 * - `headless` — spawned detached (the prior behavior); output surfaces only via
 *   Notices and the Sessions tab.
 * - `terminal` — opens the user's default terminal running the preferred CLI (or,
 *   for a script, the script body) interactively in the vault.
 */
export type LaunchMode = "headless" | "terminal";

/**
 * A user-defined bash script (Bash Scripts tab). Stored plugin-local in data.json;
 * `body` is a full shell script authored by the user and run ONLY on an explicit
 * click (same trust model as custom harnesses). `launchMode` is per-script.
 */
export interface BashScript {
  /** Stable id (generated from the label). */
  id: string;
  /** Display name. */
  label: string;
  /** Optional one-line description shown on the row. */
  description?: string;
  /** The shell script body (multi-line allowed). */
  body: string;
  /** headless (detached, Notices only) or terminal (visible, live output). */
  launchMode: LaunchMode;
}

/** How a scan root is walked. Determines which of the two+1 code paths runs. */
export type RootKind = "vault" | "adapter" | "external";

/** How a given skill was discovered (mirrors the root kind that found it). */
export type DetectionMethod = "vault" | "adapter" | "external";

/**
 * Where a resolved tag came from.
 * - `frontmatter` — the YAML `tags:` field. This is the SINGLE authoritative
 *   place the UI writes; only these chips are removable.
 * - `description` — a `#tag` token in the description text. READ-ONLY in the
 *   UI (edit the note to change it).
 * - `folder` — derived/virtual from the file's location. Never written, READ-ONLY.
 */
export type TagOrigin = "frontmatter" | "description" | "folder";

/** A resolved tag attached to a skill, labeled by origin for the UI. */
export interface SkillTag {
  tag: string;
  origin: TagOrigin;
}

/** A configurable directory the detector scans for skills. */
export interface ScanRoot {
  /**
   * For `vault`/`adapter` roots: a vault-relative path (`""` = vault root,
   * `.claude/skills`, `skills`, …). For `external` roots: an absolute
   * filesystem path.
   */
  path: string;
  kind: RootKind;
  enabled: boolean;
}

/** A discovered browsable item: a skill (default) or a command (M18). Both share
 *  the same shape and reuse the same row UI / per-item state (pins, right-click,
 *  harness, agent) keyed by `id`; only discovery + launch wording differ. */
export type ItemKind = "skill" | "command";

/** A single discovered skill (or command — see `kind`). */
export interface Skill {
  /** Stable id = the normalized absolute path. Used for pins, commands, dedupe. */
  id: string;
  /** "skill" (default/absent) or "command" (M18). */
  kind?: ItemKind;
  name: string;
  description: string;
  /** Absolute filesystem path to the skill markdown file. */
  path: string;
  /** Vault-relative path when the file lives inside the vault, else null. */
  vaultPath: string | null;
  /** The configured root (its `path`) that surfaced this skill. */
  sourceRoot: string;
  /** Inferred harness/source label, e.g. `.claude`, `codex`, `vault`. */
  sourceLabel: string;
  detection: DetectionMethod;
  /** Resolved, deduped, sorted tags from description + frontmatter + folder. */
  tags: SkillTag[];
}

export interface SkillLayerSettings {
  scanRoots: ScanRoot[];
  /** Absolute paths (= skill ids) pinned to their own ribbon icon. */
  pinnedSkillIds: string[];
  /**
   * Absolute paths (= skill ids) whose skill is exposed in the file explorer
   * right-click (file-menu) as `Run "<name>" here`. Per-skill `rightClickEnabled`
   * is modeled as membership here (default off = absent). Plugin-local state
   * only — never written into any SKILL.md.
   */
  rightClickSkillIds: string[];
  /**
   * Per-skill Lucide icon for the pinned ribbon icon, keyed by skill id (the
   * same stable path used in `pinnedSkillIds`). Plugin-local state only — never
   * written into any SKILL.md.
   */
  skillIcons: Record<string, string>;
  /**
   * Per-skill AGENT choice, keyed by skill id (the same stable path used in
   * `skillIcons`/`pinnedSkillIds`). The value is a discriminated object
   * (`{kind:'default'}` | `{kind:'builtin',name}` | `{kind:'custom',path}`); an
   * absent key = the Default agent. At launch the stored value is re-validated
   * fail-closed by `resolveAgentLaunch` (built-in name must be in the hardcoded
   * allowlist; custom path must still exist inside the scan dir and end in
   * .yaml/.yml), so any unrecognized or stale value resolves to Default. Plugin-
   * local state only — never written into any SKILL.md.
   */
  skillAgent: Record<string, SkillAgent>;
  /**
   * Per-skill omnigent HARNESS choice (M15), keyed by skill id (same stable path
   * used in `skillAgent`/`skillIcons`). The value is a harness NAME string; an
   * absent key = no `--harness` (omnigent uses its own configured default).
   * ORTHOGONAL to `skillAgent` — a skill can pin both an agent and a harness. At
   * launch the value is re-validated fail-closed by `resolveHarness` against the
   * hardcoded `OMNIGENT_HARNESSES` allowlist, so any unrecognized or stale value
   * (incl. a legacy object shape from the removed M4–M7 harness selector) simply
   * emits no `--harness`. Plugin-local state only — never written into any
   * SKILL.md.
   */
  skillHarness: Record<string, string>;
  /**
   * Per-skill CLAUDE SUBAGENT choice (M17), keyed by skill id. The value is a
   * `.claude/agents/*.md` subagent NAME. Applies ONLY when the skill's harness is
   * a claude-based CUSTOM harness (omnigent agents live in `skillAgent`); it is
   * substituted into the harness command's `{agent}` token at launch. An absent
   * key = no agent. Re-validated against the discovered subagents before use, so
   * a stale name degrades to none. Plugin-local; never written into any SKILL.md.
   */
  skillClaudeAgent: Record<string, string>;
  /**
   * User-defined custom harnesses (M15.3) — arbitrary external commands the
   * per-skill Harness dropdown can select instead of an omnigent `--harness`.
   * Each is `{id, label, command[]}` where `command[0]` is an absolute binary
   * and one token holds `{prompt}`. This is the plugin's only non-omnigent spawn
   * target; every launch re-validates fail-closed (`resolveSkillHarness` +
   * `isValidCustomHarnessCommand` + an existence check on the binary). Managed
   * from the Harnesses tab. Plugin-local state — never written into any SKILL.md.
   */
  harnesses: CustomHarness[];
  /** Absolute path to the omnigent binary; blank = auto-detect by probing. */
  omnigentBinaryPath: string;
  /**
   * Omnigent `--server` target for launches (M19). Blank = omit `--server` so
   * omnigent uses its own config/default routing. A value (e.g. `local` or a
   * host URL like `https://your-omnigent-host`) is passed as
   * `--server <value>` on every omnigent launch: with a host URL this selects
   * omnigent's local-runner + remote-server topology (work runs LOCALLY in the
   * vault, models come from the host), which sends a RELATIVE cwd the multi-
   * tenant server accepts — avoiding the absolute-cwd rejection that occurs when
   * omnigent falls back to connecting directly to a remote server. The host URL
   * changes over time, so this is user-editable in Settings. Passed as a single
   * inert argv element (shell:false); a value with whitespace is ignored.
   */
  omnigentServerUrl: string;
  /** Append the generic vault-anchor instruction to the launch prompt. */
  appendVaultAnchor: boolean;
  /**
   * Reveal hidden dot-folders (e.g. `.claude/`) in Obsidian's file explorer
   * (M15). When on, the plugin patches the vault adapter's private reconcile
   * path to surface dotfiles and suppresses the "bad dotfile" warning; when off
   * (default), the explorer behaves normally. Cleanly reverted on toggle-off and
   * on unload. NOTE: relies on undocumented Obsidian internals (see
   * `hiddenFiles.ts`).
   */
  showHiddenFolders: boolean;
  /**
   * Sessions the plugin has launched (M20), newest-appended. Each is a resumable
   * omnigent/claude/codex conversation shown in the Sessions tab. Pruned on view
   * (dropped when older than 12h or no longer resumable). Plugin-local state.
   */
  sessions: LaunchedSession[];
  /**
   * Preferred TERMINAL EMULATOR id (a `KNOWN_TERMINALS` id from `terminal.ts`)
   * used for TERMINAL launches — which terminal app opens to run the skill's
   * harness command. Blank / "auto" = the OS default terminal. Re-validated
   * fail-closed at launch by `resolvePreferredTerminal` against the
   * actually-detected set, so a stale/uninstalled id falls back to auto.
   * Plugin-local state.
   */
  preferredTerminal: string;
  /**
   * Global default launch mode for skills/commands (headless or terminal). A
   * per-item override in `skillLaunchMode` wins when present. Default `headless`
   * (the prior behavior). Plugin-local state.
   */
  defaultLaunchMode: LaunchMode;
  /**
   * Per-item launch-mode OVERRIDE, keyed by skill/command id (the same stable
   * path used across the other per-skill maps). Absent key = use
   * `defaultLaunchMode`. Plugin-local state; never written into any SKILL.md.
   */
  skillLaunchMode: Record<string, LaunchMode>;
  /**
   * User-defined bash scripts (Bash Scripts tab). Each is `{id,label,description?,
   * body,launchMode}`; the body runs only on explicit click. Managed from the
   * tab's add/edit form. Plugin-local state — never written into any SKILL.md.
   */
  bashScripts: BashScript[];
  /**
   * Preferred width (px) the browser side panel opens at, so the ribbon/command
   * open always uses a consistent "proper" width rather than whatever the user
   * last dragged the sidebar to. Applied best-effort to the right sidebar's
   * container on open (undocumented layout internals; no-ops if unavailable).
   */
  panelWidth: number;
  /**
   * True once the bundled example skill has been seeded to
   * `<vault>/.agents/skills/`. Set after the first successful seed so deleting the
   * example never recreates it. Plugin-local state.
   */
  seededExample?: boolean;
  /**
   * Global default pinned-ribbon icon — the fallback used by any pinned skill
   * that has no per-skill icon in `skillIcons`. Set via the settings selector
   * (also the migration fallback for pins created before per-skill icons).
   * Optional so new installs omit it and fall back to DEFAULT_PINNED_ICON.
   */
  pinnedIcon?: string;
}

export const DEFAULT_SETTINGS: SkillLayerSettings = {
  scanRoots: [
    { path: "", kind: "vault", enabled: true },
    { path: ".claude/skills", kind: "adapter", enabled: true },
  ],
  pinnedSkillIds: [],
  rightClickSkillIds: [],
  skillIcons: {},
  skillAgent: {},
  skillHarness: {},
  skillClaudeAgent: {},
  harnesses: [],
  omnigentBinaryPath: "",
  omnigentServerUrl: "",
  appendVaultAnchor: true,
  showHiddenFolders: false,
  sessions: [],
  preferredTerminal: "",
  defaultLaunchMode: "headless",
  skillLaunchMode: {},
  bashScripts: [],
  panelWidth: 520,
};


### Launch System

// Launch-construction helpers (no Obsidian imports) — the argv builder, binary
// allowlist/resolution, and PATH augmentation are all unit-testable. The actual
// spawn (impure) lives in main.ts and consumes these. The custom-agent path
// gate additionally needs `fs` for its symlink-aware (realpath) containment
// check; those fs calls are injectable so the resolver stays unit-testable, and
// default to the real `fs` so existing call sites need no change.

import * as fs from "fs";
import * as nodePath from "path";

/** The only binary this milestone (M1) is allowed to spawn. */
export const OMNIGENT_BIN_NAME = "omnigent";

/**
 * Build the launch prompt as NATURAL LANGUAGE, not a `/slash` form. `omnigent
 * run -p` routes a leading-slash first token to its REPL slash-command
 * dispatcher (which has no skill commands → "Unknown command"); a plain
 * sentence goes through normal model input and lets the host skill be selected
 * natively from the vault cwd. Form: `Use the <name> skill.` optionally
 * followed by a `Context file: <path>.` clause (the M3 right-click path) and/or
 * a generic vault-anchor instruction naming the real vault path.
 *
 * `contextPath` is the M3 addition: when present (the file-explorer right-click
 * path) the clicked file/folder's ABSOLUTE path is embedded as a pure TEXT
 * fragment inside this single returned string — it is NEVER its own argv
 * element and is never parsed as a flag. Because a context launch operates on a
 * specific path, the vault anchor is ALWAYS included on that path (regardless
 * of `appendAnchor`) so writes stay scoped to the vault. When `contextPath` is
 * absent the M1 behavior is byte-for-byte preserved (no Context line; anchor
 * only when `appendAnchor`).
 *
 * Returned as ONE inert string for a single `-p` argv element. Never starts
 * with `/`. Skill-agnostic (substitutes any `skillName`).
 */
export function buildLaunchPrompt(
  skillName: string,
  vaultPath: string,
  appendAnchor: boolean,
  contextPath?: string,
  userPrompt?: string,
  kind: "skill" | "command" = "skill",
): string {
  // A command (M18) is a `/name` slash command; a skill is invoked by name. The
  // command form starts with "Run" (NOT a leading slash) so omnigent's REPL
  // slash-dispatcher isn't triggered, while still naming the `/command` for
  // Claude-family harnesses to execute.
  const base =
    kind === "command"
      ? `Run the /${skillName} command.`
      : `Use the ${skillName} skill.`;
  // M16: optional free-text the user typed in the Launch modal, appended right
  // after the skill directive so the session reads `Use the <name> skill.
  // <their instructions>` — giving skills that need more context something to
  // act on. It reaches argv only as part of the single inert `-p` element (or,
  // for a custom harness, control-char-stripped into one token), so free text —
  // spaces, quotes, dashes — is safe and never tokenized. Empty/whitespace →
  // omitted, preserving the exact prior prompt.
  const extra = typeof userPrompt === "string" ? userPrompt.trim() : "";
  const withUser = extra ? `${base} ${extra}` : base;
  const hasContext = typeof contextPath === "string" && contextPath.length > 0;
  // The path is concatenated as inert prose — never split out as a separate
  // token — so any spaces/quotes/dashes/metacharacters in it stay contained.
  const head = hasContext ? `${withUser} Context file: ${contextPath}.` : withUser;
  // No context + anchor off + no user text → exactly the M1 prompt.
  if (!appendAnchor && !hasContext) return head;
  return (
    `${head} Operate in this vault: ${vaultPath}.` +
    " Write any files into this vault directory only." +
    " Do not create a git worktree or delegate the final file write."
  );
}

/**
 * Build the omnigent one-shot argv array (UI-visible run; exits on its own).
 * The per-skill AGENT selection (already resolved fail-closed by
 * `resolveAgentLaunch`) determines the subcommand and any positional; the
 * per-skill HARNESS selection (M15, resolved fail-closed by `resolveHarness`)
 * OPTIONALLY appends `--harness <h>`:
 *   - default          → [bin, 'run', '-p', prompt]
 *   - builtin          → [bin, <name>, '-p', prompt]  (subcommand, NOT 'run')
 *   - custom           → [bin, 'run', <abs agent path>, '-p', prompt]
 *   - + harness (any)  → …, '--harness', <h>, '-p', prompt
 * For a custom agent the path (a loose `.yaml`/`.yml` FILE or a BUNDLE directory)
 * is emitted as a SINGLE inert argv element after `run` — never split, never its
 * own flag (the resolver guarantees it is an absolute path, so it can never be
 * read as an option). No '--no-session'
 * (that path is ephemeral / not UI-visible). The prompt is a single inert
 * element.
 *
 * `harness` (M15) is emitted as `--harness <value>` ONLY when it is a member of
 * the hardcoded `OMNIGENT_HARNESSES` allowlist (re-checked here as
 * belt-and-suspenders; callers pass a value already resolved by
 * `resolveHarness`). It routes through the SAME omnigent binary — `omnigent run`
 * accepts `--harness`, and bundled subcommands (polly/debby) forward all run
 * options — so it is correct for every agent form. Never free text, never a
 * positional.
 *
 * No `--server` is EVER emitted (M11): omnigent's own config.yaml decides server
 * routing, so `omnigent run <agent>` with no `--server` routes via the user's
 * omnigent config. This removed the overlap with omnigent's own configuration.
 */
export function buildOmnigentArgv(opts: {
  binaryPath: string;
  prompt: string;
  agent?: ResolvedAgent;
  harness?: string | null;
  server?: string | null;
}): string[] {
  const agent: ResolvedAgent = opts.agent ?? { mode: "default" };
  const subcommand = agent.mode === "builtin" ? agent.name : "run";
  const argv = [opts.binaryPath, subcommand];
  // The custom agent path is a single inert positional after `run` — a loose
  // `.yaml`/`.yml` file or a bundle directory. The resolver has already proven
  // it absolute + a real direct child of the scan dir, so it can never split or
  // become a flag.
  if (agent.mode === "custom") argv.push(agent.path);
  // Optional omnigent `--server` target (M19). A single inert argv element
  // (shell:false); validated to a whitespace-free token so it can never split.
  if (isValidOmnigentServer(opts.server)) argv.push("--server", opts.server.trim());
  // Optional omnigent harness pin (M15). Only a hardcoded-allowlist member is
  // ever emitted, so the value can never be free text or a flag-able positional.
  if (isAllowedHarness(opts.harness)) argv.push("--harness", opts.harness);
  argv.push("-p", opts.prompt);
  return argv;
}

/**
 * Whether a user-configured omnigent `--server` value is safe to emit: a
 * non-empty, whitespace-free single token (e.g. `local` or a host URL). Empty /
 * blank = omit `--server` (omnigent uses its own default). A value containing
 * ANY whitespace is rejected (would otherwise become multiple argv elements or a
 * confusing single one), failing closed to "no --server". Pure / unit-testable.
 */
export function isValidOmnigentServer(
  server: string | null | undefined,
): server is string {
  return typeof server === "string" && server.trim().length > 0 && !/\s/.test(server.trim());
}

/**
 * The FIXED skill invocation string for the "Copy invocation" row action
 * (manual REPL/clipboard paste). Natural-language form `Use the <name> skill.`,
 * consistent with how launch prompts are built (`buildLaunchPrompt`'s base).
 * There is no user-configurable template (M11). Embeds NO path, so no shell
 * quoting is required. Pure / unit-testable.
 */
export function buildSkillInvocation(
  skillName: string,
  kind: "skill" | "command" = "skill",
): string {
  return kind === "command"
    ? `Run the /${skillName} command.`
    : `Use the ${skillName} skill.`;
}

/**
 * The agent-aware copyable CLI for the Skills-tab "Copy invocation" action. Where
 * `buildSkillInvocation` is the bare REPL prompt (agent-agnostic), this reflects
 * the per-skill AGENT selection so the copied command runs the skill under the
 * chosen agent — mirroring `buildOmnigentArgv`'s subcommand/positional shape, but
 * as a single shell-pasteable string using the `omnigent` bin NAME (not an
 * absolute binary path, matching `buildAgentInvocation`):
 *   - default → omnigent run -p '<prompt>'
 *   - builtin → omnigent <name> -p '<prompt>'        (subcommand, NOT 'run')
 *   - custom  → omnigent run '<abs path>' -p '<prompt>'
 *   - + harness (any) → … --harness <h> -p '<prompt>'
 * `agent` MUST already be resolved fail-closed by `resolveAgentLaunch`, so a
 * custom path is the validated absolute real path. The custom path and the prompt
 * are each POSIX single-quote wrapped so spaces / shell metacharacters paste as
 * one safe argument. `harness` (M15) is appended as `--harness <h>` only when it
 * is a hardcoded-allowlist member (so it can carry no metacharacters and needs
 * no quoting). Clipboard text only — pure / unit-testable.
 */
export function buildSkillCliInvocation(opts: {
  skillName: string;
  agent?: ResolvedAgent;
  harness?: string | null;
  server?: string | null;
  kind?: "skill" | "command";
}): string {
  const agent: ResolvedAgent = opts.agent ?? { mode: "default" };
  const prompt = buildSkillInvocation(opts.skillName, opts.kind ?? "skill");
  const subcommand = agent.mode === "builtin" ? agent.name : "run";
  let cli = `${OMNIGENT_BIN_NAME} ${subcommand}`;
  if (agent.mode === "custom") cli += ` ${shellSingleQuote(agent.path)}`;
  if (isValidOmnigentServer(opts.server)) cli += ` --server ${shellSingleQuote(opts.server.trim())}`;
  if (isAllowedHarness(opts.harness)) cli += ` --harness ${opts.harness}`;
  cli += ` -p ${shellSingleQuote(prompt)}`;
  return cli;
}

/**
 * POSIX single-quote shell escaping: wrap `s` in single quotes and escape any
 * embedded single quote as `'\''`. This makes a path containing spaces or shell
 * metacharacters safe to paste into a shell as one argument. Used only for the
 * COPYABLE invocation strings (clipboard text); never for argv (argv is passed
 * to spawn with shell:false and needs no quoting). Pure / unit-testable.
 */
export function shellSingleQuote(s: string): string {
  return `'${s.replace(/'/g, "'\\''")}'`;
}

/**
 * Default opening prompt for a custom-agent SESSION launched from the Agents tab
 * (M10). That spawn is non-interactive (stdio ignored), so a sensible `-p`
 * prompt is passed so the session actually opens and is visible in the omnigent
 * UI. Reaches argv as the single inert `-p` element.
 */
export const AGENT_SESSION_PROMPT =
  "Hi — what can you help with in this vault?";

/**
 * Placeholder prompt embedded in the copyable Agents-tab invocation string
 * (M10). This is clipboard text only — it never reaches argv.
 */
export const AGENT_INVOCATION_PLACEHOLDER = "<your prompt here>";

/**
 * The exact CLI to start a session with a custom agent, for the Agents-tab
 * "Copy invocation" action (M10): `omnigent run '<agentPath>' -p "<placeholder>"`.
 * `agentPath` MUST be the validated absolute real path (a loose `.yaml`/`.yml`
 * file or a bundle directory) produced by `safeCustomAgentRealPath`. The path is
 * SHELL-QUOTED (POSIX single-quote wrap, M11) so a path containing spaces or
 * shell metacharacters pastes safely into a shell as one argument. Clipboard
 * text only — pure / unit-testable.
 */
export function buildAgentInvocation(agentPath: string): string {
  return `${OMNIGENT_BIN_NAME} run ${shellSingleQuote(agentPath)} -p "${AGENT_INVOCATION_PLACEHOLDER}"`;
}

// =====================================================================
// Per-skill AGENT selector (replaces the M1–M7 harness selector).
//
// A skill is tied to a specific omnigent AGENT; omnigent itself picks the
// harness. The stored, per-skill choice is a discriminated value:
//   { kind: 'default' }                       → `omnigent run -p "<prompt>"`
//   { kind: 'builtin', name: 'polly'|'debby'} → `omnigent <name> -p "<prompt>"`
//   { kind: 'custom',  path: '<abs yaml>' }   → `omnigent run <abs yaml> -p "<prompt>"`
// At LAUNCH the stored value is re-validated fail-closed by `resolveAgentLaunch`
// before anything reaches argv. Plugin-local state only — NEVER written into any
// SKILL.md, and the display label/description of a custom agent NEVER reaches
// argv (only its validated absolute path does, as one inert element).
// =====================================================================

/**
 * The hardcoded built-in agent allowlist. These launch via an omnigent
 * SUBCOMMAND (`omnigent polly …`, NOT `omnigent run …`). This is the ONLY set a
 * stored `{kind:'builtin'}` name is permitted against at launch; anything else
 * fails closed to the Default agent.
 */
export const BUILTIN_AGENTS = ["polly", "debby"] as const;
export type BuiltinAgentName = (typeof BUILTIN_AGENTS)[number];

// =====================================================================
// Per-skill HARNESS selector (M15) — ORTHOGONAL to the AGENT selector.
//
// A skill always runs through the `omnigent` binary; the AGENT choice picks the
// subcommand / positional (`run` | `polly`/`debby` | a custom agent YAML), and
// INDEPENDENTLY a skill may pin a specific omnigent harness via `--harness <h>`.
// Verified 2026-07-06 against the real CLI: `omnigent run --help` lists the
// fixed `--harness` set below (and shows `omnigent run <agent.yaml> --harness
// <h>` as a combine example), and `omnigent polly --help` states "All run
// options are accepted and forwarded" — so a bundled agent subcommand forwards
// `--harness`/`-p` too. Because the harness routes through the SAME omnigent
// binary, this introduces NO new spawn surface and NO new binary allowlist: the
// value is re-validated fail-closed against the hardcoded allowlist below and
// only ever emitted as `--harness <member>` (never free text, never a flag-able
// positional). Plugin-local state; never written into any SKILL.md.
// =====================================================================

/**
 * The hardcoded omnigent `--harness` allowlist (from `omnigent run --help`).
 * `claude` is omnigent's documented alias for `claude-sdk`; both are listed so a
 * stored value of either resolves. This is the ONLY set a stored per-skill
 * harness is permitted against at launch; anything else fails closed to "no
 * --harness" (omnigent then uses its own configured default harness).
 */
export const OMNIGENT_HARNESSES = [
  "claude",
  "claude-sdk",
  "codex",
  "cursor",
  "kimi",
  "openai-agents",
  "open-responses",
  "pi",
  "antigravity",
  "qwen",
  "goose",
  "copilot",
] as const;
export type OmnigentHarness = (typeof OMNIGENT_HARNESSES)[number];

/** The <select> option value meaning "no explicit harness" (omnigent's default). */
export const HARNESS_DEFAULT_VALUE = "default";

/** Membership test for the hardcoded harness allowlist. */
export function isAllowedHarness(name: unknown): name is OmnigentHarness {
  return (
    typeof name === "string" &&
    (OMNIGENT_HARNESSES as readonly string[]).includes(name)
  );
}

/**
 * Resolve a per-skill stored harness choice to the validated launch value,
 * FAILING CLOSED to null ("no --harness"; omnigent uses its own default). Only a
 * member of the hardcoded allowlist survives; anything else — absent, unknown
 * string, the `"default"` sentinel, or a stale legacy object shape from the
 * removed M4–M7 harness selector — resolves to null. Pure / unit-testable.
 */
export function resolveHarness(stored: unknown): OmnigentHarness | null {
  return isAllowedHarness(stored) ? stored : null;
}

/** Encode a stored harness choice to its <select> option value. */
export function encodeHarnessChoice(harness: unknown): string {
  return isAllowedHarness(harness) ? harness : HARNESS_DEFAULT_VALUE;
}

/** Decode a <select> option value to a harness name, or null for Default. */
export function decodeHarnessChoice(value: string): OmnigentHarness | null {
  return isAllowedHarness(value) ? value : null;
}

// =====================================================================
// CUSTOM (user-defined) harnesses (M15.3) — the escape hatch for a command the
// built-in omnigent `--harness` set does not cover (e.g. a different CLI or a
// preset omnigent invocation). A custom harness spawns an ARBITRARY external
// binary instead of omnigent, so it is the plugin's only non-omnigent spawn
// surface. SECURITY, in depth:
//   • `command[0]` (the binary) MUST be an ABSOLUTE path — validated at add-time
//     AND again fail-closed at launch — so it can never be a bare name resolved
//     through PATH (no hijack) nor read as a flag.
//   • args are stored as an ARRAY (the UI takes one arg per line), so there is
//     NEVER any shell-word tokenization (the defect class that cost 3 review
//     rounds). Spawned with shell:false.
//   • only the `{prompt}` placeholder is interpolated, control-char-stripped, and
//     substituted WITHIN a token (never as its own split element).
//   • a custom harness only ever runs when the user explicitly created it AND
//     selected it for a skill; anything invalid fails closed (no spawn).
// Plugin-local state; never written into any SKILL.md.
// =====================================================================

/** Placeholder token replaced with the launch prompt in a custom harness command. */
export const HARNESS_PROMPT_PLACEHOLDER = "{prompt}";

/**
 * OPTIONAL placeholder (M17) replaced with the selected Claude subagent name in a
 * custom-harness command, e.g. `claude --agent {agent} -p {prompt}`. When the
 * skill has NO agent selected, the token — and, if it stood alone, the flag
 * immediately before it (e.g. `--agent`) — is dropped so no dangling flag
 * swallows the next argument. Substituted WITHIN a token, never split. Unlike
 * `{prompt}` it is optional: a command need not contain it.
 */
export const HARNESS_AGENT_PLACEHOLDER = "{agent}";

/** The per-skill <select> value prefix identifying a custom-harness choice. */
export const CUSTOM_HARNESS_VALUE_PREFIX = "custom:";

/**
 * A user-defined harness. `command` is an argv template: `command[0]` is the
 * absolute binary, the rest are inert args, and at least one token contains
 * `{prompt}`. See the block comment above for the security contract.
 */
export interface CustomHarness {
  id: string;
  label: string;
  command: string[];
  /**
   * Optional argv to RECONNECT to a session this harness started (M20 Sessions
   * tab). `command[0]` is the absolute binary; the rest are inert args; NO
   * `{prompt}` (resume continues an existing session). When set, it is what the
   * Sessions-tab "Connect" runs for this harness — overriding the built-in
   * defaults (claude/codex/isaac) and the generic best-effort guess. Absent =
   * best-effort (`<binary> --continue`) with a terminal hint to configure this.
   */
  resumeCommand?: string[];
}

/** Strip ASCII control chars (incl. NUL / CR / LF) from an interpolated value. */
export function stripControlChars(s: string): string {
  // eslint-disable-next-line no-control-regex -- intentional: strip C0/C1 control chars (incl. NUL/CR/LF) so an interpolated value can't inject newlines/terminators into a spawned command
  return s.replace(/[\x00-\x1f\x7f]/g, "");
}

/**
 * Validate a custom-harness command array (no filesystem). Passes ONLY if it is
 * a non-empty array of non-empty strings whose FIRST element is an ABSOLUTE path
 * and where at least one element contains the `{prompt}` placeholder. Pure /
 * unit-testable. (Filesystem existence of the binary is checked separately,
 * fail-closed, at launch.)
 */
export function isValidCustomHarnessCommand(command: unknown): command is string[] {
  if (!Array.isArray(command) || command.length === 0) return false;
  const arr = command as unknown[];
  if (!arr.every((t) => typeof t === "string" && t.length > 0)) return false;
  const strs = arr as string[];
  return (
    nodePath.isAbsolute(strs[0]) &&
    strs.some((t) => t.includes(HARNESS_PROMPT_PLACEHOLDER))
  );
}

/**
 * Build the argv for a custom harness: substitute the (control-char-stripped)
 * prompt into EVERY `{prompt}` occurrence, within each token (never split), and
 * return the argv array. Returns null (FAIL CLOSED) if the command is invalid.
 * The binary (argv[0]) passes through verbatim (already validated absolute).
 * Pure / unit-testable.
 */
export function buildCustomHarnessArgv(opts: {
  command: string[];
  prompt: string;
  agent?: string;
}): string[] | null {
  if (!isValidCustomHarnessCommand(opts.command)) return null;
  const safePrompt = stripControlChars(opts.prompt);
  const agent =
    typeof opts.agent === "string" ? stripControlChars(opts.agent).trim() : "";

  // First resolve the OPTIONAL {agent} token(s). With an agent selected,
  // substitute it within the token (like {prompt}); with none, drop the token
  // AND — if the token was the standalone value of a preceding flag (e.g.
  // `--agent {agent}`) — drop that flag too, so nothing dangles. A token that
  // merely CONTAINS the placeholder (e.g. `--agent={agent}`) is dropped whole.
  const resolved: string[] = [];
  for (const tok of opts.command) {
    if (!tok.includes(HARNESS_AGENT_PLACEHOLDER)) {
      resolved.push(tok);
      continue;
    }
    if (agent) {
      resolved.push(tok.split(HARNESS_AGENT_PLACEHOLDER).join(agent));
    } else if (tok === HARNESS_AGENT_PLACEHOLDER) {
      const prev = resolved[resolved.length - 1];
      if (prev !== undefined && prev.startsWith("-")) resolved.pop();
    }
    // else (token contains but ≠ placeholder, no agent): drop the whole token.
  }

  // Then substitute {prompt} within each surviving token (unchanged behavior).
  return resolved.map((t) => t.split(HARNESS_PROMPT_PLACEHOLDER).join(safePrompt));
}

/** The per-skill stored value for a custom-harness selection. */
export function encodeCustomHarnessChoice(id: string): string {
  return `${CUSTOM_HARNESS_VALUE_PREFIX}${id}`;
}

/**
 * The print/headless flags used by the supported CLIs. In these modes the CLI
 * answers the single prompt and EXITS — correct for a headless (background)
 * launch, but wrong for a TERMINAL launch where the user wants to keep chatting.
 */
const HEADLESS_FLAGS = new Set(["-p", "--print"]);

/**
 * Transform a headless launch argv into an INTERACTIVE one for a terminal launch:
 * drop any print/headless flag (`-p` / `--print`) so the CLI opens an interactive
 * session SEEDED with the prompt (which stays as an inert positional/message)
 * instead of printing-and-exiting. `argv[0]` (the binary) and every other token —
 * including the prompt — pass through unchanged and un-split, so this adds NO new
 * shell/tokenization surface. If the argv contains no headless flag it is returned
 * as-is. Pure / unit-testable.
 */
export function toInteractiveArgv(argv: string[]): string[] {
  if (!Array.isArray(argv) || argv.length === 0) return argv;
  // Keep argv[0] (binary) always; filter headless flags from the rest.
  return [argv[0], ...argv.slice(1).filter((t) => !HEADLESS_FLAGS.has(t))];
}

/**
 * Split a single-line custom-harness command into an argv array. This is a PLAIN
 * whitespace split — NOT a shell-words tokenizer: there is no quote handling, no
 * backslash escapes, no metacharacter interpretation (that whole defect class is
 * avoided by design; see `[[skillsplugin_learnings]]`). Consequently a token
 * cannot itself contain a space — except the `{prompt}` placeholder, which is
 * substituted (as ONE element) with the full prompt at launch. `command[0]` is
 * the binary. Empty tokens are dropped. Pure / unit-testable.
 */
export function parseHarnessCommandLine(line: string): string[] {
  if (typeof line !== "string") return [];
  return line.trim().split(/\s+/).filter((t) => t.length > 0);
}

/** A harness omnigent has configured (parsed from `omnigent config list`). */
export interface ConfiguredHarness {
  /** Display name exactly as omnigent groups it, e.g. "Claude", "Codex". */
  name: string;
  /** True when at least one credential is configured (not "(none configured)"). */
  configured: boolean;
}

/**
 * Parse the "Credentials (by harness)" section of `omnigent config list` output
 * into the harnesses omnigent knows, each flagged configured / not. omnigent has
 * no machine-readable form, so we parse the indented text: the section header is
 * at column 0; each harness is a 2-space-indented group header; its credential
 * lines are indented deeper. A group is `configured:false` only when its sole
 * child is the literal "(none configured)". A dedent (column-0 line) ends the
 * section. Pure / unit-testable; returns [] on anything unexpected.
 */
export function parseConfiguredHarnesses(stdout: string): ConfiguredHarness[] {
  if (typeof stdout !== "string") return [];
  const out: ConfiguredHarness[] = [];
  let inSection = false;
  let current: ConfiguredHarness | null = null;
  for (const line of stdout.split(/\r?\n/)) {
    if (/^Credentials \(by harness\)/.test(line)) {
      inSection = true;
      continue;
    }
    if (!inSection) continue;
    if (line.trim() === "") continue; // tolerate blank lines within the section
    if (/^\S/.test(line)) break; // a column-0 line ends the section
    if (/^ {3,}\S/.test(line)) {
      // A credential/detail line for the current group.
      if (current && line.trim() !== "(none configured)") current.configured = true;
      continue;
    }
    const header = /^ {2}(\S.*?)\s*$/.exec(line); // exactly-2-space-indented group
    if (header) {
      current = { name: header[1].trim(), configured: false };
      out.push(current);
    }
  }
  return out;
}

/** A parsed per-skill harness selection (still unvalidated against existence). */
export type HarnessChoice =
  | { kind: "none" }
  | { kind: "omnigent"; name: OmnigentHarness }
  | { kind: "custom"; id: string };

/**
 * Parse a stored/selected per-skill harness value into a choice: a hardcoded
 * omnigent-harness name, a `custom:<id>` reference, or none (Default / anything
 * unrecognized). Pure / unit-testable.
 */
export function parseHarnessValue(value: unknown): HarnessChoice {
  if (isAllowedHarness(value)) return { kind: "omnigent", name: value };
  if (
    typeof value === "string" &&
    value.startsWith(CUSTOM_HARNESS_VALUE_PREFIX)
  ) {
    const id = value.slice(CUSTOM_HARNESS_VALUE_PREFIX.length);
    if (id.length > 0) return { kind: "custom", id };
  }
  return { kind: "none" };
}

/** The launch-resolved per-skill harness, with the custom command attached. */
export type ResolvedSkillHarness =
  | { kind: "none" }
  | { kind: "omnigent"; name: OmnigentHarness }
  | { kind: "custom"; harness: CustomHarness };

/**
 * Resolve a stored per-skill harness value, FAILING CLOSED. An omnigent harness
 * name resolves to `{omnigent}`; a `custom:<id>` resolves to `{custom}` ONLY if
 * that id is in `customHarnesses` AND its command still passes
 * `isValidCustomHarnessCommand`; everything else → `{none}`. Pure /
 * unit-testable (existence of the binary is checked at spawn time).
 */
export function resolveSkillHarness(
  stored: unknown,
  customHarnesses: CustomHarness[] | undefined | null,
): ResolvedSkillHarness {
  const choice = parseHarnessValue(stored);
  if (choice.kind === "omnigent") return { kind: "omnigent", name: choice.name };
  if (choice.kind === "custom") {
    const h = (customHarnesses ?? []).find((c) => c && c.id === choice.id);
    if (h && isValidCustomHarnessCommand(h.command)) {
      return { kind: "custom", harness: h };
    }
  }
  return { kind: "none" };
}

/**
 * The copyable CLI string for a custom harness (clipboard only). Each token is
 * POSIX single-quote wrapped so it pastes as one safe shell argument; the
 * `{prompt}` placeholder is replaced with the (control-char-stripped, quoted)
 * prompt. Pure / unit-testable.
 */
export function buildCustomHarnessCliInvocation(opts: {
  command: string[];
  prompt: string;
  agent?: string;
}): string {
  const argv = buildCustomHarnessArgv(opts);
  if (!argv) return "";
  return argv.map((t) => shellSingleQuote(t)).join(" ");
}

/** The vault-relative directory custom agent YAML configs are scanned from. */
export const AGENT_CONFIG_SUBDIR = ".omnigent/agent-configs";

// =====================================================================
// Claude subagents (M17) — `.claude/agents/*.md` files (Claude Code's own agent
// format: frontmatter name/description/tools/model + a system-prompt body).
// These are ORTHOGONAL to omnigent YAML agents: they apply only when the harness
// is a claude-based CUSTOM harness, and are passed via the `{agent}` placeholder
// (see HARNESS_AGENT_PLACEHOLDER). Discovery is a plain filesystem scan; only the
// agent NAME ever reaches argv (control-char-stripped, as one inert token).
// =====================================================================

/** The vault-relative directory Claude subagents are scanned from. */
export const CLAUDE_AGENTS_SUBDIR = ".claude/agents";

/** A discovered Claude subagent (display metadata; only `name` reaches argv). */
export interface ClaudeAgent {
  /** The subagent name (frontmatter `name:`, else the filename stem). Passed to
   *  `--agent` via the `{agent}` token — the ONLY field that reaches argv. */
  name: string;
  /** Absolute path to the `.md` file (display / open only; never argv). */
  path: string;
  /** Optional frontmatter `description:` (tooltip; never argv). */
  description?: string;
  /** "project" (vault `.claude/agents`) or "global" (`~/.claude/agents`). */
  source: "project" | "global";
}

/**
 * Read a Claude subagent's frontmatter `name:` and `description:` (top-level
 * scalars inside the leading `---` fence). Minimal + dependency-free; mirrors
 * `parseAgentConfigYaml` but scoped to a fenced frontmatter block. Pure /
 * unit-testable. Returns nulls when absent.
 */
export function parseClaudeAgentFrontmatter(text: string): {
  name: string | null;
  description: string | null;
} {
  const out: { name: string | null; description: string | null } = {
    name: null,
    description: null,
  };
  if (typeof text !== "string") return out;
  const lines = text.split(/\r?\n/);
  if (lines[0]?.trim() !== "---") return out;
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === "---") break; // end of frontmatter
    if (/^[ \t]/.test(line)) continue; // nested — top-level keys only
    const m = /^([A-Za-z0-9_-]+):(.*)$/.exec(line);
    if (!m) continue;
    const key = m[1];
    if (key !== "name" && key !== "description") continue;
    if (out[key] !== null) continue; // first occurrence wins
    let val = m[2].trim();
    if (
      val.length >= 2 &&
      ((val[0] === '"' && val[val.length - 1] === '"') ||
        (val[0] === "'" && val[val.length - 1] === "'"))
    ) {
      val = val.slice(1, -1);
    }
    out[key] = val.length ? val : null;
  }
  return out;
}

/**
 * The per-skill stored choice (a discriminated union). Persisted verbatim in
 * data.json under `skillAgent[skillId]`. Absent key = Default.
 */
export type SkillAgent =
  | { kind: "default" }
  | { kind: "builtin"; name: string }
  | { kind: "custom"; path: string };

/**
 * The resolved, validated launch form consumed by `buildOmnigentArgv`. Only
 * ever produced by `resolveAgentLaunch`, which fails closed.
 */
export type ResolvedAgent =
  | { mode: "default" }
  | { mode: "builtin"; name: BuiltinAgentName }
  | { mode: "custom"; path: string };

/** A discovered custom agent (display metadata + the only argv-bound field, path). */
export interface CustomAgent {
  /**
   * Absolute launch path — the ONLY field that can reach argv. Either a loose
   * YAML config FILE or a BUNDLE directory (`omnigent run <dir>`); never the
   * `config.yaml` inside a bundle.
   */
  path: string;
  /** Display label (top-level `name:`, else the filename stem). Never argv. */
  name: string;
  /** Optional tooltip (top-level `description:`). Never argv. */
  description?: string;
}

/** Membership test for the hardcoded built-in agent allowlist. */
export function isAllowedBuiltinAgent(name: unknown): name is BuiltinAgentName {
  return (
    typeof name === "string" &&
    (BUILTIN_AGENTS as readonly string[]).includes(name)
  );
}

/**
 * The LEXICAL half of the custom-agent path gate (no filesystem). A path passes
 * only if: it is a non-empty string; the RAW string contains NO `..` path
 * segment (rejected up front, before any resolve — so traversal *syntax* that
 * would lexically collapse back into the dir, e.g. `<scanDir>/sub/../evil.yaml`
 * or `<scanDir>/../agent-configs/evil.yaml`, is refused outright); it is an
 * ABSOLUTE path (so it can never be read as a flag — leading-dash safe by
 * construction); it carries either a `.yaml`/`.yml` extension (a loose file) OR
 * NO file extension at all (a candidate BUNDLE directory `<name>/config.yaml`,
 * whose directory path has no extension) — any OTHER extension (e.g. `.txt`) is
 * rejected here; and it is a direct child of `scanDir`. Whether the path is in
 * fact a loose `.yaml`/`.yml` file or a bundle directory containing
 * `config.yaml` is decided by the filesystem-aware `safeCustomAgentRealPath`;
 * that gate also performs existence + a symlink-aware (realpath) containment
 * check. Pure / unit-testable.
 */
export function isValidCustomAgentPath(p: unknown, scanDir: string): boolean {
  if (typeof p !== "string" || p.length === 0) return false;
  if (typeof scanDir !== "string" || scanDir.length === 0) return false;
  // 1. Reject ANY `..` segment in the RAW string, before resolve() can collapse
  // it. `resolve()` flattens `..` lexically, so a syntax like `sub/../evil.yaml`
  // would otherwise survive — the contract forbids traversal syntax entirely.
  if (rawPathHasDotDot(p)) return false;
  if (!nodePath.isAbsolute(p)) return false;
  // With `..` already rejected, resolve() only normalizes separators / `.`
  // segments here.
  const resolved = nodePath.resolve(p);
  // A loose YAML file (`.yaml`/`.yml`) OR an extension-less path that may be a
  // bundle directory. Any other extension is refused outright. The file-vs-dir
  // distinction (and the `config.yaml`-inside requirement for a bundle) is the
  // job of the fs-aware gate.
  const ext = nodePath.extname(resolved).toLowerCase();
  if (ext !== "" && ext !== ".yaml" && ext !== ".yml") return false;
  // Direct child of the scan dir only (lexical).
  return nodePath.dirname(resolved) === nodePath.resolve(scanDir);
}

/** True if the raw path string contains a `..` segment (any separator). */
function rawPathHasDotDot(p: string): boolean {
  return p.split(/[\\/]+/).some((seg) => seg === "..");
}

/** Basename of the canonical config file inside an omnigent BUNDLE directory. */
export const BUNDLE_CONFIG_NAME = "config.yaml";

/**
 * The FULL custom-agent path gate, fail-closed and defense-in-depth. Returns the
 * real (symlink-resolved) absolute path ONLY if every check holds, else null
 * (caller falls back to Default); NEVER throws. The path may resolve to EITHER a
 * loose YAML file or an omnigent BUNDLE directory. Checks, in order:
 *   1–3. lexical gate (`isValidCustomAgentPath`: no `..` syntax, absolute,
 *        `.yaml`/`.yml` OR extension-less, lexical direct-child of scanDir);
 *   4.   the path exists (injected `exists`) and is EITHER
 *          (a) a regular FILE ending `.yaml`/`.yml`, OR
 *          (b) a DIRECTORY that DIRECTLY CONTAINS a regular file `config.yaml`
 *              (the canonical bundle layout — `omnigent run <dir>`). The
 *              `config.yaml` must be a directly-contained REGULAR file — checked
 *              with a NON-symlink-following stat (`isRegularFileNoFollow`), so a
 *              symlinked `config.yaml` (which would let the bundle consume a
 *              config from outside itself) or a `config.yaml` directory is
 *              rejected;
 *        anything else (extension-less plain file, dir without `config.yaml`,
 *        special file) → null;
 *   5.   the symlink gap is closed — `realpath` of the candidate AND of scanDir
 *        are computed, and the candidate's real dirname must equal the real
 *        scanDir (a real, direct child of the real scan dir).
 * The emitted real path is the validated FILE (loose) or DIRECTORY (bundle) —
 * never the `config.yaml` inside a bundle (`omnigent run <dir>` is canonical).
 * A broken symlink / ENOENT / any throw from the fs ops resolves to null. fs
 * ops are injected so this stays unit-testable; the real `fs` is the default.
 */
export function safeCustomAgentRealPath(
  rawPath: unknown,
  scanDir: string,
  fsOps: {
    exists?: (p: string) => boolean;
    realpath: (p: string) => string;
    isFile: (p: string) => boolean;
    isDirectory?: (p: string) => boolean;
    isRegularFileNoFollow?: (p: string) => boolean;
  },
): string | null {
  if (!isValidCustomAgentPath(rawPath, scanDir)) return null;
  const p = rawPath as string;
  try {
    if (fsOps.exists && !fsOps.exists(p)) return null;
    // (a) loose YAML file, OR (b) bundle directory with a regular config.yaml.
    let kindOk = false;
    if (fsOps.isFile(p)) {
      kindOk = /\.ya?ml$/i.test(p);
    } else if (fsOps.isDirectory && fsOps.isDirectory(p)) {
      // The bundle's config.yaml must be a directly-contained REGULAR file:
      // checked WITHOUT following the final symlink, so a symlinked config.yaml
      // (escaping the bundle) or a config.yaml directory is rejected.
      kindOk =
        !!fsOps.isRegularFileNoFollow &&
        fsOps.isRegularFileNoFollow(nodePath.join(p, BUNDLE_CONFIG_NAME));
    }
    if (!kindOk) return null;
    const real = fsOps.realpath(p);
    const realDir = fsOps.realpath(scanDir);
    // Real, direct child of the real scan dir — closes the symlink gap that the
    // lexical check alone (which never follows links) would miss. Applies
    // equally to a loose file and to a bundle directory.
    if (nodePath.dirname(real) !== realDir) return null;
    return real;
  } catch {
    return null; // ENOENT / broken symlink / any fs throw → fail closed.
  }
}

/**
 * Resolve a per-skill stored agent choice to the validated launch form, FAILING
 * CLOSED to the Default agent. The only value that can reach argv as a flag-able
 * token is a built-in name that is in the hardcoded allowlist; the only value
 * that can reach argv as a positional is a custom path that passes
 * `isValidCustomAgentPath` AND still exists. Anything else — unknown kind,
 * missing value, bad built-in name, custom path outside the scan dir / wrong
 * extension / non-existent — resolves to `{ mode: 'default' }`. `exists` is
 * injected so this stays pure / unit-testable. NEVER consults a display label.
 */
export function resolveAgentLaunch(
  stored: SkillAgent | undefined | null,
  opts: {
    scanDir: string;
    exists: (p: string) => boolean;
    realpath?: (p: string) => string;
    isFile?: (p: string) => boolean;
    isDirectory?: (p: string) => boolean;
    isRegularFileNoFollow?: (p: string) => boolean;
  },
): ResolvedAgent {
  if (!stored || typeof stored !== "object") return { mode: "default" };
  if (stored.kind === "builtin") {
    return isAllowedBuiltinAgent(stored.name)
      ? { mode: "builtin", name: stored.name }
      : { mode: "default" };
  }
  if (stored.kind === "custom") {
    // Fail-closed, symlink-aware containment check. fs ops default to the real
    // `fs` (so the unchanged main.ts call site is correct at runtime) and are
    // injectable for tests. The emitted path is the real (resolved) absolute
    // path — the single inert positional after `run`.
    const real = safeCustomAgentRealPath(stored.path, opts.scanDir, {
      exists: opts.exists,
      realpath: opts.realpath ?? ((p) => fs.realpathSync(p)),
      isFile: opts.isFile ?? ((p) => fs.statSync(p).isFile()),
      isDirectory: opts.isDirectory ?? ((p) => fs.statSync(p).isDirectory()),
      // lstat does NOT follow the final symlink: a symlinked config.yaml yields
      // isSymbolicLink (isFile()===false) and a directory yields isFile()===false.
      isRegularFileNoFollow:
        opts.isRegularFileNoFollow ?? ((p) => fs.lstatSync(p).isFile()),
    });
    return real ? { mode: "custom", path: real } : { mode: "default" };
  }
  // 'default' or any unrecognized kind.
  return { mode: "default" };
}

/**
 * Minimal, safe top-level scalar reader for a custom agent YAML config. Reads
 * ONLY the first top-level `name:` and `description:` (column-0 keys); nested or
 * indented keys are ignored. Surrounding quotes are stripped and a trailing
 * inline `#` comment on an unquoted scalar is dropped. This intentionally does
 * NOT pull a full YAML dependency — it never executes anything and only ever
 * yields two display strings (which never reach argv). Pure / unit-testable.
 */
export function parseAgentConfigYaml(text: string): {
  name: string | null;
  description: string | null;
} {
  const out: { name: string | null; description: string | null } = {
    name: null,
    description: null,
  };
  if (typeof text !== "string") return out;
  for (const line of text.split(/\r?\n/)) {
    // Top-level keys only — any leading whitespace means it is nested.
    if (/^[ \t]/.test(line)) continue;
    const m = /^([A-Za-z0-9_-]+):(.*)$/.exec(line);
    if (!m) continue;
    const key = m[1];
    if (key !== "name" && key !== "description") continue;
    if (out[key] !== null) continue; // first occurrence wins
    const val = unquoteScalar(m[2].trim());
    out[key] = val.length ? val : null;
  }
  return out;
}

/** Strip matching surrounding quotes, else drop a trailing ` #` inline comment. */
function unquoteScalar(s: string): string {
  if (
    s.length >= 2 &&
    ((s[0] === '"' && s[s.length - 1] === '"') ||
      (s[0] === "'" && s[s.length - 1] === "'"))
  ) {
    return s.slice(1, -1);
  }
  const hash = s.indexOf(" #");
  return hash === -1 ? s : s.slice(0, hash).trim();
}

/**
 * Discover the custom agents in `dir` (the absolute
 * `<vaultBase>/.omnigent/agent-configs`), considering ONLY direct children of
 * two kinds:
 *   1. LOOSE FILE  — a child ending `.yaml`/`.yml`; the launch path is the FILE,
 *      its display name is read from that file's top-level `name:` (else the
 *      filename stem).
 *   2. BUNDLE DIR  — a child directory that directly contains a regular
 *      `config.yaml`; the launch path is the DIRECTORY (`omnigent run <dir>` is
 *      canonical — never the `config.yaml` inside it), its display name is read
 *      from `<dir>/config.yaml`'s top-level `name:` (else the directory name).
 * Bundle detection requires the injected `isDirectory` callback; without it only
 * loose files are enumerated (the pre-bundle behavior). Subdirectories with no
 * `config.yaml` and non-yaml files are ignored. Each yields an optional tooltip
 * (`description:`). If `dir` is null or does not exist (readdir throws), yields
 * ZERO agents — never an error. fs callbacks are injected so this stays pure /
 * unit-testable. Results are sorted by entry name for stable ordering.
 */
export function discoverCustomAgents(opts: {
  dir: string | null;
  readdir: (dir: string) => string[];
  readFile: (path: string) => string;
  isFile?: (path: string) => boolean;
  isDirectory?: (path: string) => boolean;
}): CustomAgent[] {
  if (!opts.dir) return [];
  let entries: string[];
  try {
    entries = opts.readdir(opts.dir);
  } catch {
    return []; // missing dir → zero agents (no error)
  }
  const probe = (p: string, fn?: (q: string) => boolean): boolean => {
    if (!fn) return false;
    try {
      return fn(p);
    } catch {
      return false;
    }
  };
  const out: CustomAgent[] = [];
  for (const entry of [...entries].sort()) {
    const abs = nodePath.join(opts.dir, entry);
    // The path to launch (file OR dir) and the YAML to read display metadata
    // from, plus the fallback display name. Resolved per kind below.
    let launchPath: string | null = null;
    let readPath: string | null = null;
    let fallbackName = entry;

    if (/\.ya?ml$/i.test(entry)) {
      // LOOSE FILE: an isFile gate (when provided) must confirm it is a file.
      const isFileOk = opts.isFile ? probe(abs, opts.isFile) : true;
      if (isFileOk) {
        launchPath = abs;
        readPath = abs;
        fallbackName = entry.replace(/\.ya?ml$/i, "");
      }
    }
    if (launchPath === null && probe(abs, opts.isDirectory)) {
      // BUNDLE DIR: must directly contain a regular `config.yaml`.
      const config = nodePath.join(abs, BUNDLE_CONFIG_NAME);
      let hasConfig: boolean;
      if (opts.isFile) {
        hasConfig = probe(config, opts.isFile);
      } else {
        // No isFile probe → fall back to attempting the read.
        try {
          opts.readFile(config);
          hasConfig = true;
        } catch {
          hasConfig = false;
        }
      }
      if (hasConfig) {
        launchPath = abs; // the DIRECTORY, not the config.yaml inside it
        readPath = config;
        fallbackName = entry; // directory name
      }
    }
    if (launchPath === null || readPath === null) continue;

    let text: string;
    try {
      text = opts.readFile(readPath);
    } catch {
      continue;
    }
    const meta = parseAgentConfigYaml(text);
    const name = meta.name && meta.name.trim() ? meta.name.trim() : fallbackName;
    out.push({
      path: launchPath,
      name,
      ...(meta.description ? { description: meta.description } : {}),
    });
  }
  return out;
}

// --- UI encode/decode for the per-skill <select> value -----------------
// The dropdown is a flat <select>; its option values are strings. These map the
// discriminated `SkillAgent` to/from that flat string. Decoding is UNVALIDATED
// (the builtin name / custom path are taken verbatim) — validation happens at
// store time and again, authoritatively, at launch (`resolveAgentLaunch`).

export const AGENT_DEFAULT_VALUE = "default";

/** Encode a stored choice to its <select> option value. */
export function encodeAgentChoice(agent: SkillAgent | undefined | null): string {
  if (!agent || typeof agent !== "object") return AGENT_DEFAULT_VALUE;
  if (agent.kind === "builtin") return `builtin:${agent.name}`;
  if (agent.kind === "custom") return `custom:${agent.path}`;
  return AGENT_DEFAULT_VALUE;
}

/** Decode a <select> option value back to a (still-unvalidated) choice. */
export function decodeAgentChoice(value: string): SkillAgent {
  if (typeof value === "string") {
    if (value.startsWith("builtin:")) {
      return { kind: "builtin", name: value.slice("builtin:".length) };
    }
    if (value.startsWith("custom:")) {
      return { kind: "custom", path: value.slice("custom:".length) };
    }
  }
  return { kind: "default" };
}

/**
 * Ordered candidate absolute paths to probe for the omnigent binary:
 * user override first (if set), then the standard install locations.
 * `homedir` is injected so this stays pure/testable.
 */
export function omnigentCandidatePaths(
  override: string | undefined,
  homedir: string,
  platform: NodeJS.Platform = process.platform,
): string[] {
  const candidates: string[] = [];
  const ov = override?.trim();
  if (ov) candidates.push(ov);
  if (platform === "win32") {
    // Windows: uv-installed tools live under %USERPROFILE%\.local\bin; the binary
    // carries an executable extension. (Auto-detect is best-effort on Windows —
    // users typically set an explicit path in Settings.)
    for (const ext of [".exe", ".cmd", ".bat"]) {
      candidates.push(nodePath.join(homedir, ".local", "bin", OMNIGENT_BIN_NAME + ext));
    }
  } else {
    candidates.push(`${homedir}/.local/bin/${OMNIGENT_BIN_NAME}`);
    candidates.push(`/usr/local/bin/${OMNIGENT_BIN_NAME}`);
    candidates.push(`/opt/homebrew/bin/${OMNIGENT_BIN_NAME}`);
  }
  return candidates;
}

/**
 * The allowlist control: a binary path is permitted ONLY if it is an absolute
 * path whose basename is exactly `omnigent`. Validates the path STRING (not the
 * realpath) so legitimate symlinked installs (e.g. /usr/local/bin/omnigent ->
 * .../omnigent-real) are not falsely rejected.
 */
export function isAllowedOmnigentPath(p: string): boolean {
  if (!p) return false;
  if (!nodePath.isAbsolute(p)) return false;
  // Accept the bare binary name, or a Windows executable form
  // (omnigent.exe / .cmd / .bat) so the allowlist works cross-platform.
  const base = nodePath.basename(p).toLowerCase();
  return (
    base === OMNIGENT_BIN_NAME ||
    base === `${OMNIGENT_BIN_NAME}.exe` ||
    base === `${OMNIGENT_BIN_NAME}.cmd` ||
    base === `${OMNIGENT_BIN_NAME}.bat`
  );
}

export type BinaryResolution =
  | { status: "ok"; path: string }
  | { status: "invalid-override" }
  | { status: "not-found" };

/**
 * Resolve the omnigent binary, FAILING CLOSED. If an override is set it must
 * pass the allowlist (`isAllowedOmnigentPath`) — a set-but-invalid override
 * yields `invalid-override` and is NEVER masked by falling back to the
 * defaults. When the override is blank, the (already allowlisted, absolute)
 * default candidates are probed in order. `exists` is injected (fs.existsSync
 * at runtime) so resolution is testable without the filesystem.
 */
export function resolveOmnigentBinary(opts: {
  override?: string;
  homedir: string;
  exists: (path: string) => boolean;
}): BinaryResolution {
  const override = opts.override?.trim();
  if (override) {
    if (!isAllowedOmnigentPath(override)) return { status: "invalid-override" };
    // Respect the explicit override: do not fall through to defaults.
    return opts.exists(override)
      ? { status: "ok", path: override }
      : { status: "not-found" };
  }
  for (const candidate of omnigentCandidatePaths(undefined, opts.homedir)) {
    if (opts.exists(candidate)) return { status: "ok", path: candidate };
  }
  return { status: "not-found" };
}

/**
 * Augment a PATH string with extra entries (GUI apps inherit a thin launchd
 * PATH; the spawned binary execs sub-tools and needs these). Preserves order
 * and de-dupes — existing entries are not re-appended.
 */
export function augmentPath(
  currentPath: string | undefined,
  extras: string[],
): string {
  const sep = ":";
  const seen = new Set<string>();
  const out: string[] = [];
  const push = (entry: string) => {
    if (entry === "" || seen.has(entry)) return;
    seen.add(entry);
    out.push(entry);
  };
  for (const p of (currentPath ?? "").split(sep)) push(p);
  for (const e of extras) push(e);
  return out.join(sep);
}

/** A single resolved right-click (file-menu) entry: title + what to launch. */
export interface RightClickMenuItem {
  /** Menu label, e.g. `Run "transcribe-meeting" here`. */
  title: string;
  /** The skill id (= absolute path) to launch. */
  skillId: string;
  /** The clicked file/folder absolute path, passed as the launch context. */
  contextPath: string;
}

/**
 * Pure construction of the file-menu items for the M3 right-click surface.
 * GATED by `isEnabled(id)` — only skills with `rightClickEnabled` produce an
 * item, so a disabled skill never appears in the menu. The clicked file's
 * absolute path is carried through unchanged (the launcher embeds it as inert
 * text inside the single `-p` prompt). Kept side-effect-free so it is unit
 * testable independent of Obsidian's `Menu`.
 */
export function buildRightClickMenuItems(
  skills: { id: string; name: string }[],
  isEnabled: (id: string) => boolean,
  contextAbsPath: string,
): RightClickMenuItem[] {
  const items: RightClickMenuItem[] = [];
  for (const s of skills) {
    if (!isEnabled(s.id)) continue;
    items.push({
      title: `Run "${s.name}" here`,
      skillId: s.id,
      contextPath: contextAbsPath,
    });
  }
  return items;
}


### Detection Engine

import * as fs from "fs";
import * as nodePath from "path";
import {
  App,
  FileSystemAdapter,
  Platform,
  TFile,
  normalizePath,
} from "obsidian";
import {
  coerceFrontmatterTags,
  fileBaseName,
  firstHeading,
  inferSourceLabel,
  isMarkdown,
  isSkillCandidate,
  isSkillMd,
  parentFolderName,
  parseFrontmatter,
  resolveSkillTags,
} from "./parse";
import { DetectionMethod, ScanRoot, Skill, SkillLayerSettings } from "./types";

// Defensive caps so a misconfigured root (e.g. `/`) can't hang the walk.
const MAX_DEPTH = 12;
const IGNORED_DIRS = new Set([
  "node_modules",
  ".git",
  ".trash",
  ".DS_Store",
]);

interface SkillFields {
  name: string;
  description: string;
}

/**
 * Apply the uniform "what counts as a skill" rules (PRD §3) to one file.
 * Returns the resolved name/description, or null if the file is not a skill.
 */
function evaluateSkill(
  relOrAbsPath: string,
  fm: { name?: string; description?: string },
  getFirstHeading: () => string | null,
): SkillFields | null {
  if (isSkillMd(relOrAbsPath)) {
    // Primary rule: SKILL.md MUST have frontmatter name + description.
    if (fm.name && fm.description) {
      return { name: fm.name, description: fm.description };
    }
    return null;
  }

  // Fallback rule: any markdown directly under a folder named `skills/`.
  if (isMarkdown(relOrAbsPath) && parentFolderName(relOrAbsPath) === "skills") {
    const name = fm.name || fileBaseName(relOrAbsPath);
    const description =
      fm.description || getFirstHeading() || "(no description)";
    return { name, description };
  }

  return null;
}

export class Detector {
  constructor(
    private app: App,
    private getSettings: () => SkillLayerSettings,
  ) {}

  /** True when external (absolute-path) roots can be scanned safely. */
  canScanExternal(): boolean {
    return (
      Platform.isDesktopApp && this.app.vault.adapter instanceof FileSystemAdapter
    );
  }

  /** Absolute path to the vault root, or null when unavailable. */
  vaultBasePath(): string | null {
    const adapter = this.app.vault.adapter;
    if (adapter instanceof FileSystemAdapter) return adapter.getBasePath();
    return null;
  }

  /** Run all enabled roots, dedupe by absolute path. */
  async scan(): Promise<Skill[]> {
    const settings = this.getSettings();
    const byPath = new Map<string, Skill>();

    for (const root of settings.scanRoots) {
      if (!root.enabled) continue;
      let found: Skill[] = [];
      try {
        if (root.kind === "vault") {
          found = await this.scanVaultRoot(root);
        } else if (root.kind === "adapter") {
          found = await this.scanAdapterRoot(root);
        } else if (root.kind === "external") {
          found = await this.scanExternalRoot(root);
        }
      } catch (err) {
        console.error(`[skill-layer] scan failed for root "${root.path}":`, err);
      }
      // Dedupe by absolute path — first writer wins (root order is the priority).
      for (const skill of found) {
        if (!byPath.has(skill.id)) byPath.set(skill.id, skill);
      }
    }

    return Array.from(byPath.values()).sort((a, b) =>
      a.name.localeCompare(b.name),
    );
  }

  // --- Path 1: Vault API + metadataCache (non-dot folders) ---------------
  private async scanVaultRoot(root: ScanRoot): Promise<Skill[]> {
    const base = this.vaultBasePath();
    const prefix = normalizePath(root.path).replace(/^\/+|\/+$/g, "");
    const files = this.app.vault.getMarkdownFiles();
    const skills: Skill[] = [];

    for (const file of files) {
      if (prefix && !(file.path === prefix || file.path.startsWith(prefix + "/"))) {
        continue;
      }
      // Candidate gate FIRST — only SKILL.md files or markdown directly under a
      // `skills/` folder can ever be skills. Skip everything else with NO read,
      // so ordinary vault notes never trigger a cachedRead/parse.
      if (!isSkillCandidate(file.path)) continue;

      // Read fresh file content for candidates and parse name/description/tags
      // from it, so EXTERNAL / in-editor edits are reflected immediately. The
      // metadataCache can lag a `modify` event (it re-parses asynchronously),
      // which would otherwise serve stale tags. The candidate gate keeps this
      // cheap, and `cachedRead` is itself cached + invalidated on change. The
      // metadataCache is only a fallback if the read fails.
      let name: string | undefined;
      let description: string | undefined;
      let fmTags: string[] = [];
      let getFirstHeading: () => string | null = () => null;
      try {
        const content = await this.app.vault.cachedRead(file);
        const fm = parseFrontmatter(content);
        name = fm.name;
        description = fm.description;
        fmTags = fm.tags ?? [];
        getFirstHeading = () => firstHeading(content);
      } catch (err) {
        console.error(`[skill-layer] cachedRead failed for ${file.path}:`, err);
        const cache = this.app.metadataCache.getFileCache(file);
        name = cache?.frontmatter?.name as string | undefined;
        description = cache?.frontmatter?.description as string | undefined;
        fmTags = coerceFrontmatterTags(cache?.frontmatter?.tags);
        getFirstHeading = () => cache?.headings?.[0]?.heading ?? null;
      }

      const fields = evaluateSkill(file.path, { name, description }, getFirstHeading);
      if (!fields) continue;

      const absPath = base ? normalizePath(`${base}/${file.path}`) : file.path;
      skills.push(
        this.makeSkill(fields, absPath, file.path, root.path, "vault", fmTags, file.path),
      );
    }
    return skills;
  }

  // --- Path 2: dot-folders (.claude/, .codex/, …) ------------------------
  private async scanAdapterRoot(root: ScanRoot): Promise<Skill[]> {
    const base = this.vaultBasePath();
    // On desktop, walk dot-folders with Node `fs`. Obsidian's `adapter.list()`
    // does NOT surface hidden dot-folders (e.g. `.claude/`) on Windows the way it
    // does on macOS (Windows marks dot-prefixed folders hidden), so relying on it
    // silently drops those skills. `fs` lists them on every OS. The adapter path
    // remains as a fallback for environments without filesystem access.
    if (base && this.canScanExternal()) {
      return this.scanAdapterRootViaFs(root, base);
    }
    return this.scanAdapterRootViaAdapter(root, base);
  }

  /** Desktop dot-folder walk via Node `fs` (cross-platform, sees hidden dirs). */
  private async scanAdapterRootViaFs(
    root: ScanRoot,
    base: string,
  ): Promise<Skill[]> {
    const skills: Skill[] = [];
    const absStart = nodePath.join(base, root.path);
    let rootReal: string;
    try {
      rootReal = await fs.promises.realpath(absStart);
    } catch {
      return []; // root folder absent — nothing to scan
    }
    const files: string[] = [];
    await this.walkFs(absStart, rootReal, 0, files, new Set<string>());
    for (const abs of files) {
      if (!isMarkdown(abs)) continue;
      let content: string;
      try {
        content = await fs.promises.readFile(abs, "utf8");
      } catch (err) {
        console.error(`[skill-layer] fs.readFile failed for ${abs}:`, err);
        continue;
      }
      // Vault-relative, forward-slash path (matches adapter ids for dedupe).
      const rel = nodePath.relative(base, abs).split(nodePath.sep).join("/");
      const fm = parseFrontmatter(content);
      const fields = evaluateSkill(rel, fm, () => firstHeading(content));
      if (!fields) continue;
      skills.push(
        this.makeSkill(fields, normalizePath(abs), rel, root.path, "adapter", fm.tags ?? [], rel),
      );
    }
    return skills;
  }

  /** Fallback dot-folder walk via Obsidian's adapter (non-desktop). */
  private async scanAdapterRootViaAdapter(
    root: ScanRoot,
    base: string | null,
  ): Promise<Skill[]> {
    const start = normalizePath(root.path);
    const skills: Skill[] = [];
    const adapter = this.app.vault.adapter;

    const files: string[] = [];
    await this.walkAdapter(start, 0, files);

    for (const rel of files) {
      if (!isMarkdown(rel)) continue;
      let content: string;
      try {
        content = await adapter.read(rel);
      } catch (err) {
        console.error(`[skill-layer] adapter.read failed for ${rel}:`, err);
        continue;
      }
      const fm = parseFrontmatter(content);
      const fields = evaluateSkill(rel, fm, () => firstHeading(content));
      if (!fields) continue;

      // Normalize in both branches so adapter ids match the Vault-API path's
      // normalization and dedupe stays consistent (Windows / same root twice).
      const absPath = normalizePath(base ? `${base}/${rel}` : rel);
      skills.push(
        this.makeSkill(fields, absPath, rel, root.path, "adapter", fm.tags ?? [], rel),
      );
    }
    return skills;
  }

  /** `adapter.list()` is non-recursive — descend `folders` ourselves. */
  private async walkAdapter(
    dir: string,
    depth: number,
    out: string[],
  ): Promise<void> {
    if (depth > MAX_DEPTH) return;
    const adapter = this.app.vault.adapter;
    let listed;
    try {
      listed = await adapter.list(dir);
    } catch {
      return; // missing/unreadable folder — skip quietly
    }
    for (const f of listed.files) out.push(f);
    for (const sub of listed.folders) {
      const name = sub.replace(/\/+$/, "").split("/").pop() ?? "";
      if (IGNORED_DIRS.has(name) || name === this.app.vault.configDir) continue;
      await this.walkAdapter(sub, depth + 1, out);
    }
  }

  // --- Path 3: external absolute roots via Node fs (desktop-gated) -------
  private async scanExternalRoot(root: ScanRoot): Promise<Skill[]> {
    if (!this.canScanExternal()) return [];
    // `fs`/`path` are node builtins kept external by esbuild and provided by
    // the Electron runtime (desktop-only plugin).
    const skills: Skill[] = [];
    const files: string[] = [];
    // Resolve the configured root's real path once; the walk is confined to
    // this subtree so a symlink inside it can't escape to unintended trees.
    let rootReal: string;
    try {
      rootReal = await fs.promises.realpath(root.path);
    } catch (err) {
      console.error(`[skill-layer] external root unreadable ${root.path}:`, err);
      return [];
    }
    await this.walkFs(root.path, rootReal, 0, files, new Set<string>());

    for (const abs of files) {
      if (!isMarkdown(abs)) continue;
      let content: string;
      try {
        content = await fs.promises.readFile(abs, "utf8");
      } catch (err) {
        console.error(`[skill-layer] fs.readFile failed for ${abs}:`, err);
        continue;
      }
      const fm = parseFrontmatter(content);
      const fields = evaluateSkill(abs, fm, () => firstHeading(content));
      if (!fields) continue;

      const relForTag = this.relativeToRoot(abs, root.path);
      skills.push(
        this.makeSkill(fields, abs, null, root.path, "external", fm.tags ?? [], relForTag),
      );
    }
    return skills;
  }

  private async walkFs(
    dir: string,
    rootReal: string,
    depth: number,
    out: string[],
    seen: Set<string>,
  ): Promise<void> {
    if (depth > MAX_DEPTH) return;
    // Resolve symlinks and skip already-visited real directories to avoid
    // cycles (e.g. a symlink pointing back up the tree).
    let real: string;
    try {
      real = await fs.promises.realpath(dir);
    } catch {
      return;
    }
    // Confinement: the resolved path must be the root itself or under it.
    // A symlink that escapes outside the configured root is skipped.
    if (real !== rootReal && !real.startsWith(rootReal + nodePath.sep)) return;
    if (seen.has(real)) return;
    seen.add(real);

    let entries: fs.Dirent[];
    try {
      entries = await fs.promises.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = nodePath.join(dir, entry.name);
      if (entry.isDirectory() || entry.isSymbolicLink()) {
        if (IGNORED_DIRS.has(entry.name) || entry.name === this.app.vault.configDir) {
          continue;
        }
        // Stat through symlinks so we descend into linked directories too.
        let isDir = entry.isDirectory();
        if (entry.isSymbolicLink()) {
          try {
            isDir = (await fs.promises.stat(full)).isDirectory();
          } catch {
            isDir = false;
          }
        }
        if (isDir) await this.walkFs(full, rootReal, depth + 1, out, seen);
      } else if (entry.isFile()) {
        out.push(full);
      }
    }
  }

  private makeSkill(
    fields: SkillFields,
    absPath: string,
    vaultPath: string | null,
    sourceRoot: string,
    detection: DetectionMethod,
    frontmatterTags: string[],
    relForTag: string,
  ): Skill {
    return {
      id: absPath,
      name: fields.name,
      description: fields.description,
      path: absPath,
      vaultPath,
      sourceRoot,
      sourceLabel: inferSourceLabel(absPath),
      detection,
      tags: resolveSkillTags({
        relativePath: relForTag,
        description: fields.description,
        frontmatterTags,
      }),
    };
  }

  /** Best relative path for folder-tag derivation: vault path, else root-relative. */
  relativeForTag(skill: Skill): string {
    if (skill.vaultPath) return skill.vaultPath;
    return this.relativeToRoot(skill.path, skill.sourceRoot);
  }

  /** Path relative to a configured root (for folder-tag derivation). */
  private relativeToRoot(abs: string, root: string): string {
    const a = abs.replace(/\\/g, "/");
    const r = root.replace(/\\/g, "/").replace(/\/+$/, "");
    if (r && (a === r || a.startsWith(r + "/"))) {
      return a.slice(r.length).replace(/^\/+/, "");
    }
    return a.split("/").pop() ?? a;
  }

  /** Resolve a vault-relative path to a TFile, or null (dot/external files). */
  resolveTFile(vaultPath: string | null): TFile | null {
    if (!vaultPath) return null;
    const af = this.app.vault.getAbstractFileByPath(vaultPath);
    return af instanceof TFile ? af : null;
  }
}


### Session Management

// M20 — Sessions tab: pure helpers for tracking sessions the plugin launched and
// reconnecting to them in a terminal. No Obsidian / no fs / no spawn (those live
// in main.ts); everything here is side-effect-free and unit-testable.
//
// A "session" is one skill launch. It is recorded IMMEDIATELY at launch (so it
// shows up instantly — the launches are headless/detached and, when routed to a
// remote omnigent server, the conversation lives server-side and is never
// written to any local store, so there is nothing reliable to poll for). Because
// we don't capture a specific conversation id, "Connect" reopens via each tool's
// "continue most recent" mechanism, scoped as tightly as the tool allows:
//   - omnigent → `omnigent run <agent?> --server <url?> --harness <h?> -c`
//                (-c = continue the most recent conversation FOR THIS AGENT)
//   - claude   → `claude --continue`     (most recent in this cwd)
//   - codex    → `codex resume --last`   (most recent codex session)
//   - isaac    → `isaac resume`          (interactive picker of recent sessions;
//                a Claude Code CLI wrapper used by some custom harnesses)
// A launch through any OTHER (generic) custom harness has no known resume story
// and is not tracked. Precise per-conversation reconnect is a future iteration.

import { isValidOmnigentServer, shellSingleQuote } from "./launch";

// "custom" = a custom harness whose binary we don't recognize (universal
// tracking): it's still recorded, and Connect does a best-effort resume, falling
// back to a terminal hint to set a Resume command for the harness.
export type SessionTool = "omnigent" | "claude" | "codex" | "isaac" | "custom";

/** One tracked launch. Persisted in settings; pruned after 12h. */
export interface LaunchedSession {
  /** Stable de-dupe key (tool + launch time + nonce). */
  key: string;
  tool: SessionTool;
  /** The skill (or command) name that started it. */
  skillName: string;
  /** Absolute binary used to launch (reused verbatim for the resume command). */
  binaryPath: string;
  /** Launch cwd (the vault) — resume runs here. */
  cwd: string;
  /** Custom-harness id (to look up a user-set resume command), if launched via one. */
  harnessId?: string;
  /** Custom-harness display label (shown on the row instead of the tool). */
  harnessLabel?: string;
  /** omnigent custom-agent positional (bundle/file path), if any. */
  agentArg?: string;
  /** omnigent `--harness` value in effect, if any. */
  harness?: string;
  /** omnigent `--server` value in effect, re-applied on resume. */
  server?: string;
  /** Launch time, epoch ms. */
  startedAt: number;
}

/** Sessions older than this are dropped from the UI (and storage). */
export const SESSION_MAX_AGE_MS = 12 * 60 * 60 * 1000;

/** Whether a session has aged out (≥ 12h since launch). */
export function isSessionExpired(s: LaunchedSession, now: number): boolean {
  return now - s.startedAt >= SESSION_MAX_AGE_MS;
}

/** Map a custom-harness command's binary to a supported tool, or null. */
export function sessionToolFromCommand(binary: string): SessionTool | null {
  const base = (binary.split("/").pop() ?? binary).toLowerCase();
  if (base === "claude") return "claude";
  if (base === "codex") return "codex";
  if (base === "isaac") return "isaac";
  return null;
}

/**
 * The argv that reconnects to a session (binary + inert args), using each tool's
 * "continue most recent" mechanism. omnigent re-declares the agent/harness/server
 * so `-c` resolves to the latest conversation for THAT agent on THAT server.
 */
export function buildResumeArgv(s: LaunchedSession): string[] {
  if (s.tool === "omnigent") {
    const argv = [s.binaryPath, "run"];
    if (s.agentArg) argv.push(s.agentArg);
    if (isValidOmnigentServer(s.server)) argv.push("--server", s.server.trim());
    if (s.harness) argv.push("--harness", s.harness);
    argv.push("-c");
    return argv;
  }
  if (s.tool === "claude") return [s.binaryPath, "--continue"];
  if (s.tool === "isaac") return [s.binaryPath, "resume"];
  if (s.tool === "codex") return [s.binaryPath, "resume", "--last"];
  // "custom": best-effort guess (the most common continue flag). If it's wrong,
  // the terminal script surfaces a hint to set a Resume command for the harness.
  return [s.binaryPath, "--continue"];
}

/**
 * A macOS `.command` script that `cd`s into `cwd` and runs the resolved resume
 * `argv`. Written to a temp file and `open`ed so it launches in the user's
 * DEFAULT terminal. Every element is POSIX single-quoted so paths/ids with
 * metacharacters stay one inert argument. On a NON-ZERO exit (best-effort resume
 * failed / session not resumable) it prints `failHint` so the user isn't left
 * guessing. (Not `exec` — we need to observe the exit code to show the hint.)
 */
export function buildTerminalScript(
  argv: string[],
  cwd: string,
  failHint: string,
  platform: NodeJS.Platform = process.platform,
  keepOpen = false,
): { ext: string; content: string } {
  if (platform === "win32") {
    return { ext: ".bat", content: buildBatchScript(argv, cwd, failHint, keepOpen) };
  }
  // macOS uses `.command` (double-clickable / `open`-able in Terminal); other
  // Unix uses `.sh`. Both share the same bash body.
  return {
    ext: platform === "darwin" ? ".command" : ".sh",
    content: buildBashScript(argv, cwd, failHint, keepOpen),
  };
}

/**
 * A terminal script that `cd`s into `cwd` and runs a RAW user-authored script
 * `body` (the Bash Scripts tab). Unlike `buildTerminalScript` this embeds the
 * body verbatim (it IS shell source the user wrote), not a quoted argv. `cwd` is
 * still POSIX/quote-escaped. Used for the visible-terminal script-run path.
 */
export function buildRawTerminalScript(
  body: string,
  cwd: string,
  platform: NodeJS.Platform = process.platform,
): { ext: string; content: string } {
  if (platform === "win32") {
    return {
      ext: ".bat",
      content: ["@echo off", `cd /d "${cwd.replace(/"/g, '""')}"`, body, ""].join(
        "\r\n",
      ),
    };
  }
  return {
    ext: platform === "darwin" ? ".command" : ".sh",
    content: [
      "#!/bin/bash",
      // Self-delete so terminal session-restore (e.g. Ghostty/macOS reopen) can't
      // re-run this script and spawn a duplicate. The open fd keeps running fine.
      'rm -f "$0"',
      `cd ${shellSingleQuote(cwd)} || exit 1`,
      body,
      "",
    ].join("\n"),
  };
}

function buildBashScript(
  argv: string[],
  cwd: string,
  failHint: string,
  keepOpen = false,
): string {
  const cmd = argv.map(shellSingleQuote).join(" ");
  const hint = failHint.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  const lines = [
    "#!/bin/bash",
    // Self-delete so terminal session-restore (e.g. Ghostty/macOS reopen) can't
    // re-run this script and spawn a duplicate. The open fd keeps running fine.
    'rm -f "$0"',
    `cd ${shellSingleQuote(cwd)} || exit 1`,
    cmd,
    "code=$?",
    'if [ "$code" -ne 0 ]; then',
    '  echo ""',
    `  echo "${hint}"`,
    "fi",
  ];
  // Keep the window usable after the command exits: drop into an interactive
  // shell in the same cwd so the user can continue (e.g. resume the session).
  if (keepOpen) lines.push('exec "${SHELL:-/bin/bash}" -i');
  lines.push("");
  return lines.join("\n");
}

function buildBatchScript(
  argv: string[],
  cwd: string,
  failHint: string,
  keepOpen = false,
): string {
  const q = (s: string): string => `"${s.replace(/"/g, '""')}"`;
  const cmd = argv.map(q).join(" ");
  // Strip cmd.exe-special characters from the hint so `echo` prints it literally.
  const safeHint = failHint.replace(/[%&|<>^()"]/g, " ");
  const lines = [
    "@echo off",
    `cd /d ${q(cwd)}`,
    cmd,
    "if not errorlevel 1 goto :done",
    "echo.",
    `echo ${safeHint}`,
    ":done",
  ];
  // Keep the console open with a fresh prompt so the user can continue.
  if (keepOpen) lines.push("cmd /k");
  lines.push("");
  return lines.join("\r\n");
}

/** Short label describing the reconnect target (shown on the row). */
export function resumeTargetLabel(s: LaunchedSession): string {
  if (s.tool === "omnigent") {
    const agent = s.agentArg
      ? (s.agentArg.split("/").pop() ?? s.agentArg)
      : "default agent";
    const h = s.harness ? ` · ${s.harness}` : "";
    return `omnigent · ${agent}${h} · continues latest`;
  }
  if (s.tool === "claude") return "claude · continues latest in vault";
  if (s.tool === "isaac") return "isaac · resume picker";
  if (s.tool === "codex") return "codex · resumes last session";
  return "custom harness · best-effort resume";
}

/** Human "how long ago" label for a start time (e.g. "3m ago", "2h ago"). */
export function relativeTime(startedAt: number, now: number): string {
  const s = Math.max(0, Math.floor((now - startedAt) / 1000));
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ${m % 60}m ago`;
}


### Folder Scanning

// Canonical per-tool folder mapping (M18), adapted from the Agentfiles plugin's
// "Supported Tools" table (https://community.obsidian.md/plugins/agentfiles).
// Each coding assistant keeps its skills / commands / agents in a conventional
// dot-folder. We use this to PRE-SEED scan roots (so a user's skills across all
// tools are discovered automatically) and to source agents/commands per tool —
// while the user can still add custom scan roots (existing behavior).
//
// Pure / no Obsidian imports so it is unit-testable. Paths here are the
// vault-relative / home-relative SEGMENT (no leading `~/`); callers materialize
// them as vault-relative `adapter` roots and/or absolute `external` roots under
// the home directory.

import type { ScanRoot } from "./types";

/** One tool's conventional folders (relative segments; "" = not applicable). */
export interface ToolFolders {
  tool: string;
  /** e.g. ".claude/skills" */
  skills: string;
  /** e.g. ".claude/commands" / ".codex/prompts"; "" when the tool has none. */
  commands: string;
  /** e.g. ".claude/agents"; "" when the tool has none. */
  agents: string;
}

/** The canonical mapping. Order = discovery/scan-root priority. */
export const TOOL_FOLDERS: readonly ToolFolders[] = [
  { tool: "Claude Code", skills: ".claude/skills", commands: ".claude/commands", agents: ".claude/agents" },
  { tool: "Cursor", skills: ".cursor/skills", commands: "", agents: ".cursor/agents" },
  { tool: "Codex", skills: ".codex/skills", commands: ".codex/prompts", agents: ".codex/agents" },
  { tool: "Windsurf", skills: ".codeium/windsurf/memories", commands: "", agents: "" },
  { tool: "Copilot", skills: ".copilot/skills", commands: "", agents: "" },
  { tool: "Amp", skills: ".config/amp/skills", commands: "", agents: "" },
  { tool: "OpenCode", skills: ".config/opencode/skills", commands: "", agents: "" },
  { tool: "Global", skills: ".agents/skills", commands: "", agents: "" },
];

/** Distinct non-empty skills folder segments across all tools (deduped, ordered). */
export function skillFolderSegments(): string[] {
  return dedupe(TOOL_FOLDERS.map((t) => t.skills).filter(Boolean));
}

/** Distinct non-empty command folder segments across all tools. */
export function commandFolderSegments(): string[] {
  return dedupe(TOOL_FOLDERS.map((t) => t.commands).filter(Boolean));
}

/** Distinct non-empty agents folder segments across all tools. */
export function agentFolderSegments(): string[] {
  return dedupe(TOOL_FOLDERS.map((t) => t.agents).filter(Boolean));
}

function dedupe(xs: string[]): string[] {
  return Array.from(new Set(xs));
}

/** Every known tool-folder segment (skills + commands + agents), deduped. */
export function allToolFolderSegments(): string[] {
  const all: string[] = [];
  for (const t of TOOL_FOLDERS) {
    if (t.skills) all.push(t.skills);
    if (t.commands) all.push(t.commands);
    if (t.agents) all.push(t.agents);
  }
  return dedupe(all);
}

/**
 * The actual tool folder an absolute path lives under (e.g. `.claude/skills`,
 * `.codex/prompts`, `.claude/agents`), or null when it matches no known tool
 * folder. Matches the LONGEST segment first so a nested segment like
 * `.codeium/windsurf/memories` wins over any shorter accidental match. The match
 * is on the path containing `/<segment>/` (works for both in-vault and home-dir
 * paths). Case-insensitive. Pure / unit-testable.
 */
export function toolFolderForPath(absPath: string): string | null {
  const p = absPath.replace(/\\/g, "/").toLowerCase();
  const segments = allToolFolderSegments().sort((a, b) => b.length - a.length);
  for (const seg of segments) {
    if (p.includes(`/${seg.toLowerCase()}/`)) return seg;
  }
  return null;
}

/**
 * The default SKILL scan roots pre-seeded from the tool map: each tool's skills
 * folder as a vault-relative `adapter` root AND (when a home dir is given) an
 * absolute `external` root under home. `homedir` is injected (null to omit the
 * home roots) so this stays pure / testable. Vault-relative roots are enabled by
 * default. Home-directory (global) skill folders are intentionally NOT added —
 * a machine can have hundreds of global tool skills, and mixing them with the
 * user's in-vault skills is confusing. Users can add a custom scan root if they
 * want to browse global skills.
 */
export function defaultSkillScanRoots(): ScanRoot[] {
  const roots: ScanRoot[] = [
    // The vault itself (non-dot markdown / SKILL.md anywhere) — unchanged M1 root.
    { path: "", kind: "vault", enabled: true },
  ];
  for (const seg of skillFolderSegments()) {
    roots.push({ path: seg, kind: "adapter", enabled: true });
  }
  return roots;
}

/** The absolute home-dir skill-folder paths M18 previously auto-added (external,
 *  disabled). Used to clean them out of existing settings. */
export function homeSkillRootPaths(homedir: string): string[] {
  return skillFolderSegments().map((seg) => joinHome(homedir, seg));
}

/** Join a home dir and a relative segment with a single forward slash. */
export function joinHome(homedir: string, seg: string): string {
  return homedir.replace(/\/+$/, "") + "/" + seg.replace(/^\/+/, "");
}


### Terminal Integration

// Preferred TERMINAL EMULATOR registry, detection, and opener-command builder.
//
// This backs the "Preferred terminal" setting + the "run in a terminal" launch
// mode. Terminal mode writes a temp script that `cd`s into the vault and runs the
// skill's SAME resolved harness command headless mode would run (omnigent / a
// custom harness) — the only difference is it runs VISIBLY in the user's chosen
// terminal emulator instead of detached. This module decides WHICH terminal opens
// that script; it never constructs the harness command itself.
//
// Pure / injectable (no Obsidian imports; fs + platform injected) so it stays
// unit-testable, matching launch.ts. macOS is the primary target (this is a
// desktop-only, macOS-centric plugin); Windows/Linux always fall back to the
// default-terminal opener regardless of the chosen emulator.

import * as nodePath from "path";

/** The opener process to spawn: an absolute-ish bin + inert args. */
export interface OpenerCommand {
  bin: string;
  args: string[];
}

/**
 * A supported terminal emulator. Detection is by macOS app bundle (`appName` →
 * `/Applications/<appName>.app`) and/or a binary on PATH-standard dirs
 * (`binName`). `macOpener` builds the spawn command to open a written script in
 * that terminal on macOS; when absent the default opener is used. `auto` (no
 * appName/binName/macOpener) always resolves to the OS default terminal.
 */
export interface TerminalDefinition {
  id: string;
  label: string;
  /** macOS app bundle base name, e.g. "Ghostty" (detected in the app dirs). */
  appName?: string;
  /** CLI binary name, e.g. "ghostty"/"tmux" (detected in the standard bin dirs). */
  binName?: string;
  /**
   * Opener using the resolved CLI BINARY (preferred when the binary is detected)
   * — the reliable way to run a command in emulators that ship a CLI (Ghostty,
   * kitty, WezTerm all take `-e`/`start`). Pure function of (binPath, scriptPath).
   */
  binOpener?: (binPath: string, scriptPath: string) => OpenerCommand;
  /**
   * macOS opener via the app bundle (`open …`) — the FALLBACK when no CLI binary
   * is detected. Omit to use the default opener. Pure function of the script path.
   */
  macOpener?: (scriptPath: string) => OpenerCommand;
  /**
   * True when this terminal runs the script DETACHED (no window we control), so
   * the caller shows a "how to attach" hint instead of a plain open Notice
   * (currently only tmux). Display concern only.
   */
  detached?: boolean;
}

/** Fixed tmux session name reused across launches so attaches are predictable. */
export const TMUX_SESSION = "skill-harness";

/**
 * The hardcoded terminal registry. `auto` first (the safe default). GUI
 * emulators use `open`/`open -na`; tmux runs the script in a detached session the
 * user attaches to. Order is the settings-dropdown order.
 */
export const KNOWN_TERMINALS: readonly TerminalDefinition[] = [
  { id: "auto", label: "Auto (OS default terminal)" },
  {
    id: "terminal",
    label: "Terminal",
    appName: "Terminal",
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-a", "Terminal", s] }),
  },
  {
    id: "iterm",
    label: "iTerm",
    appName: "iTerm",
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-a", "iTerm", s] }),
  },
  {
    id: "ghostty",
    label: "Ghostty",
    appName: "Ghostty",
    binName: "ghostty",
    // Preferred: the ghostty CLI runs an initial command via `-e` reliably.
    binOpener: (bin, s) => ({ bin, args: ["-e", "bash", s] }),
    // Fallback (no CLI): `open -na` does NOT reliably pass `-e`, so just open the
    // app — the script won't auto-run. Install the `ghostty` CLI for auto-run.
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-na", "Ghostty", "--args", "-e", "bash", s] }),
  },
  {
    id: "kitty",
    label: "kitty",
    appName: "kitty",
    binName: "kitty",
    binOpener: (bin, s) => ({ bin, args: ["bash", s] }),
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-na", "kitty", "--args", "bash", s] }),
  },
  {
    id: "wezterm",
    label: "WezTerm",
    appName: "WezTerm",
    binName: "wezterm",
    binOpener: (bin, s) => ({ bin, args: ["start", "--", "bash", s] }),
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-na", "WezTerm", "--args", "start", "--", "bash", s] }),
  },
  {
    id: "cmux",
    label: "cmux",
    appName: "cmux",
    // cmux (manaflow-ai/cmux) is an Electron agent-orchestration app, not a
    // classic emulator with a documented run-a-command flag. Best-effort: open
    // the app with the script path as an arg. If cmux ignores it, the launch
    // won't auto-run — use Ghostty/Terminal for a guaranteed run.
    macOpener: (s) => ({
      bin: "/usr/bin/open",
      args: ["-na", "cmux", "--args", s],
    }),
  },
  {
    id: "tmux",
    label: "tmux",
    binName: "tmux",
    detached: true,
  },
] as const;

/** Look up a terminal definition by id, or undefined. */
export function terminalById(
  id: string | undefined | null,
): TerminalDefinition | undefined {
  if (typeof id !== "string" || !id) return undefined;
  return KNOWN_TERMINALS.find((t) => t.id === id);
}

/** Standard bin dirs a CLI terminal (tmux) is probed in (POSIX / Windows). */
export function terminalBinCandidates(
  binName: string,
  homedir: string,
  platform: NodeJS.Platform = process.platform,
): string[] {
  if (platform === "win32") {
    return [".exe", ".cmd", ".bat", ""].map((ext) =>
      nodePath.join(homedir, ".local", "bin", binName + ext),
    );
  }
  return [
    `/opt/homebrew/bin/${binName}`,
    `/usr/local/bin/${binName}`,
    `${homedir}/.local/bin/${binName}`,
  ];
}

/** A detected terminal: its definition plus (when found) the resolved CLI binary path. */
export interface DetectedTerminal {
  def: TerminalDefinition;
  /** Resolved CLI binary path when detected (ghostty/kitty/wezterm/tmux); else undefined. */
  binPath?: string;
}

/**
 * Detect which known terminals are available. `auto` is ALWAYS included. On
 * non-macOS only `auto` is offered (the emulator list is macOS-centric and
 * Windows/Linux use the default terminal regardless). On macOS an emulator is
 * detected when its CLI binary exists (probed in the standard bin dirs) OR its
 * app bundle exists in any of `appDirs`; the resolved `binPath` is attached when
 * a binary is found (preferred at open time). fs is injected (`exists`) so this
 * stays pure / unit-testable.
 */
export function detectInstalledTerminals(opts: {
  homedir: string;
  appDirs: string[];
  exists: (p: string) => boolean;
  platform?: NodeJS.Platform;
}): DetectedTerminal[] {
  const platform = opts.platform ?? process.platform;
  const out: DetectedTerminal[] = [];
  for (const def of KNOWN_TERMINALS) {
    if (def.id === "auto") {
      out.push({ def });
      continue;
    }
    if (platform !== "darwin") continue; // only auto off macOS
    // Prefer a CLI binary (reliable run-a-command) — probe it first.
    let binPath: string | undefined;
    if (def.binName) {
      for (const c of terminalBinCandidates(def.binName, opts.homedir, platform)) {
        if (opts.exists(c)) {
          binPath = c;
          break;
        }
      }
    }
    const hasApp =
      !!def.appName &&
      opts.appDirs.some((dir) => opts.exists(nodePath.join(dir, `${def.appName}.app`)));
    if (binPath) out.push({ def, binPath });
    else if (hasApp) out.push({ def });
  }
  return out;
}

/**
 * Resolve the effective preferred terminal, FAILING CLOSED to `auto`. Returns the
 * DetectedTerminal for `preferredId` when still available, else the `auto` entry
 * (always present). Pure / unit-testable.
 */
export function resolvePreferredTerminal(
  preferredId: string | undefined | null,
  detected: DetectedTerminal[],
): DetectedTerminal {
  if (typeof preferredId === "string" && preferredId) {
    const match = detected.find((d) => d.def.id === preferredId);
    if (match) return match;
  }
  const auto = detected.find((d) => d.def.id === "auto");
  return auto ?? { def: KNOWN_TERMINALS[0] };
}

/**
 * Build the opener command that runs the written `scriptPath` in `terminal`.
 * - tmux → `<tmux> new-session -A -s skill-harness bash <script>` (detached; the
 *   caller tells the user to `tmux attach -t skill-harness`).
 * - a CLI binary was detected + the def has a `binOpener` → run via the binary
 *   (the RELIABLE run-a-command path; e.g. `ghostty -e bash <script>`).
 * - tmux (binName, no binOpener) → its detached `new-session` form.
 * - a macOS GUI emulator with a `macOpener` (and platform darwin) → that opener.
 * - otherwise → the DEFAULT opener: `open <script>` (macOS), `cmd /c start "" …`
 *   (Windows), `$TERMINAL -e bash <script>` / `x-terminal-emulator` (Linux).
 * `env` (Linux `$TERMINAL`) is injected. Pure / unit-testable.
 */
export function buildOpenerCommand(opts: {
  terminal: DetectedTerminal;
  scriptPath: string;
  platform?: NodeJS.Platform;
  linuxTerminalEnv?: string;
}): OpenerCommand {
  const platform = opts.platform ?? process.platform;
  const { def, binPath } = opts.terminal;
  const s = opts.scriptPath;

  // Preferred: a detected CLI binary with a binOpener runs the command reliably.
  if (binPath && def.binOpener) {
    return def.binOpener(binPath, s);
  }
  if (def.id === "tmux" && binPath) {
    return {
      bin: binPath,
      args: ["new-session", "-A", "-s", TMUX_SESSION, "bash", s],
    };
  }
  if (platform === "darwin" && def.macOpener) {
    return def.macOpener(s);
  }
  return buildDefaultOpener(s, platform, opts.linuxTerminalEnv);
}

/** The OS default-terminal opener (also the `auto` opener). Pure / unit-testable. */
export function buildDefaultOpener(
  scriptPath: string,
  platform: NodeJS.Platform = process.platform,
  linuxTerminalEnv?: string,
): OpenerCommand {
  if (platform === "win32") {
    return { bin: "cmd.exe", args: ["/c", "start", "", scriptPath] };
  }
  if (platform === "darwin") {
    return { bin: "/usr/bin/open", args: [scriptPath] };
  }
  return {
    bin: linuxTerminalEnv || "x-terminal-emulator",
    args: ["-e", "bash", scriptPath],
  };
}


### YAML Frontmatter Viewer

// Pure decision logic for opening a custom-agent `config.yaml` in the "YAML
// Viewer" community plugin (id `yaml-viewer`) instead of the OS default app.
// Side-effect-free and free of any Obsidian/Electron imports so it is
// unit-testable in the smoke suite (same pattern as viewToggle.ts). The actual
// workspace mutation (`setViewState`) and TFile/FileSystemAdapter access live in
// main.ts, which injects those into these helpers.

/** YAML Viewer's manifest id AND the view type it registers (both `yaml-viewer`). */
export const YAML_VIEWER_PLUGIN_ID = "yaml-viewer";
export const YAML_VIEWER_VIEW_TYPE = "yaml-viewer";

/** YAML Viewer registers extensions ["yaml","yml"]; only these can open in it. */
export function isYamlFile(path: string): boolean {
  return /\.ya?ml$/i.test(path);
}

/**
 * True iff the YAML Viewer plugin is BOTH installed and enabled, read from the
 * untyped community-plugins API surface (`app.plugins`). Mirrors the documented
 * shape: an `enabledPlugins` Set plus a `plugins` registry keyed by id.
 */
export function detectYamlViewerEnabled(plugins: unknown): boolean {
  const p = plugins as
    | {
        enabledPlugins?: { has?: (id: string) => boolean };
        plugins?: Record<string, unknown>;
      }
    | null
    | undefined;
  return Boolean(
    p?.enabledPlugins?.has?.(YAML_VIEWER_PLUGIN_ID) &&
      p?.plugins?.[YAML_VIEWER_PLUGIN_ID],
  );
}

/** Filesystem path helpers main.ts injects (node `path`) so this stays pure. */
export interface PathDeps {
  relative: (from: string, to: string) => string;
  isAbsolute: (p: string) => boolean;
  sep: string;
}

/**
 * Map an absolute filesystem path to an in-vault path (forward slashes), or null
 * when the path is OUTSIDE the vault. A `rel` that is empty, starts with ".."
 * (parent traversal), or is itself absolute means out-of-vault → null. Dot-folder
 * paths (e.g. `.omnigent/...`) stay inside the vault here but won't resolve to a
 * TFile because Obsidian doesn't index them — that null comes from the lookup in
 * resolveVaultTFile, not from this path math.
 */
export function toVaultRelativePath(
  basePath: string,
  absPath: string,
  deps: PathDeps,
): string | null {
  const rel = deps.relative(basePath, absPath);
  if (rel === "" || rel.startsWith("..") || deps.isAbsolute(rel)) return null;
  return rel.split(deps.sep).join("/");
}

/** Lookup deps main.ts injects (the Vault API + an `instanceof TFile` check). */
export interface ResolveDeps<T> extends PathDeps {
  getAbstractFileByPath: (vaultPath: string) => T | null;
  isTFile: (f: T | null) => boolean;
}

/**
 * Resolve an absolute filesystem path to the in-vault TFile it names, or null.
 * Null when: there's no vault base path (adapter isn't a FileSystemAdapter), the
 * path is out-of-vault, or the vault-relative path doesn't index to a TFile
 * (covers non-indexed dot-folders and external scan roots).
 */
export function resolveVaultTFile<T>(
  basePath: string | null | undefined,
  absPath: string,
  deps: ResolveDeps<T>,
): T | null {
  if (basePath == null) return null;
  const vaultPath = toVaultRelativePath(basePath, absPath, deps);
  if (vaultPath == null) return null;
  const f = deps.getAbstractFileByPath(vaultPath);
  return deps.isTFile(f) ? f : null;
}

/**
 * The gate for routing an "Open file" click to the YAML Viewer: the viewer must
 * be enabled, the target must look like YAML, and it must resolve to an in-vault
 * TFile. Any false → caller falls back to the existing `shell.openPath` behavior.
 */
export function canOpenInYamlViewer(opts: {
  viewerEnabled: boolean;
  fileToOpen: string;
  hasTFile: boolean;
}): boolean {
  return opts.viewerEnabled && isYamlFile(opts.fileToOpen) && opts.hasTFile;
}


### README

# Skill and Harness Manager

**Consolidate, organize, and manage your AI skills — right inside your vault.**

If you've collected AI *skills* (`SKILL.md` files), commands, and agents across
different tools — `.claude/`, `.codex/`, `.cursor/`, `.agents/`, marketplace
folders, loose notes — they end up scattered and hard to actually use. This
plugin gathers them into one place, lets you organize, filter, and tag them, and
makes each one runnable with a click.

> No bundled model, no inference, no network calls of its own. It finds,
> organizes, and launches; the actual work runs in whatever AI CLI you point it
> at (Claude Code, Codex, omnigent, or your own).

## What you can do with it

Run AI where you already work:

- **Reformat a markdown note with one click** — pin a "clean up markdown" skill
  to the sidebar and run it on the current file.
- **Process an audio file** — right-click a recording and run a
  transcribe/summarize skill against it.
- **Trigger daily automations** — kick off a daily-note or digest skill from a
  ribbon button.
- …and anything else you can capture as a skill.

## How you launch skills

Skills can be run from wherever is most convenient:

- **Right-click a file** in the file explorer → run a skill *targeting that file*
  (great for "reformat this note", "transcribe this audio", "summarize this").
- **Sidebar buttons** — pin any skill to its own ribbon icon (with a custom
  Lucide icon) to create one-click launchers for the skills you use most.
- **Command palette** — every pinned skill also registers a command.
- **The browser view** — open it and launch anything from there.

## The browser

A single view (`brain-circuit` ribbon icon) with tabs:

- **Skills** / **Commands** — everything discovered across your scan roots,
  grouped into a collapsible source-folder tree, each with its description and
  tags. Multi-select filters by agent, harness, tag, and access, plus search.
- **Scripts** — your own bash scripts (add a name, description, and body right in
  the tab). Each script runs on click, in a terminal or headless, per its own
  setting — handy for maintenance commands like updating or launching a harness.
- **Sessions** — the launches you've started, with a **Connect** button that
  reopens the session in your terminal. Auto-pruned after 12h.
- **Agents** / **Harnesses** — the agents you can run skills as, and the
  launchers that actually run them.

The plugin also seeds one **example skill** into `.agents/skills/` on first run
(tagged `#example`) so a fresh install has something to explore. Editing or
deleting it is safe — it is never recreated.

## Launch modes: headless or terminal

Every skill/command can run one of two ways:

- **Headless** — spawned in the background (omnigent or a custom harness);
  progress surfaces via notices and the Sessions tab.
- **Terminal** — runs the *same* harness command, but visibly in a terminal
  window in the vault so you can watch it and interact.

Set the **default launch mode** and your **preferred terminal** in Settings →
*General*. The preferred-terminal list is autodetected from the emulators you
have installed (Terminal, iTerm, Ghostty, kitty, WezTerm, Warp, tmux); *Auto*
uses your OS default terminal. Override the mode per skill in its ⚙ Configure
panel.

## Harnesses (how skills get run)

A **harness** is the command that actually executes a skill — usually an AI CLI.
omnigent is supported out of the box; you can add your own for Claude Code,
Codex, or anything else.

**Add one manually:** Settings → *Skill and Harness Manager* → **Custom
harnesses** → give it a name and a one-line command whose first token is the
absolute path to the binary and which contains the `{prompt}` placeholder, e.g.:

```
/opt/homebrew/bin/claude -p {prompt}
```

The plugin substitutes the skill's prompt into `{prompt}` and runs it (no shell,
array arguments). Optionally set a **Resume command** so the Sessions tab's
*Connect* can reopen a session.

**Let the model add itself:** run this prompt inside your CLI (Claude Code,
Codex, omnigent, …) and it will register itself as a harness. The same prompt is
available with a copy button in the plugin's settings.

```
Register yourself as a launch harness in my Obsidian "Skill and Harness Manager" plugin.

1. Open the plugin config JSON at:
   <vault>/.obsidian/plugins/skill-harness-manager/data.json
2. Parse it as JSON and ensure it has a top-level "harnesses" array (create it if missing).
3. Append ONE entry describing how to run YOU non-interactively with a single prompt:
     {
       "id": "<short-kebab-id>",
       "label": "<your product name>",
       "command": ["<absolute path to your CLI>", "<non-interactive flags>", "{prompt}"]
     }
   Rules: command[0] must be an absolute path; exactly one element must contain the
   literal token {prompt}; leave every other key in the file unchanged; write back valid JSON.
   Optional: add "resumeCommand": ["<absolute CLI>", "<resume flags>"] (no {prompt}) to enable
   the Sessions tab's "Connect" button.
4. Tell me to reload the plugin (Settings → Community plugins → toggle it off and on),
   after which the new harness appears in the plugin.
```

## Requirements

Desktop only — it scans folders and launches local CLIs. Launching a skill needs
whatever CLI you configure; browsing, organizing, tagging, and filtering work
without one.

## Install

**From Obsidian:** Settings → Community plugins → Browse → search
**"Skill and Harness Manager"** → Install → Enable. No Node, no building.

**Manual / pre-release:** download `main.js`, `manifest.json`, and `styles.css`
from the [latest release](https://github.com/joeutke-dev/skill-harness-manager/releases)
into `<vault>/.obsidian/plugins/skill-harness-manager/`, then enable it.

## Development

```bash
npm install
npm run typecheck
npm run lint
npm run smoke
npm run build
```

Releases are automated: push a tag (`git tag 0.1.2 && git push --tags`) and
`.github/workflows/release.yml` builds and publishes the assets.

## License

MIT

