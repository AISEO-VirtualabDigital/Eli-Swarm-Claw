---
id: 4a9ecdbdc11e4ef0
source: "rust-scraper-README.md"
"title: Rust Scraper README"
category: scraping
skillTags: []
containmentHash: 9aeb34f80b72311975ed
createdAt: 1786051357972
embeddingSig: "fragment:u0026quot:u0026lt|hello:u0026lt:u0026gt|u0026gt:hello:u0026lt|u0026gt:u0026lt:u0026gt|u0026gt:u0026quot:nlet|u0026gt:world:u0026lt|u0026lt:u0026gt:hello|u0026lt:u0026gt:u0026lt|u0026lt:u0026gt:u0026quot|u0026lt:u0026gt:world|u0026quot:u0026lt:u0026gt|world:u0026lt:u0026gt"
---
fragment(\\u0026quot;\\u0026lt;h1\\u0026gt;Hello, \\u0026lt;i\\u0026gt;world!\\u0026lt;/i\\u0026gt;\\u0026lt;/h1\\u0026gt;\\u0026quot;);\\nlet selector = Selector::parse(\\u0026quot;h1\\u0026quot;).unwrap();\\n\\nlet h1 = fragment.select(\\u0026amp;selector).next().unwrap();\\n\\nassert_eq!(\\u0026quot;\\u0026lt;h1\\u0026gt;Hello,