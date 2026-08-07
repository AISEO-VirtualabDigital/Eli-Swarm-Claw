---
id: bf4e753346d64eb5
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: 830a7febd0e6bc46afa7
createdAt: 1786051357436
embeddingSig: "fullpath:archived:note|google:keep:json|importarchived:reportskipped:fullpath|invalid:google:keep|isarchived:this:importarchived|json:return:keepjson|keep:json:return|keepjson:isarchived:this|path:invalid:google|reportskipped:fullpath:archived|return:keepjson:isarchived|this:importarchived:reportskipped"
---
path, 'Invalid Google Keep JSON');
			return;
		}
		if (keepJson.isArchived && !this.importArchived) {
			ctx.reportSkipped(fullpath, 'Archived note');
			return;
		}
		if (keepJson.isTrashed && !this.importTrashed) {
			ctx.reportSkipped(fullpath, 'Deleted note');
			return;
		}
await this.convertKeepJson(keepJson, folder, basename);
		ctx.reportNoteSuccess(fullpath);
	}