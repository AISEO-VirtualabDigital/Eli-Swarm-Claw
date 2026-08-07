---
id: 96eaccd888695b45
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 4feafbb43fddce0e2beb
createdAt: 1786051357436
embeddingSig: "const:date:format|from:main:import|from:util:const|import:parsehtml:sanitizefilename|import:type:importcontext|importcontext:from:main|main:import:parsehtml|parsehtml:sanitizefilename:serializefrontmatter|sanitizefilename:serializefrontmatter:from|serializefrontmatter:from:util|type:importcontext:from|util:const:date"
---
r';
import type { ImportContext } from '../main';
import { parseHTML, sanitizeFileName, serializeFrontMatter } from '../util';
const DATE_FORMAT = 'dddd, D MMMM YYYY';
const DEFAULT_OUTPUT_FOLDER = 'Journal';


// Apple does not document these; check Journal exports to derive the structure.
const ASSET_TYPE_ALIASES = new Map<string, string>([
	['generic-map', 'location'],
	['multi-pin-map', 'location'],