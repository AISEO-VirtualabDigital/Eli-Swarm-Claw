---
id: 396fb0a6f2309d6d
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["tool", "code"]
containmentHash: 6dedb40ed670ef8bfd14
createdAt: 1786051357025
embeddingSig: "artesaos:seotools:providers|bootstrap:file:this|class:lumen:bootstrap|config:return:providers|discovery:config:return|file:this:line|lumen:bootstrap:file|providers:artesaos:seotools|providers:seotoolsserviceprovider:class|return:providers:artesaos|seotools:providers:seotoolsserviceprovider|seotoolsserviceprovider:class:lumen"
---
age-discovery).
> `config/app.php`

```php
<?php

return [
    // ...
    'providers' => [
        Artesaos\SEOTools\Providers\SEOToolsServiceProvider::class,
        // ...
    ],
    // ...
];
```
#### Lumen

Go to `/bootstrap/app.php` file and add this line:

```php
<?php
// ...

$app = new Laravel\Lumen\Application(
    dirname(__DIR__)
);
// ...