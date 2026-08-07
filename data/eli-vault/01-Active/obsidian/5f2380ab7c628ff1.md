---
id: 5f2380ab7c628ff1
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: b6bb721eb303dee4aecc
createdAt: 1786051357436
embeddingSig: "await:this:vault|existingfile:mdcontent:return|false:await:this|import:return:false|last:import:return|mdcontent:return:true|modify:existingfile:mdcontent|return:false:await|return:true:await|since:last:import|this:vault:modify|vault:modify:existingfile"
---
ged since last import');
					return false;
				}
			}
await this.vault.modify(existingFile, mdContent);
			return true;
		}

		await this.vault.create(fullPath, mdContent);
		return true;
	}
}
function extractEntryDate(source: HTMLElement): string | undefined {
	const headerText = source.querySelector('.pageHeader')?.textContent?.trim();