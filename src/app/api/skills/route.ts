import { NextResponse } from 'next/server';
import { readdir, readFile } from 'fs/promises';
import path from 'path';

const SKILLS_DIR = process.env.SKILLS_DIR || path.join(process.cwd(), 'data', 'eli-os-delivery', 'skill-templates');

export async function GET() {
  try {
    const files = await readdir(SKILLS_DIR).then(f => f.filter(f => f.endsWith('.md')));
    const skills: Array<{
      filename: string;
      name: string;
      description: string;
      content: string;
    }> = [];

    for (const file of files) {
      try {
        const raw = await readFile(path.join(SKILLS_DIR, file), 'utf-8');
        // Extract first heading and first paragraph as description
        const headingMatch = raw.match(/^#\s+(.+)$/m);
        const descMatch = raw.match(/\n#\s+.+\n+([^{#\n][^\n]{20,200})/);

        const name = headingMatch
          ? headingMatch[1].replace(/[^a-zA-Z0-9\s-]/g, '').trim()
          : file.replace(/\.md$/, '').replace(/_/g, ' ');
        const description = descMatch
          ? descMatch[1].trim()
          : 'Eli skill template — ' + file.replace(/\.md$/, '').replace(/_/g, ' ');

        skills.push({ filename: file, name, description, content: raw });
      } catch {
        skills.push({
          filename: file,
          name: file.replace(/\.md$/, ''),
          description: 'Skill template',
          content: '',
        });
      }
    }

    return NextResponse.json({ skills, total: skills.length });
  } catch (error) {
    console.error('Skills API error:', error);
    return NextResponse.json(
      { error: 'Failed to load skills', skills: [], total: 0 },
      { status: 500 }
    );
  }
}
