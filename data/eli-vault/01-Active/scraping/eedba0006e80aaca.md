---
id: eedba0006e80aaca
source: "rust-scraper-README.md"
"title: Rust Scraper README"
category: scraping
skillTags: []
containmentHash: 62a2d7c64bf770483655
createdAt: 1786051357972
embeddingSig: "fragment:html:nlet|fragment:html:parse|html:nlet:selector|html:parse:fragment|nlet:fragment:html|nlet:selector:selector|parse:fragment:html|parse:quot:quot|quot:nlet:fragment|quot:quot:unwrap|selector:parse:quot|selector:selector:parse"
---
lt;/li&gt;\n        &lt;li&gt;Baz&lt;/li&gt;\n    &lt;/ul&gt;\n&quot;#;\n\nlet fragment = Html::parse_fragment(html);\nlet ul_selector = Selector::parse(&quot;ul&quot;).unwrap();\nlet li_selector = Selector::parse(&quot;li&quot;).unwrap();\n\nlet ul = fragment.select(&amp;ul_selector).next().unwrap();\nfor element in ul.select(&amp;li_selector) {\n