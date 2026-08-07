---
id: cef5b2e00dde588d
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 6d1c7850a8ef2d30289f
createdAt: 1786051357436
embeddingSig: "basename:extension:splitext|filepath:parent:lastindex|filepath:substring:lastindex|lastindex:basename:extension|lastindex:name:filepath|lastindex:parent:filepath|name:filepath:parent|name:filepath:substring|parent:filepath:substring|parent:lastindex:name|substring:lastindex:basename|substring:lastindex:parent"
---
f('\\'));
	let name = filepath;
	let parent = '';
	if (lastIndex >= 0) {
		name = filepath.substring(lastIndex + 1);
		parent = filepath.substring(0, lastIndex);
	}
let [basename, extension] = splitext(name);
	return { parent, name, basename, extension };
}

export function splitext(name: string) {
	let dotIndex = name.lastIndexOf('.');
	let basename = name;