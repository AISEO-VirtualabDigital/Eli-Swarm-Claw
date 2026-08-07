---
id: ac6cb5ff6ea77e0f
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: dd9c9528ba194b80cc97
createdAt: 1786051357436
embeddingSig: "deleted:deleted:notes|deleted:google:keep|deleted:notes:will|exist:your:google|google:keep:will|keep:will:tagged|notes:will:only|only:exist:your|tagged:deleted:deleted|will:only:exist|will:tagged:deleted|your:google:export"
---
deleted in Google Keep will be tagged as deleted. Deleted notes will only exist in your Google export if deleted recently.')
			.addToggle(toggle => {
				toggle.setValue(this.importTrashed);
				toggle.onChange(async (value) => {
					this.importTrashed = value;
				});
			});
this.addOutputLocationSetting('Google Keep');

	}