---
id: 9aedcc356da71b7b
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: 178ee450d2471093c5a5
createdAt: 1786051357436
embeddingSig: "addoutputlocationsetting:defaultexportfoldername:string|defaultexportfoldername:string:this|descriptionfragment:addoutputlocationsetting:defaultexportfoldername|eateel:span:text|filelocationsetting:setdesc:descriptionfragment|outputlocation:defaultexportfoldername:setting|pathtext:filelocationsetting:setdesc|setdesc:descriptionfragment:addoutputlocationsetting|span:text:pathtext|string:this:outputlocation|text:pathtext:filelocationsetting|this:outputlocation:defaultexportfoldername"
---
eateEl('span', { cls: 'u-pop', text: pathText });
			fileLocationSetting.setDesc(descriptionFragment);
		};
	}
addOutputLocationSetting(defaultExportFolderName: string) {
		this.outputLocation = defaultExportFolderName;
		new Setting(this.modal.contentEl)
			.setName('Output folder')
			.setDesc('Choose a folder in the vault to put the imported files.