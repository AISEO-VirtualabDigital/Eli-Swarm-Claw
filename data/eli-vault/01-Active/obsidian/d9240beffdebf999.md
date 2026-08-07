---
id: d9240beffdebf999
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 8867ba183d51dcf4280a
createdAt: 1786051357436
embeddingSig: "await:this:database|const:notefolders:await|database:select:ztitle2|gobject:where:this|icaccount:const:notefolders|keys:icaccount:const|notefolders:await:this|select:ztitle2:from|this:database:select|this:keys:icaccount|where:this:keys|ztitle2:from:ziccloudsyncingobject"
---
gobject WHERE z_ent = ${this.keys.ICAccount}
		`;
		const noteFolders = await this.database.all`
			SELECT z_pk, ztitle2 FROM ziccloudsyncingobject WHERE z_ent = ${this.keys.ICFolder}
		`;
for (let a of noteAccounts) await this.resolveAccount(a.Z_PK);

		for (let f of noteFolders) {
			try {
				await this.resolveFolder(f.Z_PK);
			}
			catch (e) {
				this.ctx.reportFailed(f.ZTITLE2, extractErrorMessage(e));