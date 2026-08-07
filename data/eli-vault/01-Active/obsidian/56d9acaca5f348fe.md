---
id: 56d9acaca5f348fe
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: ff53a39d4363f6872284
createdAt: 1786051357436
embeddingSig: "file:import:return|files:length:notice|files:this:files|least:file:import|length:notice:please|notice:please:pick|pick:least:file|please:pick:least|progress:files:this|progress:progress:files|this:files:length|this:progress:progress"
---
this.progress = progress;
		let { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}
let outputFolder = await this.getOutputFolder();
		if (!outputFolder) {
			new Notice('Please select a location to export to.');
			return;
		}
for (let file of files) {
			if (progress.isCancelled()) {
				return;
			}