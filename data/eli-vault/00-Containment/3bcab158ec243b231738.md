---
id: bcd681ab7a7fe82a
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: 3bcab158ec243b231738
createdAt: 1786051357436
embeddingSig: "addfilechoosersetting:this:addoutputlocationsetting|boolean:init:this|config:templateconfig:null|hasheaderrow:boolean:init|init:this:addfilechoosersetting|null:null:private|null:private:hasheaderrow|private:config:templateconfig|private:hasheaderrow:boolean|templateconfig:null:null|this:addfilechoosersetting:this|this:addoutputlocationsetting:import"
---
];
	private config: TemplateConfig | null = null;
	private hasHeaderRow: boolean;
init() {
		this.addFileChooserSetting('CSV', ['csv']);
		this.addOutputLocationSetting('CSV import');
this.hasHeaderRow = true;
		new Setting(this.modal.contentEl)
			.setName('CSV has header row')
			.setDesc('If enabled, the first row of the CSV file will be treated as column headers.')
			.addToggle(toggle => {