---
id: c374d78f73ac68ab
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: f6bf9f91fadcc3c3a4d9
createdAt: 1786051357436
embeddingSig: "allpages:const:pagedata|allpages:index:pagename|const:pagedata:allpages|convertdatestring:sanitizefilenamekeeppath:pagedata|index:allpages:const|index:pagename:convertdatestring|pagedata:allpages:index|pagedata:title:this|pagename:convertdatestring:sanitizefilenamekeeppath|sanitizefilenamekeeppath:pagedata:title|this:userdnpformat:trim|title:this:userdnpformat"
---
ng> = new Map();
			for (let index in allPages) {
				const pageData = allPages[index];
let pageName = convertDateString(sanitizeFileNameKeepPath(pageData.title), this.userDNPFormat).trim();
				if (pageName === '') {
					progress.reportFailed(pageData.uid, 'Title is empty');
					console.error('Cannot import data with an empty title', pageData);
					continue;
				}