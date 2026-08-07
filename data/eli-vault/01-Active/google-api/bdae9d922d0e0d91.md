---
id: bdae9d922d0e0d91
source: "googleapis-nodejs-docs-README.md"
"title: Googleapis Nodejs Docs README"
category: google-api
skillTags: ["tool"]
containmentHash: aa61ca0d682eaedf0f9d
createdAt: 1786051356929
embeddingSig: "await:span:oauth2client|class:hljs:keyword|code:noauth2client:setcredentials|gettoken:code:noauth2client|hljs:keyword:await|kens:span:class|keyword:await:span|noauth2client:setcredentials:tokens|oauth2client:gettoken:code|setcredentials:tokens:code|span:class:hljs|span:oauth2client:gettoken"
---
kens} = <span class=\"hljs-keyword\">await</span> oauth2Client.getToken(code)\noauth2Client.setCredentials(tokens);\n</code></pre>\n<p>With the credentials set on your OAuth2 client - you're ready to go!</p>\n<h4 id=\"handling-refresh-tokens\">Handling refresh tokens</h4>\n<p>Access tokens expire. This library will automatically use a refresh token to obtain a new access token if it is about to expire.