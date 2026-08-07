---
id: 3f16cd9007a3f99a
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 0c4e601ebbdb3b597bba
createdAt: 1786051357436
embeddingSig: "binaryregex:https:firebasestorage|class:roamjsonimporter:extends|const:binaryregex:https|downloadattachments:boolean:false|export:class:roamjsonimporter|extends:formatimporter:downloadattachments|firebasestorage:const:binaryregex|firebasestorage:export:class|formatimporter:downloadattachments:boolean|https:firebasestorage:const|https:firebasestorage:export|roamjsonimporter:extends:formatimporter"
---
x = /https:\/\/firebasestorage(.*?)\?alt(.*?)\)/;
const binaryRegex = /https:\/\/firebasestorage(.*?)\?alt(.*?)/;
export class RoamJSONImporter extends FormatImporter {
	downloadAttachments: boolean = false;
	progress: ImportContext;
	userDNPFormat: string;
// YAML options
	fileDateYAML: boolean = false;
	titleYAML: boolean = false;