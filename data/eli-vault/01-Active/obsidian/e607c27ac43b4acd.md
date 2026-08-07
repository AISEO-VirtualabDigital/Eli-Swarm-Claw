---
id: e607c27ac43b4acd
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 5c9e533cb6faf97fdb7d
createdAt: 1786051357436
embeddingSig: "addoutputlocationsetting:apple:notes|apple:notes:retrieve|const:storedprefix:localstorage|file:prefix:format|format:const:storedprefix|localstorage:getitem:local|notes:retrieve:stored|prefix:format:const|retrieve:stored:file|stored:file:prefix|storedprefix:localstorage:getitem|this:addoutputlocationsetting:apple"
---
this.addOutputLocationSetting('Apple Notes');

		// Retrieve stored file prefix format
		const storedPrefix = localStorage.getItem(LOCAL_STORAGE_KEY) || '';
		this.filePrefixFormat = storedPrefix;
new Setting(this.modal.contentEl)
			.setName('File prefix format')
			.setDesc(
				'Format for the creation date prefix in filenames.