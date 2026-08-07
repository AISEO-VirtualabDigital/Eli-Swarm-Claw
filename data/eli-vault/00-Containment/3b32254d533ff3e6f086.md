---
id: 27fd9abcd9de98dc
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 3b32254d533ff3e6f086
createdAt: 1786051357436
embeddingSig: "buckets:buckets:textbundle|buckets:textbundle:entry|buckets:textbundle:push|continue:textbundle:buckets|else:buckets:textbundle|entry:else:buckets|entry:fullpath:continue|fullpath:continue:textbundle|push:entry:else|skipping:entry:fullpath|textbundle:buckets:buckets|textbundle:push:entry"
---
('Skipping', entry.fullpath);
				continue;
			}

			if (textBundle in buckets) {
				buckets[textBundle].push(entry);
			}
			else {
				buckets[textBundle] = [entry];
			}
		}
return Object.values(buckets);
	}

	async process(progress: ProgressReporter, bundleName: string, entries: (PickedFile | PickedFolder | ZipEntryFile)[]) {
		// First look for the info.json and check that the file type is Markdown