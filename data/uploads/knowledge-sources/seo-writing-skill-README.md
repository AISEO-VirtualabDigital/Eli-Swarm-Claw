---
Source: https://github.com/flaqai/Awesome_SEO_Writing_Skill
Category: seo
Description: Share the awesome skills for SEO Writing. All the skills are developed by Flaq AI Team
Stars: 31
Topics: codex-skills, seo, seo-optimization, seo-tools, seo-writing, seo-writing-skill, writing
FetchedAt: 2026-08-04T19:03:58.661Z
---

# Awesome SEO Writing Skill

> Created by [Flaq.ai](https://flaq.ai/) — a comprehensive, all-in-one Agentic API solution that gives AI agents and production applications unified access to advanced image, video, and LLM models.

This writing skill distills nearly two years of hands-on SEO writing, content production, fact-checking, image packaging, and publishing experience. It also incorporates useful community ideas, especially Zimu's SEO audit workflow and the reader-focused humanization approach documented by `blader/humanizer`.

**References and acknowledgements:**

- Website: [Flaq.ai — an all-in-one AI Agentic API solution](https://flaq.ai/)
- Community reference: Zimu's [SEO Audit Skill](https://github.com/JeffLi1993/seo-audit-skill)
- Writing reference: [`blader/humanizer`](https://github.com/blader/humanizer), used as inspiration for the post-audit humanization workflow
- Recommended collection: [Awesome Codex Skills](https://github.com/flaqai/awesome_codex_skills)
- Recommended collection: [Awesome Claude Code Skills](https://github.com/flaqai/awesome_claude_code_skills)

---

[![English](https://img.shields.io/badge/English-Current-brightgreen)](README.md) [![简体中文](https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-View-lightgrey)](README_zh.md) [![繁體中文](https://img.shields.io/badge/%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-View-lightgrey)](README_tw.md) [![日本語](https://img.shields.io/badge/%E6%97%A5%E6%9C%AC%E8%AA%9E-View-lightgrey)](README_ja.md) [![한국어](https://img.shields.io/badge/%ED%95%9C%EA%B5%AD%EC%96%B4-View-lightgrey)](README_ko.md) [![ไทย](https://img.shields.io/badge/%E0%B9%84%E0%B8%97%E0%B8%A2-View-lightgrey)](README_th.md) [![Tiếng Việt](https://img.shields.io/badge/Ti%E1%BA%BFng%20Vi%E1%BB%87t-View-lightgrey)](README_vi.md) [![Bahasa Indonesia](https://img.shields.io/badge/Bahasa%20Indonesia-View-lightgrey)](README_id.md) [![Español](https://img.shields.io/badge/Espa%C3%B1ol-View-lightgrey)](README_es.md) [![Français](https://img.shields.io/badge/Fran%C3%A7ais-View-lightgrey)](README_fr.md) [![Deutsch](https://img.shields.io/badge/Deutsch-View-lightgrey)](README_de.md) [![Italiano](https://img.shields.io/badge/Italiano-View-lightgrey)](README_it.md) [![Português](https://img.shields.io/badge/Portugu%C3%AAs-View-lightgrey)](README_pt.md) [![Русский](https://img.shields.io/badge/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-View-lightgrey)](README_ru.md) [![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-View-lightgrey)](README_ar.md)

---

## What This Skill Does

Awesome SEO Writing Skill is a reusable workflow for AI coding agents such as Codex and Claude Code. It turns a content request into a structured process covering the task brief, outline, writing, fact-checking, SEO audit, image generation, and file delivery.

- Writes SEO-focused how-to articles, comparisons, listicles, and explainers.
- Aligns the title, introduction, headings, FAQ, conclusion, and metadata with one search intent.
- Checks product features, prices, dates, statistics, policies, and comparison claims.
- Separates deterministic SEO checks from semantic editorial judgment.
- Humanizes the audit-corrected draft while preserving verified facts, search intent, citations, code, links, and the author's intended voice.
- Produces 16:9 article images and uses local Markdown paths by default.
- Optionally compresses and uploads images to Cloudflare R2 when local configuration exists.
- Includes a separate `medium-writer` workflow for narrative, editorial, review, and thought-leadership articles.

## Design Principles

### 1. Search intent before keyword density

The article must answer why the reader searched. The title, first 100 words, sections, FAQ, and conclusion should solve the same core problem instead of repeating an exact keyword.

### 2. Outline before body copy

The workflow starts with a task card of no more than ten lines, followed by title selection and an outline. Even one-shot article requests internally follow `task card -> outline -> draft` to reduce drift and repetition.

### 3. Facts and opinions stay separate

Dates, prices, product capabilities, policies, statistics, and comparative claims require evidence. Recommendations are editorial judgment. Unverified claims should be cited, softened, or removed rather than invented for SEO completeness.

### 4. Audit-driven improvement

The skill checks measurable items such as title length, keyword position, H1 count, FAQ presence, and metadata before evaluating intent, depth, credibility, and prose quality. Factual risks and high-impact issues are fixed first.

### 5. Humanize after the audit, then verify again

Once factual and SEO issues are fixed, the workflow runs a dedicated humanization pass inspired by [`blader/humanizer`](https://github.com/blader/humanizer). It looks for clusters of mechanical writing such as inflated significance, promotional language, vague attribution, repetitive transitions, forced symmetry, uniform rhythm, generic conclusions, and chatbot artifacts. It does not invent personal experience or promise to bypass AI detectors. Any changed facts, keywords, metadata, links, code, or image paths are rechecked before delivery.

### 6. Files are the primary deliverable

Final articles live under `writer/output/<article-slug>/`. The article, audit, images, and optional upload manifest stay together for publishing, review, and handoff.

### 7. Local images first, R2 as progressive enhancement

Every article starts with portable local references:

```markdown
![AI video workflow](./section-01-16x9.png)
```

The skill uploads images only when `writer/config/r2.config.json` exists and is valid. Without that file, the local article remains a complete deliverable: no credentials are requested and the writing task does not fail.

## Repository Structure

```text
.
├── README.md
├── README_*.md
└── writer/
    ├── SKILL.md
    ├── medium-writer/
    │   └── SKILL.md
    ├── config/
    │   └── r2.config.example.json
    ├── references/
    │   ├── fact-check-and-style.md
    │   ├── humanization.md
    │   ├── output-packaging.md
    │   ├── r2-image-upload.md
    │   ├── r2-security.md
    │   ├── seo-article-template.md
    │   └── seo-audit-checklist.md
    ├── scripts/
    │   └── upload-r2.mjs
    └── output/
        └── <article-slug>/
            ├── article.md
            ├── seo-audit.md
            ├── hero-16x9.png
            └── image-urls.json  # Created only after a successful R2 upload
```

## How to Use

Copy the `writer/` directory into the root of your target project, then explicitly ask your agent to use it:

```text
Use the writer skill to create an English how-to article about
"AI music detector" for YouTube creators.

Main keyword: AI music detector
Supporting keywords: AI-generated music, Content ID, music copyright
Length: 1,200-1,500 words
Requirements: fact-checking, three 16:9 images, SEO audit, and file output.
```

The agent should read `writer/SKILL.md` first and load only the references needed for the task:

- Complete article or reusable prompt: `writer/references/seo-article-template.md`
- SEO audit and optimization: `writer/references/seo-audit-checklist.md`
- Fact-heavy writing and comparisons: `writer/references/fact-check-and-style.md`
- Post-audit humanization: `writer/references/humanization.md`
- File and image packaging: `writer/references/output-packaging.md`
- Optional R2 upload: `writer/references/r2-image-upload.md`
- Credential safety: `writer/references/r2-security.md`

## Standard Workflow

1. Infer or create the article task card.
2. Generate and select the SEO title.
3. Build the outline and section notes.
4. Write the Markdown article.
5. Generate 16:9 images and insert local relative paths.
6. Verify current and high-risk claims.
7. Run the SEO audit and fix high-priority findings.
8. Humanize the corrected draft and run the post-humanization integrity check.
9. Save everything under `writer/output/<article-slug>/`.
10. Upload images only if valid local R2 configuration exists.
11. Re-audit changed sections and deliver exact file paths.

## Optional Cloudflare R2 Configuration

No cloud configuration is required. To enable R2 uploads:

```bash
cp writer/config/r2.config.example.json writer/config/r2.config.json
```

Fill in the ignored local file, then run:

```bash
node writer/scripts/upload-r2.mjs \
  --file writer/output/<article-slug>/hero-16x9.png \
  --article writer/output/<article-slug>/article.md \
  --manifest writer/output/<article-slug>/image-urls.json \
  --seoName "AI music detector hero" \
  --keyword "AI music detector" \
  --alt "AI music detector workflow hero image"
```

Behavior:

- Valid default config: compress and upload the image, update the article URL, and write `image-urls.json`.
- Missing default config: return `skipped: true` without compressing, uploading, or editing the article.
- Missing or invalid explicit `--config <path>`: fail with a clear configuration error.
- The original local image is always retained.

Use `--dryRun` before the first upload to preview the object key and public URL.

## Output Contract

A normal article package contains at least:

```text
writer/output/<article-slug>/article.md
writer/output/<article-slug>/hero-16x9.png
```

It may also contain `seo-audit.md`, section images, compressed `*-r2.webp` copies, and `image-urls.json` after successful uploads.

The article should use one H1, useful H2/H3 sections, an FAQ, a conclusion, and an SEO meta pack containing SEO Title, Excerpt, Meta Description, and Tags.

## Medium Writer

Use `writer/medium-writer/SKILL.md` for Medium posts, LinkedIn long-form articles, third-party reviews, opinion pieces, and content where narrative flow matters more than strict keyword placement.

## Security

- Never commit `writer/config/r2.config.json`.
- Never include R2 credentials in prompts, articles, audits, manifests, logs, screenshots, or final responses.
- Do not automatically search for or download remote credential files.
- Prefer a bucket-scoped R2 token with the minimum required permissions.
- Rotate credentials immediately if they appear in chat, Git history, logs, or screenshots.

## Related Skill Projects

- [Awesome Codex Skills](https://github.com/flaqai/awesome_codex_skills)
- [Awesome Claude Code Skills](https://github.com/flaqai/awesome_claude_code_skills)
- [SEO Audit Skill](https://github.com/JeffLi1993/seo-audit-skill)
- [Humanizer](https://github.com/blader/humanizer), which inspired the post-audit humanization pass

## License

See [LICENSE](./LICENSE).
