---
id: 7daca9a2be48ebd8
source: "uswds-README.md"
"title: United States Web Design System"
category: knowledge
skillTags: ["code"]
containmentHash: 6a60fe3ee2fdbc7ef60e
createdAt: 1786051359679
embeddingSig: "character:count:requires|count:from:uswds|count:requires:webpack|example:function:const|from:uswds:uswds|function:const:document|hooks:example:function|react:hooks:example|requires:webpack:react|uswds:character:count|uswds:uswds:character|webpack:react:hooks"
---
Count from "@uswds/uswds/js/usa-character-count";
```
⚠️Requires webpack 5+

React hooks example:

```js
function App() {
  const ref = document.body;

  useEffect(() => {
    // initialize
    characterCount.on(ref);
    // default ref is document.body, if you want to use
    // default you do not have to pass arguments
    accordion.on();
// remove event listeners when the component un-mounts.
    return () => {