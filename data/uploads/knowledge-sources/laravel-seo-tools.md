# Laravel SEO Tools

**Repository**: [artesaos/seotools](https://github.com/artesaos/seotools)

<p align="center">
    <a href="https://github.com/artesaos" target="_blank">
        
    </a>
    <h1 align="center">SEOTools - SEO Tools for Laravel and Lumen</h1>
    <br>
</p>

SEOTools is a package for [Laravel 5.8+](https://laravel.com/) and [Lumen](https://lumen.laravel.com/) that provides helpers for some common SEO techniques.

> Current Build Status




> Statistics

   

For license information check the [LICENSE](LICENSE.md)-file.

Features
--------

- Friendly simple interface
- Easy of set titles and meta tags
- Easy of set metas for [Twitter Cards](https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/abouts-cards) and [Open Graph](https://ogp.me/)
- Easy of set for [JSON Linked Data](https://json-ld.org/)

Installation
------------

### 1 - Dependency

The first step is using composer to install the package and automatically update your `composer.json` file, you can do this by running:

```shell
composer require artesaos/seotools
```

> **Note**: If you are using Laravel 5.5, the steps 2 and 3, for providers and aliases, are unnecessaries. SEOTools supports Laravel new [Package Discovery](https://laravel.com/docs/5.5/packages#package-discovery).

### 2 - Provider

You need to update your application configuration in order to register the package so it can be loaded by Laravel, just update your `config/app.php` file adding the following code at the end of your `'providers'` section:

> **Note**: If you are using Laravel 11+, you will have to update `bootstrap/providers.php` instead. [Package Discovery](https://laravel.com/docs/12.x/packages#package-discovery).

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
        'OpenGraph'     => Artesaos\SEOTools\Facades\OpenGraph::class,
        'Twitter'       => Artesaos\SEOTools\Facades\TwitterCard::class,
        'JsonLd'        => Artesaos\SEOTools\Facades\JsonLd::class,
        'JsonLdMulti'   => Artesaos\SEOTools\Facades\JsonLdMulti::class,
        // or
        'SEO' => Artesaos\SEOTools\Facades\SEOTools::class,
        // ...
    ],
    // ...
];
```

### 4 Configuration

#### Publish config

In your terminal type

```shell
php artisan vendor:publish
```

or

```shell
php artisan vendor:publish --provider="Artesaos\SEOTools\Providers\SEOToolsServiceProvider"
```

> Lumen does not support this command, for it you should copy the file `src/resources/config/seotools.php` to `config/seotools.php` of your project

In `seotools.php` configuration file you can determine the properties of the default values and some behaviors.

#### seotools.php

- **meta**
   - `defaults` - What values are displayed if not specified any value for the page display. If the value is `false`, nothing is displayed.
   - `webmaster` - Are the settings of tags values for major webmaster tools. If you are `null` nothing is displayed.
- **opengraph**
   - `defaults` - Are the properties that will always be displayed and when no other value is set instead. **You can add additional tags** that are not included in the original configuration file.
- **twitter**
   - `defaults` - Are the properties that will always be displayed and when no other value is set instead. **You can add additional tags** that are not included in the original configuration file.
- **json-ld**
   - `defaults` - Are the properties that will always be displayed and when no other value is set instead. **You can add additional tags** that are not included in the original configuration file.

Usage
-----

### Lumen Usage

> Note: facades are not supported in Lumen.

```php
<?php

$seotools = app('seotools');
$metatags = app('seotools.metatags');
$twitter = app('seotools.twitter');
$opengraph = app('seotools.opengraph');
$jsonld = app('seotools.json-ld');
$jsonldMulti = app('seotools.json-ld-multi');

// The behavior is the same as the facade

echo app('seotools')->generate();
```

### Meta tags Generator

With **SEOMeta** you can create meta tags to the `head`

### Opengraph tags Generator

With **OpenGraph** you can create OpenGraph tags to the `head`

### Twitter for Twitter Cards tags Generator

With **Twitter** you can create OpenGraph tags to the `head`

#### In your controller

```php
<?php

namespace App\Http\Controllers;

use Artesaos\SEOTools\Facades\SEOMeta;
use Artesaos\SEOTools\Facades\OpenGraph;
use Artesaos\SEOTools\Facades\TwitterCard;
use Artesaos\SEOTools\Facades\JsonLd;
// OR with multi
use Artesaos\SEOTools\Facades\JsonLdMulti;

// OR
use Artesaos\SEOTools\Facades\SEOTools;

class CommonController extends Controller
{
    public function index()
    {
        SEOMeta::setTitle('Home');
        SEOMeta::setDescription('This is my page description');
        SEOMeta::setCanonical('https://codecasts.com.br/lesson');

        OpenGraph::setDescription('This is my page description');
        OpenGraph::setTitle('Home');
        OpenGraph::setUrl('http://current.url.com');
        OpenGraph::addProperty('type', 'articles');

        TwitterCard::setTitle('Homepage');
        TwitterCard::setSite('@LuizVinicius73');

        JsonLd::setTitle('Homepage');
        JsonLd::setDescription('This is my page description');
        JsonLd::addImage('https://codecasts.com.br/img/logo.jpg');

        // OR

        SEOTools::setTitle('Home');
        SEOTools::setDescription('This is my page description');
        SEOTools::opengraph()->setUrl('http://current.url.com');
        SEOTools::setCanonical('https://codecasts.com.br/lesson');
        SEOTools::opengraph()->addProperty('type', 'articles');
        SEOTools::twitter()->setSite('@LuizVinicius73');
        SEOTools::jsonLd()->addImage('https://codecasts.com.br/img/logo.jpg');

        $posts = Post::all();

        return view('myindex', compact('posts'));
    }

    public function show($id)
    {
        $post = Post::find($id);

        SEOMeta::setTitle($post->title);
        SEOMeta::setDescription($post->resume);
        SEOMeta::addMeta('article:published_time', $post->published_date->toW3CString(), 'property');
        SEOMeta::addMeta('article:section', $post->category, 'property');
        SEOMeta::addKeyword(['key1', 'key2', 'key3']);

        OpenGraph::setDescription($post->resume);
        OpenGraph::setTitle($post->title);
        OpenGraph::setUrl('http://current.url.com');
        OpenGraph::addProperty('type', 'article');
        OpenGraph::addProperty('locale', 'pt-br');
        OpenGraph::addProperty('locale:alternate', ['pt-pt', 'en-us']);

        OpenGraph::addImage($post->cover->url);
        OpenGraph::addImage($post->images->list('url'));
        OpenGraph::addImage(['url' => 'http://image.url.com/cover.jpg', 'size' => 300]);
        OpenGraph::addImage('http://image.url.com/cover.jpg', ['height' => 300, 'width' => 300]);

        JsonLd::setTitle($post->title);
        JsonLd::setDescription($post->resume);
        JsonLd::setType('Article');
        JsonLd::addImage($post->images->list('url'));

        // OR with multi

        JsonLdMulti::setTitle($post->title);
        JsonLdMulti::setDescription($post->resume);
        JsonLdMulti::setType('Article');
        JsonLdMulti::addImage($post->images->list('url'));
        if(! JsonLdMulti::isEmpty()) {
            JsonLdMulti::newJsonLd();
            JsonLdMulti::setType('WebPage');
            JsonLdMulti::setTitle('Page Article - '.$post->title);
        }

        // Namespace URI: http://ogp.me/ns/article#
        // article
        OpenGraph::setTitle('Article')
            ->setDescription('Some Article')
            ->setType('article')
            ->setArticle([
                'published_time' => 'datetime',
                'modified_time' => 'datetime',
                'expiration_time' => 'datetime',
                'author' => 'profile / array',
                'section' => 'string',
                'tag' => 'string / array'
            ]);

        // Namespace URI: http://ogp.me/ns/book#
        // book
        OpenGraph::setTitle('Book')
            ->setDescription('Some Book')
            ->setType('book')
            ->setBook([
                'author' => 'profile / array',
                'isbn' => 'string',
                'release_date' => 'datetime',
                'tag' => 'string / array'
            ]);

        // Namespace URI: http://ogp.me/ns/profile#
        // profile
        OpenGraph::setTitle('Profile')
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
            ->setMusicSong([
                'duration' => 'integer',
                'album' => 'array',
                'album:disc' => 'integer',
                'album:track' => 'integer',
                'musician' => 'array'
            ]);

        // music.album
        OpenGraph::setType('music.album')
            ->setMusicAlbum([
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
                'song:track' => 'integer',
                'creator' => 'profile'
            ]);

        // music.radio_station
        OpenGraph::setType('music.radio_station')
            ->setMusicRadioStation([
                'creator' => 'profile'
            ]);

        // Namespace URI: http://ogp.me/ns/video#
        // video.movie
        OpenGraph::setType('video.movie')
            ->setVideoMovie([
                'actor' => 'profile / array',
                'actor:role' => 'string',
                'director' => 'profile /array',
                'writer' => 'profile / array',
                'duration' => 'integer',
                'release_date' => 'datetime',
                'tag' => 'string / array'
            ]);

        // video.episode
        OpenGraph::setType('video.episode')
            ->setVideoEpisode([
                'actor' => 'profile / array',
                'actor:role' => 'string',
                'director' => 'profile /array',
                'writer' => 'profile / array',
                'duration' => 'integer',
                'release_date' => 'datetime',
                'tag' => 'string / array',
                'series' => 'video.tv_show'
            ]);

        // video.tv_show
        OpenGraph::setType('video.tv_show')
            ->setVideoTVShow([
                'actor' => 'profile / array',
                'actor:role' => 'string',
                'director' => 'profile /array',
                'writer' => 'pr