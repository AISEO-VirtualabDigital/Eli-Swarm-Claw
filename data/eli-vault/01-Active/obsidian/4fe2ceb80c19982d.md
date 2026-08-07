---
id: 4fe2ceb80c19982d
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 63abbbff8e5bc317ebd3
createdAt: 1786051357436
embeddingSig: "addtext:text:text|empty:output:vault|files:leave:empty|folder:vault:imported|imported:files:leave|leave:empty:output|output:vault:root|root:addtext:text|text:setvalue:defaultexportfoldername|text:text:setvalue|vault:imported:files|vault:root:addtext"
---
a folder in the vault to put the imported files. Leave empty to output to vault root.')
			.addText(text => text
				.setValue(defaultExportFolderName)
				.onChange(value => {
					this.outputLocation = value;
					this.outputFolder = null;
				}));
	}
async getOutputFolder(): Promise<TFolder | null> {
		if (this.outputFolder) {
			return this.outputFolder;