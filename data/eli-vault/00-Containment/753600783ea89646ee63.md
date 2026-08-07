---
id: adc4835bcc2afdd2
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 753600783ea89646ee63
createdAt: 1786051357436
embeddingSig: "apple:notes:import|body:paragraphs:function|buildentrydocument:source:htmlelement|entry:body:paragraphs|function:buildentrydocument:source|htmlelement:apple:notes|htmlelement:htmlelement:apple|notes:import:notice|paragraphs:function:buildentrydocument|prompt:entry:body|reflection:prompt:entry|source:htmlelement:htmlelement"
---
reflection prompt and entry body paragraphs.
 */
function buildEntryDocument(source: HTMLElement): HTMLElement {
---
### apple-notes.ts

import { Notice, Platform, Setting, TFile, TFolder, moment } from 'obsidian';
import { NoteConverter } from './apple-notes/convert-note';
import { ANAccount, ANAttachment, ANConverter, ANConverterType, ANFolderType } from './apple-notes/models';