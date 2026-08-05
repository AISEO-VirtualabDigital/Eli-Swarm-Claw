# Next SEO — SEO Plugin for Next.js

**Repository**: [garmeeh/next-seo](https://github.com/garmeeh/next-seo)

## Key Features

Next SEO is a plug-in that makes managing SEO in Next.js projects easier.

### ArticleJsonLd

ArticleJsonLd } from "next-seo";

export default function BlogPost() {
  return (
    <>
      <ArticleJsonLd
        headline="Getting Started with Next SEO"
        datePublished="2024-01-01T08:00:00+00:00"
        author="John Doe"
        image="https://example.com/article-image.jpg"
        description="Learn how to improve your Next.js SEO"
      />
      <article>
        <h1>Getting Started with Next SEO</h1>
        {/* Your content */}
      </article>
    </>
  );
}
```

> **Note**: For standard meta tags (`<meta>`, `<title>`), use Next.js's built-in [`generateMetadata`](https://nextjs.org/docs/app/api-reference/functions/generate-metadata) function.

> **Pages Router Support**: If you're using Next.js Pages Router, import components from `next-seo/pages`. See the [Pages Router documentation](./src/pages/README.md) for details.

### Content Security Policy (CSP)

Every JSON-LD component renders an inline `<script type="application/ld+json">` tag. If your site sends a strict CSP header such as `script-src 'nonce-{RANDOM}'`, that inline script is blocked unless it carries a matching nonce.

All JSON-LD components accept an optional `nonce` prop, which is rendered as the `nonce` attribute on the script tag:

```tsx
import { headers } from "next/headers";
import { ArticleJsonLd } from "next-seo";

export default async function BlogPost() {
  const nonce = (await headers()).get("x-nonce") ?? undefined;

  return (
    <ArticleJsonLd
      headline="Getting Started with Next SEO"
      datePublished="2024-01-01T08:00:00+00:00"
      author="John Doe"
      nonce={nonce}
    />
  );
}
```

The nonce value must be generated per request and match the one in your CSP header. See the [Next.js CSP guide](https://nextjs.org/docs/app/guides/content-security-policy) for how to generate one in middleware and expose it to your pages.

> **Note**: Omit the `nonce` prop entirely if you are not using a nonce-based CSP — no attribute is rendered when it is not provided.

## S

---

### BreadcrumbJsonLd

BreadcrumbJsonLd

The `BreadcrumbJsonLd` component helps you add breadcrumb structured data to indicate a page's position in the site hierarchy. This can help Google display breadcrumb trails in search results, making it easier for users to understand and navigate your site structure.

#### Basic Usage

```tsx
import { BreadcrumbJsonLd } from "next-seo";

export default function ProductPage() {
  return (
    <>
      <BreadcrumbJsonLd
        items={[
          {
            name: "Home",
            item: "https://example.com",
          },
          {
            name: "Products",
            item: "https://example.com/products",
          },
          {
            name: "Electronics",
            item: "https://example.com/products/electronics",
          },
          {
            name: "Headphones",
            item: "https://example.com/products/electronics/headphones",
          },
          {
            name: "Wireless Headphones XYZ",
          },
        ]}
      />
      <main>
        <h1>Wireless Headphones XYZ</h1>
        {/* Product content */}
      </main>
    </>
  );
}
```

#### Multiple Breadcrumb Trails

Some pages can be reached through multiple paths. You can specify multiple breadcrumb trails:

```tsx
<BreadcrumbJsonLd
  multipleTrails={[
    // First trail: Category path
    [
      {
        name: "Books",
        item: "https://example.com/books",
      },
      {
        name: "Science Fiction",
        item: "https://example.com/books/sciencefiction",
      },
      {
        name: "Award Winners",
      },
    ],
    // Second trail: Award path
    [
      {
        name: "Literature",
        item: "https://example.com/literature",
      },
      {
        name: "Award Winners",
      },
    ],
  ]}
/>
```

#### Advanced Example with Thing Objects

You can use Thing objects with `@id` instead of plain URL strings:

```tsx
<BreadcrumbJsonLd
  items={[
    {
      name: "Home",
      item: "https://example.com",
    },
    {
      na

---

### ProductJsonLd

ProductJsonLd } from "next-seo";

<ProductJsonLd
  name="Premium Wireless Headphones"
  offers={{
    price: 349.99,
    priceCurrency: "USD",
    hasMerchantReturnPolicy: {
      applicableCountry: "US",
      returnPolicyCategory:
        "https://schema.org/MerchantReturnFiniteReturnWindow",
      merchantReturnDays: 45,
      returnFees: "https://schema.org/FreeReturn",
      refundType: "https://schema.org/FullRefund",
    },
  }}
/>;
```

#### Organization-Level Return Policy

For online stores, specify a standard return policy at the organization level:

```tsx
import { OrganizationJsonLd } from "next-seo";

<OrganizationJsonLd
  type="OnlineStore"
  name="Example Store"
  hasMerchantReturnPolicy={{
    applicableCountry: ["US", "CA"],
    returnPolicyCategory: "https://schema.org/MerchantReturnFiniteReturnWindow",
    merchantReturnDays: 60,
    returnFees: "https://schema.org/FreeReturn",
    refundType: "https://schema.org/FullRefund",
  }}
/>;
```

#### Props

| Property                                  | Type                                     | Description                                                |
| ----------------------------------------- | ---------------------------------------- | ---------------------------------------------------------- |
| **Option A Properties**                   |
| `applicableCountry`                       | `string \| string[]`                     | **Required** (Option A). Countries where products are sold |
| `returnPolicyCategory`                    | `string`                                 | **Required** (Option A). Type of return policy             |
| `merchantReturnDays`                      | `number`                                 | Days for returns (required if finite window)               |
| `returnPolicyCountry`                     | `string \| string[]`                     | Countries where returns are processed                      |
| `returnMethod`                            | `string \| string[]`  

---

### LocalBusinessJsonLd

LocalBusinessJsonLd

The `LocalBusinessJsonLd` component helps you add structured data for local businesses to improve their appearance in Google Search and Maps results, including knowledge panels and local business carousels.

#### Basic Usage

```tsx
import { LocalBusinessJsonLd } from "next-seo";

<LocalBusinessJsonLd
  type="Restaurant"
  name="Dave's Steak House"
  address={{
    "@type": "PostalAddress",
    streetAddress: "148 W 51st St",
    addressLocality: "New York",
    addressRegion: "NY",
    postalCode: "10019",
    addressCountry: "US",
  }}
  telephone="+12125551234"
  url="https://www.example.com"
  priceRange="$$$"
/>;
```

#### Restaurant Example with Full Details

```tsx
<LocalBusinessJsonLd
  type="Restaurant"
  name="Dave's Steak House"
  address={{
    "@type": "PostalAddress",
    streetAddress: "148 W 51st St",
    addressLocality: "New York",
    addressRegion: "NY",
    postalCode: "10019",
    addressCountry: "US",
  }}
  geo={{
    "@type": "GeoCoordinates",
    latitude: 40.761293,
    longitude: -73.982294,
  }}
  url="https://www.example.com/restaurant-locations/manhattan"
  telephone="+12122459600"
  image={[
    "https://example.com/photos/1x1/photo.jpg",
    "https://example.com/photos/4x3/photo.jpg",
    "https://example.com/photos/16x9/photo.jpg",
  ]}
  servesCuisine="American"
  priceRange="$$$"
  openingHoursSpecification={[
    {
      "@type": "OpeningHoursSpecification",
      dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      opens: "11:30",
      closes: "22:00",
    },
    {
      "@type": "OpeningHoursSpecification",
      dayOfWeek: "Saturday",
      opens: "16:00",
      closes: "23:00",
    },
    {
      "@type": "OpeningHoursSpecification",
      dayOfWeek: "Sunday",
      opens: "16:00",
      closes: "22:00",
    },
  ]}
  menu="https://www.example.com/menu"
  aggregateRating={{
    "@type": "AggregateRating",
    ratingValue: 4.5,
    ratingCount: 250,
  }}
/>
```

#### Store with Depar

---

