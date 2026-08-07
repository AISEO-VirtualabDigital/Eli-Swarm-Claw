---
id: eaba88f90fef5a68
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: a64e2e1f7d5606a1fe2f
createdAt: 1786051357436
embeddingSig: "from:node:import|from:node:zlib|import:type:nodeurl|import:type:nodezlib|node:import:type|node:zlib:import|nodeurl:from:node|nodezlib:from:node|path:import:type|type:nodeurl:from|type:nodezlib:from|zlib:import:platform"
---
:path';
import type * as NodeUrl from 'node:url';
import type * as NodeZlib from 'node:zlib';
import { Platform } from 'obsidian';
import { configureWebWorker } from './z-worker-inline';
configureWebWorker(configure);

export interface PickedFile {
	readonly type: 'file';
	/** Full path, including container zip names, for debugging/reporting purposes */
	readonly fullpath: string;
	/** File name, including extension */