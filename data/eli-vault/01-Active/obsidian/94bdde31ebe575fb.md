---
id: 94bdde31ebe575fb
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool"]
containmentHash: 18021ad0276ed8925827
createdAt: 1786051357436
embeddingSig: "await:getallfiles:folders|extensions:contains:file|file:pickedfile:extensions|filepath:this:files|files:await:getallfiles|folders:file:pickedfile|getallfiles:folders:file|nodepickedfolder:filepath:this|path:string:nodepickedfolder|pickedfile:extensions:contains|string:nodepickedfolder:filepath|this:files:await"
---
path: string) => new NodePickedFolder(filepath));
							this.files = await getAllFiles(folders, (file: PickedFile) => extensions.contains(file.extension));
							updateFiles();
						}
					}
				}));
		}
let updateFiles = () => {
			let descriptionFragment = document.createDocumentFragment();
			let fileCount = this.files.length;
			let pathText = this.files.map(f => f.name).join(', ');