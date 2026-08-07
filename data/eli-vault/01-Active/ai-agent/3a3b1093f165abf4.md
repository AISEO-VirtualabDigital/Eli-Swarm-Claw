---
id: 3a3b1093f165abf4
source: "github-llm-ai-frameworks.md"
"title: LLM & AI Frameworks — GitHub Repositories"
category: ai-agent
skillTags: []
containmentHash: a3bd7f3088cdb3aed61e
createdAt: 1786051355211
embeddingSig: "cycle:when:pass|each:render:cycle|inline:object:prop|object:prop:react|object:reference:each|pass:inline:object|prop:react:shallow|react:shallow:comparison|reference:each:render|render:cycle:when|ting:object:reference|when:pass:inline"
---
ting a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object.
</td>
<td valign="top">

> New object ref each render. Inline object prop = new ref = re-render.