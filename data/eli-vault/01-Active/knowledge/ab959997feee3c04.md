---
id: ab959997feee3c04
source: "uswds-README.md"
"title: United States Web Design System"
category: knowledge
skillTags: ["code"]
containmentHash: ab6abbd29eee40af5c1e
createdAt: 1786051359679
embeddingSig: "accordion:angular:example|angular:example:export|charactercount:accordion:angular|class:implements:oninit|component:mounts:return|example:export:class|export:class:implements|implements:oninit:constructor|mounts:return:charactercount|oninit:constructor:this|return:charactercount:accordion|when:component:mounts"
---
when the component un-mounts.
    return () => {
      characterCount.off();
      accordion.off();
    };
  });
}
```
Angular example:

```js
export class App implements OnInit {
  constructor() {
    this.ref = document.body;
    // default ref is document.body, if you want to use
    // default you do not have to pass arguments
  }
ngOnInit() {
    // initialize
    characterCount.on(this.ref);
    accordion.on();
  }