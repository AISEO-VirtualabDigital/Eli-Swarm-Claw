---
id: c7c4d8d6aee2b067
source: "googleapis-nodejs-docs-README.md"
"title: Googleapis Nodejs Docs README"
category: google-api
skillTags: ["pattern"]
containmentHash: ebd12883e8eca5ae6bda
createdAt: 1786051356929
embeddingSig: "about:expire:easy|access:token:about|always:store:most|easy:make:sure|expire:easy:make|make:sure:always|most:recent:tokens|recent:tokens:code|store:most:recent|sure:always:store|tain:access:token|token:about:expire"
---
tain a new access token if it is about to expire. An easy way to make sure you always store the most recent tokens is to use the <code>tokens</code> event:</p>\n<pre class=\"prettyprint source lang-js\"><code class=\"hljs javascript\">oauth2Client.on(<span class=\"hljs-string\">'tokens'</span>, (tokens) =&gt; {\n  <span