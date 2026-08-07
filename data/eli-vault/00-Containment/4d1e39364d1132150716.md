---
id: 5ec691fe6b3abbc9
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 4d1e39364d1132150716
createdAt: 1786051357436
embeddingSig: "async:authenticateuser:protocoldata|authenticateuser:protocoldata:obsidianprotocoldata|await:this:showsectionpickerui|else:this:switchusersetting|hide:async:authenticateuser|protocoldata:obsidianprotocoldata:protocoldata|settingel:hide:async|showsectionpickerui:else:this|switchusersetting:settingel:hide|this:showsectionpickerui:else|this:switchusersetting:settingel|witchuser:await:this"
---
witchUser();
			await this.showSectionPickerUI();
		}
		else {
			this.switchUserSetting.settingEl.hide();
		}
	}
async authenticateUser(protocolData: ObsidianProtocolData) {
		try {
			if (protocolData['state'] !== this.graphData.state) {
				throw new Error(`An incorrect state was returned.\nExpected state: ${this.graphData.state}\nReturned state: ${protocolData['state']}`);