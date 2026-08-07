---
id: a69aaac121ccd00f
source: "laravel-seo-tools.md"
"title: Laravel SEO Tools"
category: seo
skillTags: []
containmentHash: c0293fff2a9b45276ca8
createdAt: 1786051357025
embeddingSig: "disc:integer:song|icalbum:song:music|integer:musician:profile|integer:song:track|music:song:song|musician:profile:release|profile:release:date|song:disc:integer|song:music:song|song:song:disc|song:track:integer|track:integer:musician"
---
icAlbum([
                'song' => 'music.song',
                'song:disc' => 'integer',
                'song:track' => 'integer',
                'musician' => 'profile',
                'release_date' => 'datetime'
            ]);
//music.playlist
        OpenGraph::setType('music.playlist')
            ->setMusicPlaylist([
                'song' => 'music.song',
                'song:disc' => 'integer',