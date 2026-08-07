---
id: acad0be93acbb338
source: "uswds-README.md"
"title: United States Web Design System"
category: knowledge
skillTags: ["code"]
containmentHash: c9b8069432196f297538
createdAt: 1786051359679
embeddingSig: "build:component:styles|component:styles:scss|example:include:padding|include:padding:theme|padding:theme:site|scss:example:include|site:margins:mobile|styles:scss:example|theme:site:margins|those:tokens:build|tokens:build:component|uses:those:tokens"
---
WDS uses those tokens to build component styles:

```scss
.usa-example {
  @include u-padding-x($theme-site-margins-mobile-width);
  max-width: units($theme-grid-container-max-width);
@include at-media($theme-site-margins-breakpoint) {
    @include u-padding-x($theme-site-margins-width);
  }
}
```
This is the functional equivalent of: