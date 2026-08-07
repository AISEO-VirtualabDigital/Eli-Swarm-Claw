---
id: bbbeaff0b13f7664
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 468253ed59d457177d74
createdAt: 1786051357436
embeddingSig: "attachmentfile:attachmentfile:attachmentlookup|attachmentfile:attachmentlookup:attachmentfile|attachmentfile:name:else|attachmentfile:path:attachmentfile|attachmentfile:reportattachmentsuccess:attachmentfile|attachmentlookup:attachmentfile:path|else:keep:json|json:import:frontmattercache|keep:json:import|name:else:keep|path:attachmentfile:reportattachmentsuccess|reportattachmentsuccess:attachmentfile:name"
---
key, attachmentFile);
						if (attachmentFile) {
							attachmentLookup.set(attachmentFile.path, attachmentFile);
							ctx.reportAttachmentSuccess(attachmentFile.name);
						}
						else {
---
### keep-json.ts

import { FrontMatterCache, Notice, Setting, TFolder } from 'obsidian';
import { PickedFile } from '../filesystem';
import { FormatImporter } from '../format-importer';