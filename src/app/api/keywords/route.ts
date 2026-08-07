import { NextResponse } from 'next/server';
import { readdir, readFile } from 'fs/promises';
import path from 'path';

const KEYWORD_DIR = process.env.KEYWORD_DIR || path.join(process.cwd(), 'data', 'keyword-research');

export async function GET() {
  try {
    const files = await readdir(KEYWORD_DIR).then(f => f.filter(f => f.endsWith('.json')));
    const results: Array<{
      filename: string;
      label: string;
      count: number;
      keywords: Array<Record<string, any>>;
    }> = [];

    for (const file of files) {
      try {
        const raw = await readFile(path.join(KEYWORD_DIR, file), 'utf-8');
        const data = JSON.parse(raw);
        const keywords = Array.isArray(data) ? data : data.keywords || data.data || [];

        // Derive a label from filename: kw_cloud_stack.json → "Cloud Stack"
        const label = file
          .replace(/^kw_/, '')
          .replace(/\.json$/i, '')
          .replace(/_/g, ' ')
          .replace(/\b\w/g, c => c.toUpperCase());

        results.push({ filename: file, label, count: keywords.length, keywords });
      } catch {
        results.push({ filename: file, label: file, count: 0, keywords: [] });
      }
    }

    // Sort by count descending
    results.sort((a, b) => b.count - a.count);

    const totalKeywords = results.reduce((sum, r) => sum + r.count, 0);

    return NextResponse.json({
      datasets: results,
      totalDatasets: results.length,
      totalKeywords,
    });
  } catch (error) {
    console.error('Keywords API error:', error);
    return NextResponse.json(
      { error: 'Failed to load keyword data', datasets: [], totalDatasets: 0, totalKeywords: 0 },
      { status: 500 }
    );
  }
}
