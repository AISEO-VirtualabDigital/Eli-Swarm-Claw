---
id: dcba38a6646e637e
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: []
containmentHash: da17afd979ef89f18bfd
createdAt: 1786051357025
embeddingSig: "addkeyword:key1:key2|article:section:post|category:property:seometa|key1:key2:key3|key2:key3:opengraph|key3:opengraph:setdescription|opengraph:setdescription:post|post:category:property|property:seometa:addkeyword|section:post:category|seometa:addkeyword:key1|setdescription:post:resume"
---
('article:section', $post->category, 'property');
        SEOMeta::addKeyword(['key1', 'key2', 'key3']);
OpenGraph::setDescription($post->resume);
        OpenGraph::setTitle($post->title);
        OpenGraph::setUrl('http://current.url.com');
        OpenGraph::addProperty('type', 'article');
        OpenGraph::addProperty('locale', 'pt-br');