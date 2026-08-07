---
id: 5ac7c2664fe4ce88
source: "fmhy-image-tools.json"
"title: Fmhy Image Tools"
category: knowledge
skillTags: ["code"]
containmentHash: 3dc8f85fda2eab72d54c
createdAt: 1786051354092
embeddingSig: "boostdocument:documentid:term|combinewith:fuzzy:false|documentid:term:storedfields|false:boostdocument:documentid|fuzzy:false:boostdocument|newterms:return:term|return:newterms:return|return:term:searchoptions|searchoptions:combinewith:fuzzy|storedfields:const:titles2|term:searchoptions:combinewith|term:storedfields:const"
---
\\n return newTerms;\\n }\\n }\\n return term;\\n }\"},\"searchOptions\":{\"combineWith\":\"AND\",\"fuzzy\":false,\"boostDocument\":\"_vp-fn_(documentId, term, storedFields) => {\\n const titles2 = (storedFields?.titles || []).filter((t) => Boolean(t)).map((t) => t.toLowerCase());\\n let boost = 1;\\n const titleIndex = titles2.map((t, i) => t?.includes(term) ? i : -1).find((i) => i >= 0) ??