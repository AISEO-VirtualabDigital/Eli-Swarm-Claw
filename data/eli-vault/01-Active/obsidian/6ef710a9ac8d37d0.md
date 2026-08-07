---
id: 6ef710a9ac8d37d0
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: ce9bd16cca5177d3c7ec
createdAt: 1786051357436
embeddingSig: "async:file:current|const:getnotionid:file|current:reportprogress:current|current:total:file|extension:html:const|file:current:reportprogress|file:extension:html|files:async:file|html:const:getnotionid|reportprogress:current:total|szips:files:async|total:file:extension"
---
sZips(ctx, files, async (file) => {
			current++;
			ctx.reportProgress(current, total);
try {
				if (file.extension === 'html') {
					const id = getNotionId(file.name);
					if (!id) {
						throw new Error('ids not found for ' + file.filepath);
					}
					const fileInfo = info.idsToFileInfo[id];
					if (!fileInfo) {
						throw new Error('file info not found for ' + file.filepath);