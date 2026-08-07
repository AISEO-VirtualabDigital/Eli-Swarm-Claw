---
id: 4c1da0edae5f5c23
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: fa64b3c9bbc22cf12e67
createdAt: 1786051357436
embeddingSig: "const:fields:templatefield|data:found:file|false:prepare:template|fields:const:fields|fields:templatefield:this|file:return:false|found:file:return|prepare:template:fields|return:false:prepare|template:fields:const|templatefield:this:csvheaders|this:csvheaders:header"
---
No data found in CSV file(s).');
			return false;
		}
// Prepare template fields
		const fields: TemplateField[] = this.csvHeaders.map(header => ({
			id: header,
			label: header,
			exampleValue: this.findExampleValue(header),
		}));
// Set up defaults
		const propertyNames = new Map<string, string>();
		const propertyValues = new Map<string, string>();
		this.csvHeaders.forEach(header => {