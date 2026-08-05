# Image SEO — Complete Reference

Source: https://github.com/search?q=image+seo&type=repositories

## Core Image SEO Factors

### File Name Optimization
- Use descriptive, keyword-rich file names (e.g., `blue-widget-dallas-tx.jpg` not `IMG_3847.jpg`)
- Use hyphens, not underscores, as word separators
- Keep file names concise but descriptive (3-5 words)
- Include primary keyword and geo-modifier when relevant

### Alt Text Best Practices
- Write descriptive alt text for every image (125-250 characters max)
- Include primary keyword naturally in alt text
- Describe what is actually in the image, not what the page is about
- For decorative images, use empty alt attribute `alt=""`
- Avoid keyword stuffing in alt text
- Test alt text by closing your eyes and imagining the image from the description

### Image Format Selection
- **JPEG**: Photographs, complex images with many colors (use quality 80-85)
- **PNG**: Screenshots, logos, images needing transparency, text overlays
- **WebP**: Modern format with 25-35% smaller file sizes than JPEG (serve with fallback)
- **AVIF**: Next-gen format with even better compression than WebP
- **SVG**: Icons, logos, simple graphics (infinitely scalable, tiny file size)

### Technical Image Optimization
- Compress all images before upload (tools: Squoosh, TinyPNG, ImageOptim)
- Use responsive images with `srcset` and `sizes` attributes
- Implement lazy loading with `loading="lazy"` for below-fold images
- Set explicit `width` and `height` to prevent Cumulative Layout Shift (CLS)
- Use CDN for image delivery
- Implement HTTP/2 server push for critical images
- Consider progressive JPEGs for better perceived loading performance

### Structured Data for Images
- Use `ImageObject` schema markup for important images
- Include `caption`, `creditText`, and `contentUrl`
- Implement `logo` and `image` fields in Organization/WebSite schema
- Use `itemListElement` for image galleries

### Google Image Search Optimization
- Add structured data to enable badges (recipe, product, video)
- Use `max-image-preview:large` robots meta tag
- Ensure images are crawlable (not blocked by robots.txt)
- Submit image sitemaps with `image:image`, `image:loc`, `image:caption`, `image:title`
- Use WebP in image sitemaps with `<image:caption>` descriptions
- Implement AMP for image-heavy pages (where applicable)
- Use `data-src` attributes carefully — Google may not crawl JavaScript-loaded images

### Image Sitemaps
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://example.com/page.html</loc>
    <image:image>
      <image:loc>https://example.com/image.jpg</image:loc>
      <image:title>Descriptive Title</image:title>
      <image:caption>What the image shows</image:caption>
    </image:image>
  </url>
</urlset>
```

### Core Web Vitals & Images
- **LCP (Largest Contentful Paint)**: Often an image — optimize hero images aggressively
- **CLS (Cumulative Layout Shift)**: Set width/height on all images to prevent layout shift
- **INP (Interaction to Next Paint)**: Avoid heavy image decoding blocking main thread

### Tools for Image SEO
- **Squoosh** (Google): Browser-based image compression
- **TinyPNG**: Smart lossy compression
- **ImageOptim**: Mac app for bulk image optimization
- **Cloudinary**: Automated image transformation and CDN delivery
- **Imgix**: Real-time image manipulation and optimization
- **Google PageSpeed Insights**: Check image performance impact
- **Screaming Frog**: Audit image SEO issues at scale
- **Ahrefs Site Audit**: Image SEO health check

### Image SEO for E-Commerce
- Use high-quality product images (minimum 1000px on longest side)
- Include multiple angles and lifestyle shots
- Add zoom functionality for product images
- Implement product schema with `image` arrays
- Use consistent naming conventions across product catalogs
- Optimize for Google Shopping image requirements
