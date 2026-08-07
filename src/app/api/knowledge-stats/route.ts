import { NextResponse } from 'next/server';
import { getVaultStats } from '@/lib/vault-search';

export async function GET() {
  try {
    const index = await getVaultStats();

    if (!index) {
      return NextResponse.json({
        totalFiles: 0,
        totalCategories: 0,
        totalSizeMB: '0',
        categories: [],
        engine: 'none',
      });
    }

    const categories = Object.entries(index.categories || {})
      .map(([key, count]: [string, any]) => ({ key, count: Number(count) }))
      .sort((a, b) => b.count - a.count);

    return NextResponse.json({
      totalFiles: index.totalChunks || 0,
      totalCategories: categories.length,
      totalSizeMB: index.totalSourceChars ? (index.totalSourceChars / 1024 / 1024).toFixed(1) : '0',
      categories,
      engine: index.engine || 'unknown',
      skills: index.skills || 0,
      skillTags: index.skillTags || {},
    });
  } catch (error) {
    console.error('Knowledge stats error:', error);
    return NextResponse.json(
      { error: 'Failed to load knowledge stats' },
      { status: 500 }
    );
  }
}
