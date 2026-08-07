---
id: 38cdd5fa161afc8b
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 89791ac31a75a231aafe
createdAt: 1786051357436
embeddingSig: "const:sanitizedpath:path|create:folders:starting|createfolders:path:string|folders:starting:with|path:split:segment|path:string:promise|promise:tfolder:create|sanitizedpath:path:split|starting:with:const|string:promise:tfolder|tfolder:create:folders|with:const:sanitizedpath"
---
c createFolders(path: string): Promise<TFolder> {
		// can't create folders starting with a dot
		const sanitizedPath = path.split('/').map(segment => segment.replace(/^\.+/, '')).join('/');
		let normalizedPath = normalizePath(sanitizedPath);
		let folder = this.vault.getAbstractFileByPathInsensitive(normalizedPath);
		if (folder && folder instanceof TFolder) {
			return folder;