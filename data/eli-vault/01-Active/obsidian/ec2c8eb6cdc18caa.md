---
id: ec2c8eb6cdc18caa
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 49a29dcf9ce775e465ec
createdAt: 1786051357436
embeddingSig: "client:null:null|default:disabled:private|disabled:private:notionclient|files:with:same|notion:default:disabled|notionclient:client:null|null:null:private|null:private:processedpages|private:notionclient:client|private:processedpages:string|same:notion:default|with:same:notion"
---
kip files with same notion-id (default: disabled)
	private notionClient: Client | null = null;
	private processedPages: Set<string> = new Set();
	private requestCount: number = 0;
	private totalNodesToImport: number = 0; // Total number of nodes selected for import
	private selectedNodeIds: Set<string> = new Set(); // IDs of nodes selected in tree for progress tracking
	// Page/database tree for selection