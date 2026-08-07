---
id: a26ffdb1d91851a2
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: []
containmentHash: dcb65bcbba4c8fc88c73
createdAt: 1786051357436
embeddingSig: "await:fspromises:readdir|dirent:await:fspromises|filepath:this:files|files:nodefs:dirent|fspromises:readdir:filepath|list:promise:pickedfile|nodefs:dirent:await|pickedfile:pickedfolder:filepath|pickedfolder:filepath:this|promise:pickedfile:pickedfolder|readdir:filepath:withfiletypes|this:files:nodefs"
---
list(): Promise<(PickedFile | PickedFolder)[]> {
		let { filepath } = this;
		let files: NodeFS.Dirent[] = await fsPromises.readdir(filepath, { withFileTypes: true });
		let results = [];
for (let file of files) {
			if (file.isFile()) {
				results.push(new NodePickedFile(path.join(filepath, file.name)));
			}
			else if (file.isDirectory()) {
				results.push(new NodePickedFolder(path.join(filepath, file.name)));
			}