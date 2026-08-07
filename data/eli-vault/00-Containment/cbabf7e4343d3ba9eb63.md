---
id: 2c73161e54faf4fc
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: cbabf7e4343d3ba9eb63
createdAt: 1786051357436
embeddingSig: "await:this:getnotesdatabase|database:await:this|database:return:this|elect:location:export|export:return:this|getnotesdatabase:sqlitetagspawned:this|location:export:return|return:this:database|sqlitetagspawned:this:database|this:database:await|this:database:return|this:getnotesdatabase:sqlitetagspawned"
---
elect a location to export to.');
			return;
		}

		this.database = await this.getNotesDatabase() as SQLiteTagSpawned;
		if (!this.database) return;
this.keys = Object.fromEntries(
			(await this.database.all`SELECT z_ent, z_name FROM z_primarykey`).map(k => [k.Z_NAME, k.Z_ENT])
		);
const noteAccounts = await this.database.all`
			SELECT z_pk FROM ziccloudsyncingobject WHERE z_ent = ${this.keys.ICAccount}
		`;