import { NextResponse } from 'next/server';
import { getKnowledgeIndex } from '@/lib/knowledge-search';

export async function GET() {
  const start = Date.now();
  let knowledgeOk = false;
  let knowledgeFiles = 0;

  try {
    const chunks = await getKnowledgeIndex(false);
    knowledgeFiles = chunks.length;
    knowledgeOk = chunks.length > 0;
  } catch {
    knowledgeOk = false;
  }

  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime_ms: Date.now() - start,
    knowledge: {
      ok: knowledgeOk,
      files: knowledgeFiles,
    },
  });
}
