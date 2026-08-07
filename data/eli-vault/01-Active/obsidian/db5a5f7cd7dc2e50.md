---
id: db5a5f7cd7dc2e50
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: 6d17e4825796d3fe9edf
createdAt: 1786051357436
embeddingSig: "block:block:string|block:string:tree|node:page:database|page:database:selection|string:tree:node|tree:node:page|tring:type:workspace|true:type:block|type:block:block|type:workspace:workspace|workspace:true:type|workspace:workspace:true"
---
tring }
	| { type: 'workspace', workspace: true }
	| { type: 'block_id', block_id: string };
// Tree node for page/database selection
interface NotionTreeNode {
	id: string; // For pages: page ID; For databases: data_source ID
	title: string;
	type: 'page' | 'database';
	parentId: string | null;
	children: NotionTreeNode[];
	selected: boolean;
	disabled: boolean; // Disabled when parent is selected