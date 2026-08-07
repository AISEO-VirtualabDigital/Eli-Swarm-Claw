---
id: 7b0f4cfbcf5b9f95
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: ea5c8bb1f525521ae30a
createdAt: 1786051357436
embeddingSig: "apple:notes:uses|first:line:setdesc|first:line:text|include:first:line|line:setdesc:include|line:text:since|ntel:setname:omit|omit:first:line|setdesc:include:first|setname:omit:first|since:apple:notes|text:since:apple"
---
ntEl)
			.setName('Omit first line')
			.setDesc(
				'Don\'t include the first line in the text, since Apple Notes uses it' +
				' as the title. It will still be used as the note name.'
			)
			.addToggle(t => t
				.setValue(true)
				.onChange(async v => this.omitFirstLine = v)
			);
new Setting(this.modal.contentEl)
			.setName('Include handwriting text')
			.setDesc(