---
id: d4b734ecf95e9b02
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 71f1fe8e01caef5b0f8e
createdAt: 1786051357436
embeddingSig: "attachmentmap:record:string|bear2bkimporter:extends:formatimporter|class:bear2bkimporter:extends|export:class:bear2bkimporter|extends:formatimporter:private|file:tfile:export|formatimporter:private:attachmentmap|metadata:file:tfile|metadata:metadata:file|private:attachmentmap:record|string:metadata:metadata|tfile:export:class"
---
e: string;
	metadata: Metadata;
	file: TFile;
};

export class Bear2bkImporter extends FormatImporter {
	private attachmentMap: Record<string, string> = {};
	private flattenTags: boolean = false;
	private storeId: boolean = false;
init() {
		this.addFileChooserSetting('Bear2bk', ['bear2bk']);
		this.addOutputLocationSetting('Bear');
new Setting(this.modal.contentEl)
			.setName('Flatten nested tags')
			.setDesc(