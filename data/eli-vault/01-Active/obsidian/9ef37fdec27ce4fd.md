---
id: 9ef37fdec27ce4fd
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 982fcb2178a105f1bbc4
createdAt: 1786051357436
embeddingSig: "arraybuffer:return:buffer|buffer:buffer:slice|buffer:bytelength:offset|buffer:byteoffset:offset|buffer:slice:buffer|bytelength:offset:arraybuffer|byteoffset:offset:buffer|ngth:buffer:bytelength|offset:arraybuffer:return|offset:buffer:byteoffset|return:buffer:buffer|slice:buffer:byteoffset"
---
ngth = buffer.byteLength - offset): ArrayBuffer {
	return buffer.buffer.slice(buffer.byteOffset + offset, buffer.byteOffset + offset + length);
}
export class NodePickedFile implements PickedFile {
	readonly type: 'file' = 'file';
	readonly filepath: string;
readonly fullpath: string;
	readonly name: string;
	readonly basename: string;