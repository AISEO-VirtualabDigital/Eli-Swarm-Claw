---
id: d41a92cb3d63c537
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["metric", "code"]
containmentHash: dba3fd425fcbd49a1c4c
createdAt: 1786051357436
embeddingSig: "already:asserted:previously|attachmentsfolderpath:path:filepath|await:this:getoutputfolder|const:outputfolder:await|filepath:normalizepath:mdfilename|getoutputfolder:already:asserted|mdfilename:const:outputfolder|normalizepath:mdfilename:const|outputfolder:await:this|path:filepath:normalizepath|this:attachmentsfolderpath:path|this:getoutputfolder:already"
---
${this.attachmentsFolderPath.path}/$1]]`);
					}
					let filePath = normalizePath(mdFilename);
					const outputFolder = await this.getOutputFolder();
					// We already asserted previously that the result from getOutputFolder is not null.
					await this.saveAsMarkdownFile(outputFolder!, filePath, mdContent);
					progress.reportNoteSuccess(mdFilename);
				}