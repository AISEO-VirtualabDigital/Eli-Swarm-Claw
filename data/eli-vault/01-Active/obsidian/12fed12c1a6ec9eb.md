---
id: 12fed12c1a6ec9eb
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: f0205831a251a31d130c
createdAt: 1786051357436
embeddingSig: "collectfrontmattertokens:documentel:const|const:entrydate:extractentrydate|const:finaldocument:buildentrydocument|date:entrydate:const|documentel:const:entrydate|documentel:entrydate:frontmatter|entrydate:const:finaldocument|entrydate:extractentrydate:documentel|entrydate:frontmatter:date|extractentrydate:documentel:entrydate|finaldocument:buildentrydocument:documentel|frontmatter:date:entrydate"
---
led
			? (collectFrontMatterTokens(documentEl) ?? {})
			: {};
const entryDate = extractEntryDate(documentEl);
		if (entryDate) {
			frontMatter.date = entryDate;
		}
const finalDocument = buildEntryDocument(documentEl);
		let mdContent = htmlToMarkdown(finalDocument);
if (Object.keys(frontMatter).length > 0) {
			const frontMatterText = serializeFrontMatter(frontMatter);
			if (frontMatterText) {