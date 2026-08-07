---
id: 8084ff071069ba09
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: []
containmentHash: b6f94d18eaea5fbed4cd
createdAt: 1786051357025
embeddingSig: "first:name:string|last:name:string|name:string:last|name:string:username|person:settype:profile|profile:setprofile:first|setdescription:some:person|setprofile:first:name|settype:profile:setprofile|some:person:settype|string:last:name|string:username:string"
---
le')
             ->setDescription('Some Person')
            ->setType('profile')
            ->setProfile([
                'first_name' => 'string',
                'last_name' => 'string',
                'username' => 'string',
                'gender' => 'enum(male, female)'
            ]);
// Namespace URI: http://ogp.me/ns/music#
        // music.song
        OpenGraph::setType('music.song')