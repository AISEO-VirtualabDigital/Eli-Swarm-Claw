---
id: bdbb8bd89527d0ef
source: "agent-eli-v1-frontend-prototype.md"
"title: Agent Eli v1 — Frontend Prototype"
category: ai-agent
skillTags: []
containmentHash: 8a2d756d8c1ea53acd50
createdAt: 1786051352663
embeddingSig: "filter:filter:systems|filter:name:tolowercase|filter:systems:filter|includes:desc:tolowercase|innerhtml:integrations:filter|integrations:filter:filter|integrationsearch:value:tolowercase|name:tolowercase:includes|systems:filter:name|tolowercase:includes:desc|tolowercase:innerhtml:integrations|value:tolowercase:innerhtml"
---
d('integrationSearch')?.value||'').toLowerCase();
 el.innerHTML=integrations.filter(i=>(filter==='All Systems'||i.cat===filter) && (i.name.toLowerCase().includes(q)||i.desc.toLowerCase().includes(q))).map(i=>`
 <div class="integration" data-id="${i.id}">
   <div class="integration-icon">${i.icon}</div><h4>${i.name}</h4><p>${i.desc}</p>