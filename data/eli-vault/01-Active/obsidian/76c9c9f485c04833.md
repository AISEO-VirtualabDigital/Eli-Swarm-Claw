---
id: 76c9c9f485c04833
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: ae597a1bcd18f6dc3b4e
createdAt: 1786051357436
embeddingSig: "extensionformime:from:mime|from:main:import|from:mime:import|import:extensionformime:from|import:importcontext:from|import:parsehtml:stringtoutf8|importcontext:from:main|main:import:extensionformime|mime:import:parsehtml|parsehtml:stringtoutf8:from|porter:import:importcontext|stringtoutf8:from:util"
---
porter';
import { ImportContext } from '../main';
import { extensionForMime } from '../mime';
import { parseHTML, stringToUtf8 } from '../util';
export class HtmlImporter extends FormatImporter {
	attachmentSizeLimit: number;
	minimumImageSize: number;
init() {
		this.addFileChooserSetting('HTML', ['htm', 'html'], true);
		this.addAttachmentSizeLimit(0);
		this.addMinimumImageSize(65); // 65 so that 64×64 are excluded