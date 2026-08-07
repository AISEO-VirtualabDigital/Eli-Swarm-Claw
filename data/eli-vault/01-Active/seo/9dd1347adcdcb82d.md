---
id: 9dd1347adcdcb82d
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["tool", "code"]
containmentHash: 451875726c855252693a
createdAt: 1786051357025
embeddingSig: "application:dirname:register|artesaos:seotools:providers|class:return:facades|dirname:register:artesaos|facades:note:facades|note:facades:supported|providers:seotoolsserviceprovider:class|register:artesaos:seotools|return:facades:note|seotools:providers:seotoolsserviceprovider|seotoolsserviceprovider:class:return|umen:application:dirname"
---
umen\Application(
    dirname(__DIR__)
);
// ...

$app->register(Artesaos\SEOTools\Providers\SEOToolsServiceProvider::class);

// ...

return $app;
```
### 3 - Facades

> Note: facades are not supported in Lumen.

You may get access to the SEO tool services using following facades:
- `Artesaos\SEOTools\Facades\SEOMeta`
 - `Artesaos\SEOTools\Facades\OpenGraph`
 - `Artesaos\SEOTools\Facades\TwitterCard`