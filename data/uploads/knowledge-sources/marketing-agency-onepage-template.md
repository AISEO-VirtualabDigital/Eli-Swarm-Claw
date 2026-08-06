# Marketing Agency One-Page Template

**Source:** https://github.com/website-templates/marketing-agency_one-page-template
**Status:** ARCHIVED
**Author:** Maxim Orlov
**Based on:** Portfolio one page template
**Demo:** http://website-templates.github.io/marketing-agency_one-page-template/

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Template engine | Pug (Jade) |
| CSS preprocessor | Sass + Stylus |
| Build tool | Gulp 3.9 task runner |
| JS bundler | Rollup + Babel |
| Post-processing | PostCSS + Autoprefixer + CSSO (minification) |
| Dev server | BrowserSync with live reload |
| Image optimization | Gulp-imagemin |
| Sprite generation | gulp.spritesmith |
| HTML minification | gulp-htmlmin |
| JS minification | gulp-uglify |

## Page Sections (One-Page Layout)

1. **Home / Hero** — Full-width hero with CTA
2. **About** — Company description block
3. **Services** — 4-column service cards with icons
4. **Process / How It Works** — Step-by-step process section
5. **Projects / Portfolio** — Work showcase grid
6. **Testimonials** — Client testimonials carousel
7. **Our Team** — Team member cards with photos
8. **Contacts** — Contact form + info
9. **Multilingual** — English, French, German via Pug data files

## File Structure

```
dev/
├── pug/           # Templates (blocks/, helpers/, vendor/, layouts/, pages/)
├── sass/          # Styles (blocks/, helpers/, vendor/, custom.sass)
├── js/            # Scripts (vendor/, lib/, head.js, body.js)
├── images/        # Image sources
├── fonts/         # Font sources
├── data/          # Config and template data (i18n content)
└── helpers/       # favicon, .htaccess

build/             # Compiled output
├── index.html
└── static/
    ├── css/
    ├── js/
    ├── images/
    └── fonts/
```

## VirtuaLab Use Case

**NOT for the Next.js web app** — this is a static HTML/Gulp template.

**Potential use: GHL client landing pages or parasite SEO one-pagers.**
- The section structure (Hero → About → Services → Process → Projects → Testimonials → Team → Contact) maps well to local service business landing pages
- Pug templating makes it easy to generate variants programmatically via n8n
- Multilingual support (EN/FR/DE) is a bonus for multi-market parasite pages
- **However:** Gulp 3.9 is outdated, and the repo is archived — better to extract the section structure and rebuild in Next.js or plain HTML

## Assessment

- **Section structure:** Useful reference for local service business page layout
- **Code:** Too outdated (Gulp 3, Babel 7, no modern bundler) — do not use as-is
- **Verdict:** Absorb the layout pattern, not the code
