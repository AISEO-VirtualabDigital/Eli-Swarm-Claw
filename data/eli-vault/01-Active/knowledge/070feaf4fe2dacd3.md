---
id: 070feaf4fe2dacd3
source: "uswds-README.md"
"title: United States Web Design System"
category: knowledge
skillTags: ["code"]
containmentHash: 2f644f28fdbaea9d1a7b
createdAt: 1786051359679
embeddingSig: "collects:theme:settings|compile:collects:theme|custom:styles:scss|file:that:compile|files:custom:styles|primary:sass:file|sass:file:that|settings:uswds:source|source:files:custom|that:compile:collects|theme:settings:uswds|uswds:source:files"
---
his is the primary Sass file that you'll compile. It collects theme settings, USWDS source files, and custom CSS
`styles.scss` looks something like the following code. It adds all the project theme settings, then adds USWDS source, and finally adds your project's custom styles:
```scss
@forward "uswds-theme";
@forward "uswds";
@forward "uswds-theme-custom-styles";
```