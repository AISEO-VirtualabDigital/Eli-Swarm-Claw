---
id: c5adf1ed10f8bf12
source: "fmhy-ai-tools.json"
"title: Fmhy Ai Tools"
category: ai-agent
skillTags: ["code"]
containmentHash: 532ca035c70f6f7105b9
createdAt: 1786051353935
embeddingSig: "about:with:term|const:stopwords:frontmatter|frontmatter:frontmatter:synopsis|frontmatter:synopsis:about|replace:const:stopwords|replace:replace:const|stopwords:frontmatter:frontmatter|synopsis:about:with|term:trim:tolowercase|tolowercase:replace:replace|trim:tolowercase:replace|with:term:length"
---
rm = term.trim().toLowerCase().replace(/^\\\\.+/, \\\"\\\").replace(/\\\\.+$/, \\\"\\\");\\n const stopWords = [\\n \\\"frontmatter\\\",\\n \\\"$frontmatter.synopsis\\\",\\n \\\"and\\\",\\n \\\"about\\\",\\n \\\"but\\\",\\n \\\"now\\\",\\n \\\"the\\\",\\n \\\"with\\\",\\n \\\"you\\\"\\n ];\\n if (term.length 1) {\\n const newTerms = [term,