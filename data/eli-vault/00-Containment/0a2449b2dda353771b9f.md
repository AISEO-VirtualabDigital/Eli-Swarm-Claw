---
id: 9a49bedddcabf01a
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 0a2449b2dda353771b9f
createdAt: 1786051357436
embeddingSig: "assetpath:path:join|await:this:getattachmentstoragepath|const:fullmatch:linkpath|decodeuri:linkpath:replacementpath|fullmatch:linkpath:match|join:parent:decodeuri|linkpath:match:assetpath|linkpath:replacementpath:await|match:assetpath:path|parent:decodeuri:linkpath|path:join:parent|replacementpath:await:this"
---
) {
									const [fullMatch, linkPath] = match;
									let assetPath = path.join(parent, decodeURI(linkPath));
									let replacementPath = await this.getAttachmentStoragePath(assetPath);
// Don't allow spaces in the file name.
									replacementPath = encodeURI(replacementPath);

									// NOTE: We can't use metadataCache.fileToLinktext to potentially shorten