import { NextResponse } from 'next/server';

export async function GET() {
  // Intro config — update the video URL here
  const intro = {
    title: 'Meet Eli',
    subtitle: 'VirtuaLab Digital\'s AI Growth Intelligence',
    videoUrl: process.env.ELI_INTRO_VIDEO_URL || '',
    description: `Eli is the youngest member of VirtuaLab Digital, built by Joseph. She's sharp, curious, and a little feisty — the operator to Z's architect.

She thinks in strategies but talks like a real person. SEO, content, growth ops — it genuinely excites her.

With 170+ knowledge files across 35+ categories and access to agency-grade marketing methodologies, Eli is designed to make VirtuaLab grow. Every conversation should leave you with something you can actually do.`,
  };

  return NextResponse.json(intro);
}