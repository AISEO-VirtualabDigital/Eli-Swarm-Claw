---
id: 01c30ade4ecc4f9b
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 14de6a497d0eb128a543
createdAt: 1786051357436
embeddingSig: "await:this:getoutputfolder|file:import:return|folder:await:this|folder:notice:please|getoutputfolder:folder:notice|import:return:folder|least:file:import|pick:least:file|please:pick:least|return:folder:await|this:getoutputfolder:folder|tice:please:pick"
---
tice('Please pick at least one file to import.');
			return;
		}
let folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}
let outputFolder = folder;

		// match 1: assets/something.jpg
		const assetMatcher = new RegExp('\\[[^\\]]*\\]\\((assets/[^\\)]+)\\)', 'gm');
const archiveFolder = await this.createFolders(`${folder.path}/archive`);