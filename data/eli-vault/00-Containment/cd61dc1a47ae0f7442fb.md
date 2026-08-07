---
id: d5efd8a679b3fc1d
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["tool"]
containmentHash: cd61dc1a47ae0f7442fb
createdAt: 1786051357025
embeddingSig: "addproperty:type:articles|codecasts:lesson:seotools|current:seotools:setcanonical|http:current:seotools|https:codecasts:lesson|lesson:seotools:opengraph|opengraph:addproperty:type|opengraph:seturl:http|seotools:opengraph:addproperty|seotools:setcanonical:https|setcanonical:https:codecasts|seturl:http:current"
---
s::opengraph()->setUrl('http://current.url.com');
        SEOTools::setCanonical('https://codecasts.com.br/lesson');
        SEOTools::opengraph()->addProperty('type', 'articles');
        SEOTools::twitter()->setSite('@LuizVinicius73');
        SEOTools::jsonLd()->addImage('https://codecasts.com.br/img/logo.jpg');
$posts = Post::all();

        return view('myindex', compact('posts'));
    }