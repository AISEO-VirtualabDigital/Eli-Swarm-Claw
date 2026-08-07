---
id: dd897eca5fb00b3f
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 291ccaa0f28c5c811ddb
createdAt: 1786051357436
embeddingSig: "coreconverter:setkeeptitlemode:this|coreconverter:settodoenabled:this|files:length:files|keeptitlemode:reportprogress:files|length:files:length|reportprogress:files:length|setkeeptitlemode:this:keeptitlemode|settodoenabled:this:todoenabled|this:coreconverter:setkeeptitlemode|this:keeptitlemode:reportprogress|this:todoenabled:this|todoenabled:this:coreconverter"
---
s.coreConverter.setTodoEnabled(this.todoEnabled);
		this.coreConverter.setKeepTitleMode(this.keepTitleMode);
ctx.reportProgress(0, files.length);
		for (let i = 0; i < files.length; i++) {
			if (ctx.isCancelled()) return;
const file = files[i];
			ctx.status('Processing ' + file.name);
			try {
				await this.processFile(ctx, folder, file);
				ctx.reportNoteSuccess(file.fullpath);
			}
			catch (e) {