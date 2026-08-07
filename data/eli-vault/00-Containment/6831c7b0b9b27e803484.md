---
id: e51a5afb3829eadd
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: ["tool"]
containmentHash: 6831c7b0b9b27e803484
createdAt: 1786051357025
embeddingSig: "description:jsonld:addimage|homepage:jsonld:setdescription|jsonld:addimage:https|jsonld:setdescription:this|jsonld:settitle:homepage|luizvinicius73:jsonld:settitle|page:description:jsonld|setdescription:this:page|setsite:luizvinicius73:jsonld|settitle:homepage:jsonld|this:page:description|twittercard:setsite:luizvinicius73"
---
TwitterCard::setSite('@LuizVinicius73');

        JsonLd::setTitle('Homepage');
        JsonLd::setDescription('This is my page description');
        JsonLd::addImage('https://codecasts.com.br/img/logo.jpg');
// OR

        SEOTools::setTitle('Home');
        SEOTools::setDescription('This is my page description');
        SEOTools::opengraph()->setUrl('http://current.url.com');