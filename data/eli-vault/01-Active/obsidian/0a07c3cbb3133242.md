---
id: 0a07c3cbb3133242
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: ce5c2f8a35dda11eba4c
createdAt: 1786051357436
embeddingSig: "abstract:import:importcontext|await:promise:abstract|else:await:promise|functions:vault:remove|import:importcontext:promise|importcontext:promise:utility|promise:abstract:import|promise:utility:functions|remove:characters:that|tatusmessage:else:await|utility:functions:vault|vault:remove:characters"
---
tatusMessage);
		}
		else {
			await promise;
		}
	}
abstract import(ctx: ImportContext): Promise<any>;

	// Utility functions for vault

	/** Remove any characters that would be illegal on any platform. */
	sanitizeFilePath(path: string): string {
		return path.replace(/[:|?<>*\\]/g, '');
	}
/**
	 * Recursively create folders, if they don't exist.
	 */
	async createFolders(path: string): Promise<TFolder> {