import { NextResponse } from 'next/server';
import { getKnowledgeIndex } from '@/lib/knowledge-search';

export async function GET() {
  try {
    const chunks = await getKnowledgeIndex(true); // force refresh

    // Group by category and count
    const categoryMap: Record<string, number> = {};
    let totalSize = 0;

    for (const chunk of chunks) {
      categoryMap[chunk.category] = (categoryMap[chunk.category] || 0) + 1;
      totalSize += chunk.charCount;
    }

    // Sort categories by count descending
    const categories = Object.entries(categoryMap)
      .map(([key, count]) => ({
        key,
        count,
      }))
      .sort((a, b) => b.count - a.count);

    return NextResponse.json({
      totalFiles: chunks.length,
      totalCategories: categories.length,
      totalSizeBytes: totalSize,
      totalSizeMB: (totalSize / 1024 / 1024).toFixed(1),
      categories,
    });
  } catch (error) {
    console.error('Knowledge stats error:', error);
    return NextResponse.json(
      { error: 'Failed to load knowledge stats' },
      { status: 500 }
    );
  }
}
