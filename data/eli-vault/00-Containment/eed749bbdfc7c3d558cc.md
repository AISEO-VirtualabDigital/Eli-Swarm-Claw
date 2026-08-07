---
id: c49f5d15239837be
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: eed749bbdfc7c3d558cc
createdAt: 1786051357436
embeddingSig: "allows:file:lookup|database:using:file|file:lookup:instead|file:path:allows|instead:search:private|lookup:instead:search|mentioned:page:database|page:database:using|path:allows:file|path:mentioned:page|search:private:mentionplaceholders|using:file:path"
---
le path to the set of mentioned page/database IDs
	// Using file path as key allows O(1) file lookup instead of O(n) search
	private mentionPlaceholders: Map<string, Set<string>> = new Map();
	// Track synced blocks mapping (original block ID -> file path)
	// Used to reference synced block content across the vault
	private syncedBlocksMap: Map<string, string> = new Map();