---
id: 5f5832848e830bc3
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 9e75dc8aea0dfb41c9a1
createdAt: 1786051357436
embeddingSig: "authorize:requestbody:tostring|common:oauth2:authorize|graphdata:state:window|https:login:microsoftonline|login:microsoftonline:common|microsoftonline:common:oauth2|oauth2:authorize:requestbody|open:https:login|state:this:graphdata|state:window:open|this:graphdata:state|window:open:https"
---
y',
							state: this.graphData.state,
						});
						window.open(`https://login.microsoftonline.com/common/oauth2/v2.0/authorize?${requestBody.toString()}`);
					})
				);
		this.microsoftAccountSetting.settingEl.toggle(!authenticated);
const rememberMeSetting = new Setting(this.modal.contentEl)
			.setName('Remember me')
			.setDesc('If checked, you will be automatically logged in for subsequent imports.')