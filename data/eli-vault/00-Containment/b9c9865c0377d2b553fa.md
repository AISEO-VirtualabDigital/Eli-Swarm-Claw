---
id: fde96c581b3cca1b
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["strategy", "metric", "code"]
containmentHash: b9c9865c0377d2b553fa
createdAt: 1786051357436
embeddingSig: "adddropdown:dropdown:notion|contentel:setname:convert|convert:formulas:setdesc|createformulastrategydescription:adddropdown:dropdown|dropdown:notion:import|formulas:setdesc:this|import:normalizepath:notice|modal:contentel:setname|notion:import:normalizepath|setdesc:this:createformulastrategydescription|setname:convert:formulas|this:createformulastrategydescription:adddropdown"
---
.modal.contentEl)
			.setName('Convert formulas')
			.setDesc(this.createFormulaStrategyDescription())
			.addDropdown(dropdown => {
---
### notion.ts

import { normalizePath, Notice, Setting, DataWriteOptions } from 'obsidian';
import { PickedFile } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { extractErrorMessage } from '../util';