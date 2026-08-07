---
id: ce50a05aec9bf8da
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 3791d039f1cdc0fce567
createdAt: 1786051357436
embeddingSig: "attachmentlookup:string:tfile|audio:video:iscancelled|const:attachmentlookup:string|const:startswith:https|continue:const:startswith|findall:audio:video|getattribute:continue:const|iscancelled:return:getattribute|return:getattribute:continue|string:tfile:findall|tfile:findall:audio|video:iscancelled:return"
---
const attachmentLookup = new Map<string, TFile>;
			for (let el of dom.findAll('img, audio, video')) {
				if (ctx.isCancelled()) return;
let src = el.getAttribute('src');
				if (!src) continue;

				try {
					const url = new URL(src.startsWith('//') ? `https:${src}` : src, baseUrl);
if (url.protocol === 'data:') {
						continue;
					}