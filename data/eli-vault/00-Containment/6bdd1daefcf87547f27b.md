---
id: 715353f251c4d954
source: "seo-tools-yoast-ether-indexing-openseo.md"
"title: SEO Tools Collection — Yoast, Ether SEO, Google Indexing Script, OpenSEO"
category: seo
skillTags: ["capability", "code"]
containmentHash: 6bdd1daefcf87547f27b
createdAt: 1786051359101
embeddingSig: "below:twig:craft|creating:custom:object|custom:object:using|description:socials:this|function:below:twig|object:using:function|page:title:description|socials:this:creating|this:creating:custom|title:description:socials|twig:craft:custom|using:function:below"
---
nt to set the page title, description, & socials. You can do this by creating a custom SEO object using the function below:
```twig
craft.seo.custom(
    'The Page Title',
    'The page description',
    null,

    // Social media - Any missing fields (excluding images) will be populated by the values above
    {
        twitter: { image: myImageField.first() },