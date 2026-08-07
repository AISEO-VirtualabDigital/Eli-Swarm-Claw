---
id: 19cdd6bd1664238e
source: "fmhy-ai-tools.json"
"title: Fmhy Ai Tools"
category: ai-agent
skillTags: ["code"]
containmentHash: 53abb2d54fdde0b17fff
createdAt: 1786051353935
embeddingSig: "const:newterms:term|filter:length:filter|filter:stopwords:includes|includes:return:newterms|length:const:newterms|length:filter:stopwords|newterms:term:parts|parts:filter:length|return:newterms:return|stopwords:includes:return|term:length:const|term:parts:filter"
---
n if (term.length 1) {\\n const newTerms = [term, ...parts].filter((t) => t.length >= 2).filter((t) => !stopWords.includes(t));\\n return newTerms;\\n }\\n }\\n return term;\\n }\"},\"searchOptions\":{\"combineWith\":\"AND\",\"fuzzy\":false,\"boostDocument\":\"_vp-fn_(documentId, term, storedFields) => {\\n const titles2 = (storedFields?.titles ||