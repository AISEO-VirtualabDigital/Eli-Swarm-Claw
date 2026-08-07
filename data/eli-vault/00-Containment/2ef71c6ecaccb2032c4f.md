---
id: 7f484f0c49edbcbd
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 2ef71c6ecaccb2032c4f
createdAt: 1786051357436
embeddingSig: "const:buckets:record|entries:groupfilesbytextbundle:zipname|entries:zipentryfile:zipentryfile|file:name:entries|groupfilesbytextbundle:zipname:string|name:entries:groupfilesbytextbundle|process:progress:file|progress:file:name|string:entries:zipentryfile|zipentryfile:const:buckets|zipentryfile:zipentryfile:const|zipname:string:entries"
---
s.process(progress, file.name, entries);
			}
		}
	}
groupFilesByTextbundle(zipName: string, entries: ZipEntryFile[]): ZipEntryFile[][] {
		const buckets: Record<string, ZipEntryFile[]> = {};
		const prefix = zipName + '/';
		const dotTextbundle = '.textbundle';
		for (const entry of entries) {
			if (!entry.fullpath.startsWith(prefix)) {
				console.log('Skipping', entry.fullpath);
				continue;