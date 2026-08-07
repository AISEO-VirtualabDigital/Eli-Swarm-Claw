---
id: 7b85633a5f1f8f5c
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["capability", "tool", "code"]
containmentHash: bcfc93a9b1aefa6d8712
createdAt: 1786051357025
embeddingSig: "artesaos:seotools:facades|facades:jsonld:artesaos|facades:jsonldmulti:artesaos|facades:twittercard:artesaos|graph:artesaos:seotools|jsonld:artesaos:seotools|jsonldmulti:artesaos:seotools|seotools:facades:jsonld|seotools:facades:jsonldmulti|seotools:facades:seotools|seotools:facades:twittercard|twittercard:artesaos:seotools"
---
Graph`
 - `Artesaos\SEOTools\Facades\TwitterCard`
 - `Artesaos\SEOTools\Facades\JsonLd`
 - `Artesaos\SEOTools\Facades\JsonLdMulti`
 - `Artesaos\SEOTools\Facades\SEOTools`
You can setup a short-version aliases for these facades in your `config/app.php` file. For example:

```php
<?php
return [
    // ...
    'aliases' => [
        'SEOMeta'       => Artesaos\SEOTools\Facades\SEOMeta::class,