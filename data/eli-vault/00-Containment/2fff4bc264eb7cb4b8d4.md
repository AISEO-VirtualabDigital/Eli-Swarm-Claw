---
id: 72ea37186a625e6a
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 2fff4bc264eb7cb4b8d4
createdAt: 1786051357436
embeddingSig: "async:entries:entry|await:readzip:zipfile|entries:entry:entries|entry:entries:iscancelled|files:iscancelled:return|iscancelled:return:await|promise:void:zipfile|readzip:zipfile:async|return:await:readzip|void:zipfile:files|zipfile:async:entries|zipfile:files:iscancelled"
---
=> Promise<void>) {
	for (let zipFile of files) {
		if (ctx.isCancelled()) return;
		try {
			await readZip(zipFile, async (zip, entries) => {
				for (let entry of entries) {
					if (ctx.isCancelled()) return;
// throw an error for Notion Markdown exports
					if (entry.extension === 'md' && getNotionId(entry.name)) {
						new Notice('Notion Markdown export detected.