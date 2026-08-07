---
id: 547d6a14e5db3216
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: bcb2d42d0117b82eebdb
createdAt: 1786051357436
embeddingSig: "async:function:getallfiles|blobreader:this:file|export:async:function|file:tostring:export|file:tostring:string|llback:zipreader:blobreader|return:this:file|string:return:this|this:file:tostring|tostring:export:async|tostring:string:return|zipreader:blobreader:this"
---
llback(new ZipReader(new BlobReader(this.file)));
	}
toString(): string {
		return this.file.toString();
	}
}

export async function getAllFiles(files: (PickedFolder | PickedFile)[], filter?: (file: PickedFile) => boolean): Promise<PickedFile[]> {
	let results: PickedFile[] = [];
	for (let file of files) {
		try {
			if (file.type === 'folder') {
				results.push(...await getAllFiles(await file.list(), filter));
			}