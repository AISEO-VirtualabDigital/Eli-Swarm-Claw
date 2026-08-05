# SEO Tools Collection — Yoast, Ether SEO, Google Indexing Script, OpenSEO

## Yoast/wordpress-seo

**URL**: https://github.com/Yoast/wordpress-seo

# Yoast SEO












## Welcome to the Yoast SEO GitHub repository


While the documentation for the [Yoast SEO plugin](https://yoa.st/1ul) can be found on [Yoast.com](https://yoa.st/1um), here
you can browse the source of the project, find and discuss open issues and even
[contribute yourself](.github/CONTRIBUTING.md).

## Installation

Here's a [guide on how to install Yoast SEO in your WordPress site](https://yoa.st/1un).

## Want to contribute to Yoast SEO?

### Prerequisites

At Yoast, we make use a specific toolset to develop our code. Please ensure you have the following tools installed before contributing.

* [Composer](https://getcomposer.org/)
* [Yarn](https://yarnpkg.com/en/)
* [Grunt](https://gruntjs.com/)

### Getting started
After installing the aforementioned tools, you can use the steps below to acquire a development version of Yoast SEO.
Please note that this will download the latest development version of Yoast SEO. While this version is usually stable,
it is not recommended for use in a production environment.

Within your WordPress installation, navigate to `wp-content/plugins` and run the following commands:
```bash
git clone https://github.com/Yoast/wordpress-seo.git
cd wordpress-seo
```

To install all the necessary dependencies, run the following commands:
```bash
composer install
yarn
grunt build
```

During development, you could run `grunt build:dev` instead of `grunt build`, to save yourself downloading some dependencies that are only needed for a production environment.

Please note that if you change anything in the JavaScript or CSS, you'll have to run `grunt build:js` or `grunt build:css`, respectively.

For active development, you could run `grunt watch` to keep the build up-to-date and run checks right away.

For JavaScript only, you start a Webpack watch by running `yarn start`, this command will keep the JS files up-to-date. You'll have to refresh the page yourself.
When working in other folders than `packages/js`, you can refer to their individual readme or package.json scripts. If the package offers a watch, you still have to build the plugin afterwards.

For example, the `packages/ui-library` package has its own `yarn watch` (and js/css) commands. You can either `cd` into that folder or target it from the root using the workspace command:
```bash
yarn workspace @yoast/ui-library watch:js
```
or using Lerna:
```bash
yarn lerna run watch:js --scope @yoast/ui-library --stream
```

This repository uses [the Yoast grunt tasks plugin](https://github.com/Yoast/plugin-grunt-tasks).

## Testing packages

To run tests for js packages, run the following command from the root of the repository:
```bash
yarn test
```

## Support

This is a developer's portal for Yoast SEO and should not be used for support. Please visit the
[support forums](https://wordpress.org/support/plugin/wordpress-seo).

## Reporting bugs

If you find an issue, [let us know here](https://github.com/yoast/wordpress-seo/issues/new)! Please follow [these guidelines](https://yoa.st/1uo) on how to write a good bug report.

It may help us a lot if you can provide a backtrace of the error encountered. You can use [code in this gist](https://gist.github.com/jrfnl/5925642) to enable the backtrace in your website's configuration.

## Contributions

Anyone is welcome to contribute to Yoast SEO. Please
[read the guidelines](.github/CONTRIBUTING.md) for contributing to this
repository.

There are various ways you can contribute:

* [Raise an issue](https://github.com/yoast/wordpress-seo/issues) on GitHub.
* Send us a Pull Request with your bug fixes and/or new features.
* [Translate Yoast SEO into different languages](http://translate.yoast.com/projects/wordpress-seo/).
* Provide feedback and [suggestions on enhancements](https://github.com/yoast/wordpress-seo/issues?direction=desc&labels=Enhancement&page=1&sort=created&state=open).

---

## ethercreative/seo

**URL**: https://github.com/ethercreative/seo

![SEO for Craft CMS](resources/imgs/banner.jpg)

# SEO for Craft CMS

SEO for Craft does three things that will help your sites SEO, and does them really damn well:

1. [**Optimisation Field Type**](#the-field-type) - Helps your clients write better optimised copy, and manage other SEO meta.
2. [**Sitemap**](#the-sitemap) - Generates an always up-to-date XML sitemap automatically, with controls for customisation.
3. [**Redirects**](#the-redirects) - Quickly and easily manage 301 & 302 redirects. Especially useful when migrating from an old site.

[Click here for the **Craft 2** version.](https://github.com/ethercreative/seo/tree/v2)

### The Field Type

The SEO field type helps give users an idea of how their page will look in Google, and how their pages content scores when compared to a specific keyword.

The field type allows users to manage the meta of their page in one simple and easy to use input that has the added bonus of giving them an idea of how their page will show up in a Google search.

The field also contains a *Focus Keyword* input and *Page Score*. This is used to workout how relevant a keyword or phrase is to your entry and how well the page is likely to do in a search for that keyword.

The Page Score also contains a breakdown of your entries score, and tips on where it can be improved.

![SEO for Craft CMS](resources/imgs/fieldtype.jpg)

![SEO Social](resources/imgs/fieldtype-social.jpg)

![SEO Advanced](resources/imgs/fieldtype-advanced.jpg)

### The Sitemap

SEO for Craft boasts an extremely powerful, yet simple to use Sitemap manager. With automatic support for all your site’s sections and categories (with localisations taken into account), and the ability to easily add custom URLs (useful for public templates that aren’t content managed), keeping your sitemap up-to-date has never been easier.

With SEO for Craft’s sitemap manager you have complete control over what content you want to have appear on your sitemap as well as managing its change frequency and priority in your site.

![SEO Sitemap](resources/imgs/sitemap.jpg)

### The Redirects

When moving from your old, awful site to your shiny new Craft one, you’ll want to make sure that all your old pages are redirected to their new counterparts. Redirects are easy to manage with SEO for Craft.

SEO for Crafts redirect manager lets you easily add 301 & 302 redirects, with full .htaccess style regex support!

Redirects support [PCRE regex syntax](http://php.net/manual/en/reference.pcre.pattern.syntax.php). By default, all `/` and `?` not inside parenthesis are escaped. To prevent any escaping include the opening and closing forward slashes and flags: `/^blog$/i`. All redirects are given the insensitive flag, unless overwritten.

**Redirect Regex Example**  
To redirect from `blog/2016/my-post` to `news/my-post` you would add the following redirect:

URI: `blog/([0-9]{4})/(.*)` To: `news/$2`

![SEO Redirects](resources/imgs/redirects.jpg)

## Installation & Usage

Clone this repo into `craft/plugins/seo`.

### Using Composer

**Easy way**

`composer require ether/seo`

**Alternative way**
1. Append `"ether/seo": "^3.1.0"` to the `require` hash of `composer.json`
2. `composer update`
3. Install via CP in `/admin/settings/plugins`

Before using the SEO field type, you’ll need to ensure all the settings are correct. You can find the settings under the SEO plugin menu in the sidebar, or via the plugin menu.

### Environment Setup

Ensure that your Production environment’s name is `production` (going with Craft’s convention). All other environments will get `X-Robots-Tag: none, noimageindex` headers added to every web response, to prevent search engines from indexing duplicate content.

Environment names are typically defined by an `ENVIRONMENT` environment variable.

### Fieldtype Usage

Replace your `title` tag, and any other SEO related meta tags with `{% hook "seo" %}`. That's it!

This assumes that you will be creating a variable call `seo` in your templates that will return either the SEO field or a custom SEO object (see below). You can modify the output of this hook by setting your own SEO Meta Template in the SEO Settings. You can [view the default template here](https://github.com/ethercreative/seo/blob/v3/src/templates/_seo/meta.twig).

### How meta output works (what the hook renders)

- **Automatic field detection**: The default meta template will try to find your SEO field automatically using `getSeoField('seo')`. If your field handle is not `seo`, pass it: `getSeoField('mySeoHandle')`. If nothing is found, it falls back to `craft.seo.custom(siteName, '')`.
- **Meta tags included**:
  - `<title>` from your SEO field’s title tokens or fallback
  - `<meta name="description">`
  - Open Graph tags (title, description, image, site name, locale, alternates)
  - Twitter Card tags (summary_large_image)
  - `<meta name="robots">` when applicable (see Robots section below)
  - `<link rel="canonical">`
- **Canonical also as a header**: In addition to the `<link rel="canonical">`, the plugin adds an HTTP `Link: <...>; rel="canonical"` header on every frontend response.

Tip: If you prefer to use an SEO object directly (e.g. for non-element templates), set a variable named `seo` in your template to `craft.seo.custom(...)` or include your element’s field value, and the hook will use it.

### Custom SEO Object

In some cases, you will not have access to an SEO field, but will want to set the page title, description, & socials. You can do this by creating a custom SEO object using the function below:

```twig
craft.seo.custom(
    'The Page Title',
    'The page description',
    null,

    // Social media - Any missing fields (excluding images) will be populated by the values above
    {
        twitter: { image: myImageField.first() },
        facebook: { title: '', description: '', image: myImageField.first() },
    }
)
```

alternatively pass an object as the first parameter. This will be used in place of an element.

`

---

## goenning/google-indexing-script

**URL**: https://github.com/goenning/google-indexing-script

# Google Indexing Script

Use this script to get your entire site indexed on Google in less than 48 hours. No tricks, no hacks, just a simple script and a Google API.

> [!IMPORTANT]
>
> 1. This script uses [Google Indexing API](https://developers.google.com/search/apis/indexing-api/v3/quickstart) and it only works on pages with either `JobPosting` or `BroadcastEvent` structured data.
> 2. Indexing != Ranking. This will not help your page rank on Google, it'll just let Google know about the existence of your pages.

## Requirements

- Install [Node.js](https://nodejs.org/en/download)
- An account on [Google Search Console](https://search.google.com/search-console/about) with the verified sites you want to index
- An account on [Google Cloud](https://console.cloud.google.com/)

## Preparation

1. Follow this [guide](https://developers.google.com/search/apis/indexing-api/v3/prereqs) from Google. By the end of it, you should have a project on Google Cloud with the Indexing API enabled, a service account with the `Owner` permission on your sites.
2. Make sure you enable both [`Google Search Console API`](https://console.cloud.google.com/apis/api/searchconsole.googleapis.com) and [`Web Search Indexing API`](https://console.cloud.google.com/apis/api/indexing.googleapis.com) on your [Google Project ➤ API Services ➤ Enabled API & Services](https://console.cloud.google.com/apis/dashboard).
3. [Download the JSON](https://github.com/goenning/google-indexing-script/issues/2) file with the credentials of your service account and save it in the same folder as the script. The file should be named `service_account.json`

## Installation

### Using CLI

Install the cli globally on your machine.

```bash
npm i -g google-indexing-script
```

### Using the repository

Clone the repository to your machine.

```bash
git clone https://github.com/goenning/google-indexing-script.git
cd google-indexing-script
```

Install and build the project.

```bash
npm install
npm run build
npm i -g .
```

> [!NOTE]
> Ensure you are using an up-to-date Node.js version, with a preference for v20 or later. Check your current version with `node -v`.

## Usage

<details open>
<summary>With <code>service_account.json</code> <i>(recommended)</i></summary>

Create a `.gis` directory in your home folder and move the `service_account.json` file there.

```bash
mkdir ~/.gis
mv service_account.json ~/.gis
```

Run the script with the domain or url you want to index.

```bash
gis <domain or url>
# example
gis seogets.com
```

Here are some other ways to run the script:

```bash
# custom path to service_account.json
gis seogets.com --path /path/to/service_account.json
# long version command
google-indexing-script seogets.com
# cloned repository
npm run index seogets.com
```

</details>

<details>
<summary>With environment variables</summary>

Open `service_account.json` and copy the `client_email` and `private_key` values.

Run the script with the domain or url you want to index.

```bash
GIS_CLIENT_EMAIL=your-client-email GIS_PRIVATE_KEY=your-private-key gis seogets.com
```

</details>

<details>
<summary>With arguments <i>(not recommended)</i></summary>

Open `service_account.json` and copy the `client_email` and `private_key` values.

Once you have the values, run the script with the domain or url you want to index, the client email and the private key.

```bash
gis seogets.com --client-email your-client-email --private-key your-private-key
```

</details>

<details>
<summary>As a npm module</summary>

You can also use the script as a [npm module](https://www.npmjs.com/package/google-indexing-script) in your own project.

```bash
npm i google-indexing-script
```

```javascript
import { index } from "google-indexing-script";
import serviceAccount from "./service_account.json";

index("seogets.com", {
  client_email: serviceAccount.client_email,
  private_key: serviceAccount.private_key,
})
  .then(console.log)
  .catch(console.error);
```

Read the [API documentation](https://jsdocs.io/package/google-indexing-script) for more details.

</details>

Here's an example of what you should expect:

![](./output.png)

> [!IMPORTANT]
>
> - Your site must have 1 or more sitemaps submitted to Google Search Console. Otherwise, the script will not be able to find the pages to index.
> - You can run the script as many times as you want. It will only index the pages that are not already indexed.
> - Sites with a large number of pages might take a while to index, be patient.

## Quota

Depending on your account several quotas are configured for the API (see [docs](https://developers.google.com/search/apis/indexing-api/v3/quota-pricing#quota)). By default the script exits as soon as the rate limit is exceeded. You can configure a retry mechanism for the read requests that apply on a per minute time frame.

<details>
<summary>With environment variables</summary>

```bash
export GIS_QUOTA_RPM_RETRY=true
```

</details>

<details>
<summary>As a npm module</summary>

```javascript
import { index } from 'google-indexing-script'
import serviceAccount from './service_account.json'

index('seogets.com', {
  client_email: serviceAccount.client_email,
  private_key: serviceAccount.private_key
  quota: {
    rpmRetry: true
  }
})
  .then(console.log)
  .catch(console.error)
```

</details>

## 📄 License

MIT License

## 💖 Sponsor

This project is sponsored by [SEO Gets](https://seogets.com)

![](https://seogets.com/og.png)

---

## every-app/open-seo

**URL**: https://github.com/every-app/open-seo

# OpenSEO

> Open source alternative to Semrush and Ahrefs

OpenSEO is an SEO tool for _the people_. If tools like Semrush or Ahrefs are too expensive or bloated, OpenSEO is a pay-as-you-go alternative that you actually control.

> All-in-one SEO tool for you and your AI agent.

Connect with any agent like Claude Code, OpenClaw or Hermes. We have pre-built skills, but you can build your own to tailor OpenSEO to your needs.



## Hosted Version

Try OpenSEO for free on our website. If you want to support the project, a hosted subscription is $10/month.

[openseo.so](https://openseo.so)

## Why use OpenSEO?

- Best in class MCP and AI Skills.
- Modern, simple UI.
  - Focused workflows instead of a bloated, complex SEO suite.
- No subscriptions.
  - Bring your own DataForSEO API key and pay only for what you use.
- Fork and vibe code your own custom tool.

## Main SEO Workflows

- Keyword research
- Rank tracking
- Competitor Insights
- Backlinks
- Site Audits
- AI Visibility

## OpenSEO MCP & Agent Skills

OpenSEO exposes an MCP server so AI agents like Claude Code, OpenClaw, and Hermes can use your SEO data directly. Agent Skills are reusable workflows that guide your agent through SEO tasks using the MCP.

- [Set up OpenSEO MCP](https://openseo.so/docs/mcp)
- [Set up OpenSEO Agent Skills](https://openseo.so/docs/skills/setup)

## Self-Hosting

OpenSEO supports two self-hosting paths:

- **Simple: Docker** for personal use on your own machine (recommended for getting started). See [`docs/SELF_HOSTING_DOCKER.md`](./docs/SELF_HOSTING_DOCKER.md).
- **Advanced: Cloudflare** for internet-facing self-hosting across multiple devices or with your team (works on the free plan). See [`docs/SELF_HOSTING_CLOUDFLARE.md`](./docs/SELF_HOSTING_CLOUDFLARE.md).

Either way, you need a DataForSEO API key to get SEO data. See [`docs/DATAFORSEO_API_KEY.md`](./docs/DATAFORSEO_API_KEY.md).

## Costs

OpenSEO needs a [DataForSEO](https://dataforseo.com/?aff=255379) API key so that you can get SEO data. You pay them directly when self hosting.

See [openseo.so/pricing](https://openseo.so/pricing)

When you self host, your costs will be slightly lower than the estimates on our website. The way the hosted service makes money is by charging 28% extra for every request we make to DataForSEO.

## Local Development

See [`docs/LOCAL_DEVELOPMENT.md`](./docs/LOCAL_DEVELOPMENT.md).

## Contributing

Contributions are very welcome. See [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md).

## Community

Join Discord to chat: [Discord](https://discord.gg/c9uGs3cFXr)

Follow along for updates:

- Follow on X: https://x.com/bensenescu
- Sign up for the mailing list on our website: [openseo.so](https://openseo.so)

---

