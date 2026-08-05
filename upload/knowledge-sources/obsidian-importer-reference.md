# Obsidian Importer — Format Conversion Reference

## Overview

The Obsidian Importer is an official Obsidian plugin for converting notes from other platforms (Apple Notes, Bear, Evernote, Google Keep, Notion, HTML, CSV, and more) into Obsidian-compatible Markdown.

## Supported Formats

The importer handles these source formats through dedicated converter modules:
- **Apple Notes** — converts SQLite database to Markdown with scan/image handling
- **Apple Journal** — journal entry conversion
- **Bear (bear2bk)** — Bear markdown export format
- **CSV** — tabular data to markdown tables
- **Evernote (ENEX)** — Evernote export XML to Markdown
- **HTML** — generic HTML to clean Markdown
- **Google Keep (JSON)** — Google Takeout JSON format
- **Notion (Export)** — Notion HTML/CSV export conversion
- **Notion (API)** — Direct Notion API integration with block converter, database helpers, formula converter, and vault helpers

## Architecture

The importer uses a base `FormatImporter` class extended by each format. Key design patterns:
- `createNote()` creates TFile objects in the vault
- `createFolder()` handles nested folder structures
- Content is processed in batches for performance
- Attachments are extracted and relinked
- Internal links are converted to `[[wikilink]]` format

### apple-journal.ts

import { htmlToMarkdown, moment, normalizePath, Notice, Setting, TFile } from 'obsidian';
import type { FrontMatterCache, TFolder } from 'obsidian';
import type { PickedFile } from '../filesystem';
import { fs, os, path } from '../filesystem';
import { FormatImporter } from '../format-importer';
import type { ImportContext } from '../main';
import { parseHTML, sanitizeFileName, serializeFrontMatter } from '../util';

const DATE_FORMAT = 'dddd, D MMMM YYYY';
const DEFAULT_OUTPUT_FOLDER = 'Journal';


// Apple does not document these; check Journal exports to derive the structure.
const ASSET_TYPE_ALIASES = new Map<string, string>([
	['generic-map', 'location'],
	['multi-pin-map', 'location'],
]);

// currently resource import is not supported
const IGNORED_ASSET_TYPES = new Set<string>(['photo', 'live-photo', 'video']);
const BODY_PARAGRAPH_SELECTOR = '.p2, .p3';
const OVERLAY_TEXT_SELECTORS = [
	'.gridItemOverlayHeader',
	'.gridItemOverlayFooter',
	'.gridItemOverlayText',
	'.activityType',
	'.activityMetrics',
	'.activityMetricsDistance',
	'.activityMetricsCalories',
	'.activityMetricsDuration',
	'.mediaTitle',
	'.mediaArtist',
	'.mediaCategory',
];

const DUPLICATE_HANDLING = {
	Skip: 'skip',
	ImportUpdated: 'import-updated',
	CreateCopy: 'create-copy',
} as const;

type DuplicateHandling = (typeof DUPLICATE_HANDLING)[keyof typeof DUPLICATE_HANDLING];
const DEFAULT_DUPLICATE_HANDLING = DUPLICATE_HANDLING.ImportUpdated;

export class AppleJournalImporter extends FormatImporter {
	private frontMatterEnabled = true;
	private duplicateHandling: DuplicateHandling = DEFAULT_DUPLICATE_HANDLING;

	init(): void {
		const defaultImportPath = detectDefaultEntriesPath();
		this.addFileChooserSetting(
			'Journal entries',
			['htm', 'html'],
			true,
			'Pick the Journal app exported folder',
			defaultImportPath
		);

		new Setting(this.modal.contentEl)
			.setName('Journal metadata')
			.setHeading();

		new Setting(this.modal.contentEl)
			.setName('Add metadata as frontmatter')
			.setDesc('Capture state-of-mind, contact, and similar tokens in YAML when available.')
			.addToggle(toggle => {
				toggle.setValue(this.frontMatterEnabled);
				toggle.onChange(value => {
					this.frontMatterEnabled = value;
				});
			});

		new Setting(this.modal.contentEl)
			.setName('Handle duplicate files')
			.setDesc('How to handle entries that already exist in the vault.')
			.addDropdown(dropdown => {
				dropdown
					.addOption(DUPLICATE_HANDLING.Skip, 'Skip import')
					.addOption(DUPLICATE_HANDLING.ImportUpdated, 'Import only updated')
					.addOption(DUPLICATE_HANDLING.CreateCopy, 'Create a copy')
					.setValue(DEFAULT_DUPLICATE_HANDLING)
					.onChange(value => {
						this.duplicateHandling = value as DuplicateHandling;
					});
			});

		this.addOutputLocationSetting(DEFAULT_OUTPUT_FOLDER);
	}

	async import(ctx: ImportContext): Promise<void> {
		if (this.files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		const folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		ctx.reportProgress(0, this.files.length);
		for (let index = 0; index < this.files.length; index++) {
			if (ctx.isCancelled()) return;

			const file = this.files[index];
			if (file.name === 'index.html') {
				ctx.reportSkipped(file.fullpath, 'index file is not a journal entry');
				ctx.reportProgress(index + 1, this.files.length);
				continue;
			}

			try {
				ctx.status(`Importing note ${file.basename}`);
				const imported = await this.importEntry(ctx, folder, file);
				if (imported) {
					ctx.reportNoteSuccess(file.fullpath);
				}
			}
			catch (error) {
				ctx.reportFailed(file.fullpath, error as Error);
			}

			ctx.reportProgress(index + 1, this.files.length);
		}
	}

	private async importEntry(ctx: ImportContext, folder: TFolder, file: PickedFile): Promise<boolean> {
		const htmlContent = await file.readText();
		const documentEl = parseHTML(htmlContent);
		const frontMatter = this.frontMatterEnabled
			? (collectFrontMatterTokens(documentEl) ?? {})
			: {};

		const entryDate = extractEntryDate(documentEl);
		if (entryDate) {
			frontMatter.date = entryDate;
		}

		const finalDocument = buildEntryDocument(documentEl);
		let mdContent = htmlToMarkdown(finalDocument);

		if (Object.keys(frontMatter).length > 0) {
			const frontMatterText = serializeFrontMatter(frontMatter);
			if (frontMatterText) {
				mdContent = frontMatterText + mdContent;
			}
		}

		const sanitizedName = sanitizeFileName(file.basename);
		const folderPath = folder.path === '/' ? '' : folder.path;
		const fullPath = normalizePath(path.join(folderPath, sanitizedName + '.md'));
		const existingFile = this.vault.getAbstractFileByPath(fullPath)
			?? this.vault.getAbstractFileByPathInsensitive(fullPath);

		if (this.duplicateHandling === DUPLICATE_HANDLING.CreateCopy) {
			await this.saveAsMarkdownFile(folder, file.basename, mdContent);
			return true;
		}

		if (existingFile instanceof TFile) {
			if (this.duplicateHandling === DUPLICATE_HANDLING.Skip) {
				ctx.reportSkipped(file.fullpath, 'file already exists');
				return false;
			}

			if (this.duplicateHandling === DUPLICATE_HANDLING.ImportUpdated) {
				const existingContent = await this.vault.read(existingFile);
				if (existingContent === mdContent) {
					ctx.reportSkipped(file.fullpath, 'journal entry unchanged since last import');
					return false;
				}
			}

			await this.vault.modify(existingFile, mdContent);
			return true;
		}

		await this.vault.create(fullPath, mdContent);
		return true;
	}
}

function extractEntryDate(source: HTMLElement): string | undefined {
	const headerText = source.querySelector('.pageHeader')?.textContent?.trim();
	if (!headerText) return undefined;

	/**
	 * Journal exports format the date as "Sunday, 3 November 2024".
	 */
	const parsed = moment(headerText, DATE_FORMAT);
	if (!parsed.isValid()) return undefined;

	return parsed.format('YYYY-MM-DD');
}

/**
 * Builds a clean document that only contains the reflection prompt and entry body paragraphs.
 */
function buildEntryDocument(source: HTMLElement): HTMLElement {

---

### apple-notes.ts

import { Notice, Platform, Setting, TFile, TFolder, moment } from 'obsidian';
import { NoteConverter } from './apple-notes/convert-note';
import { ANAccount, ANAttachment, ANConverter, ANConverterType, ANFolderType } from './apple-notes/models';
import { descriptor } from './apple-notes/descriptor';
import { ImportContext } from '../main';
import { fsPromises, nodeBufferToArrayBuffer, os, parseFilePath, path, splitext, zlib } from '../filesystem';
import { extractErrorMessage, sanitizeFileName } from '../util';
import { FormatImporter } from '../format-importer';
import { Root } from 'protobufjs';
import SQLiteTag from './apple-notes/sqlite/index';
import { SQLiteTagSpawned } from './apple-notes/models';

const NOTE_FOLDER_PATH = 'Library/Group Containers/group.com.apple.notes';
const NOTE_DB = 'NoteStore.sqlite';
/** Additional amount of seconds that Apple CoreTime datatypes start at, to convert them into Unix timestamps. */
const CORETIME_OFFSET = 978307200;
const LOCAL_STORAGE_KEY = 'apple-notes-importer-file-prefix';

enum DuplicateHandling {
	Skip = 'skip',
	ImportUpdated = 'import-updated',
	CreateCopy = 'create-copy'
}

export class AppleNotesImporter extends FormatImporter {
	ctx: ImportContext;
	rootFolder: TFolder;

	database: SQLiteTagSpawned;
	protobufRoot: Root;

	keys: Record<string, number>;
	owners: Record<number, number> = {};
	resolvedAccounts: Record<number, ANAccount> = {};
	resolvedFiles: Record<number, TFile> = {};
	resolvedFolders: Record<number, TFolder> = {};

	multiAccount = false;
	noteCount = 0;
	parsedNotes = 0;

	omitFirstLine = true;
	importTrashed = false;
	includeHandwriting = false;
	duplicateHandling = DuplicateHandling.ImportUpdated;
	trashFolders: number[] = [];
	filePrefixFormat: string;

	init(): void {
		if (!Platform.isMacOS || !Platform.isDesktop) {
			this.modal.contentEl.createEl('p', {
				text:
					'Due to platform limitations, Apple Notes cannot be exported from this device.' +
					' Open your vault on a Mac to export from Apple Notes.'
			});

			this.notAvailable = true;
			return;
		}

		this.addOutputLocationSetting('Apple Notes');

		// Retrieve stored file prefix format
		const storedPrefix = localStorage.getItem(LOCAL_STORAGE_KEY) || '';
		this.filePrefixFormat = storedPrefix;

		new Setting(this.modal.contentEl)
			.setName('File prefix format')
			.setDesc(
				'Format for the creation date prefix in filenames. Use YYYY, MM, DD for year, month, day.' +
				' Leave blank for no prefix.'
			)
			.addText(t => t
				.setValue(storedPrefix)
				.setPlaceholder('YYYY-MM-DD')
				.onChange(async v => {
					this.filePrefixFormat = v;
					localStorage.setItem(LOCAL_STORAGE_KEY, v);
				})
			);

		new Setting(this.modal.contentEl)
			.setName('Import recently deleted notes')
			.setDesc(
				'Import notes in the "Recently Deleted" folder. Unlike in Apple Notes' +
				', they will not be automatically removed after a set amount of time.'
			)
			.addToggle(t => t
				.setValue(false)
				.onChange(async v => this.importTrashed = v)
			);

		new Setting(this.modal.contentEl)
			.setName('Omit first line')
			.setDesc(
				'Don\'t include the first line in the text, since Apple Notes uses it' +
				' as the title. It will still be used as the note name.'
			)
			.addToggle(t => t
				.setValue(true)
				.onChange(async v => this.omitFirstLine = v)
			);

		new Setting(this.modal.contentEl)
			.setName('Include handwriting text')
			.setDesc(
				'When Apple Notes has detected handwriting in drawings, include it as text before the drawing.'
			)
			.addToggle(t => t
				.setValue(false)
				.onChange(async v => this.includeHandwriting = v)
			);

		new Setting(this.modal.contentEl)
			.setName('Handle duplicate files')
			.setDesc(
				'How to handle notes that already exist in the vault.'
			)
			.addDropdown(d => d
				.addOption(DuplicateHandling.Skip, 'Skip import')
				.addOption(DuplicateHandling.ImportUpdated, 'Import only updated')
				.addOption(DuplicateHandling.CreateCopy, 'Create a copy')
				.setValue(DuplicateHandling.ImportUpdated)
				.onChange(async v => this.duplicateHandling = v as DuplicateHandling)
			);
	}

	async getNotesDatabase(): Promise<SQLiteTagSpawned | null> {
		const dataPath = path.join(os.homedir(), NOTE_FOLDER_PATH);

		const names = window.electron.remote.dialog.showOpenDialogSync({
			defaultPath: dataPath,
			properties: ['openDirectory'],
			//see https://developer.apple.com/videos/play/wwdc2019/701/
			message: 'Select the "group.com.apple.notes" folder to allow Obsidian to read Apple Notes data.'
		});

		if (!names?.includes(dataPath)) {
			new Notice('Data import failed. Ensure you have selected the correct Apple Notes data folder.');
			return null;
		}

		const originalDB = path.join(dataPath, NOTE_DB);
		const clonedDB = path.join(os.tmpdir(), NOTE_DB);

		await fsPromises.copyFile(originalDB, clonedDB);
		await fsPromises.copyFile(originalDB + '-shm', clonedDB + '-shm');
		await fsPromises.copyFile(originalDB + '-wal', clonedDB + '-wal');

		//@ts-ignore
		return new SQLiteTag(clonedDB, { readonly: true, persistent: true });
	}

	async import(ctx: ImportContext): Promise<void> {
		this.ctx = ctx;
		this.protobufRoot = Root.fromJSON(descriptor);
		this.rootFolder = await this.getOutputFolder() as TFolder;

		if (!this.rootFolder) {
			new Notice('Please select a location to export to.');
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
		const noteFolders = await this.database.all`
			SELECT z_pk, ztitle2 FROM ziccloudsyncingobject WHERE z_ent = ${this.keys.ICFolder}
		`;

		for (let a of noteAccounts) await this.resolveAccount(a.Z_PK);

		for (let f of noteFolders) {
			try {
				await this.resolveFolder(f.Z_PK);
			}
			catch (e) {
				this.ctx.reportFailed(f.ZTITLE2, extractErrorMessage(e));
				console.error(e);
			}
		}

		const notes = await this.database.all`
			SELECT
				z_pk, zfolder, ztitle1 FROM ziccloudsyncingobject
			WHERE
				z_ent = ${this.keys.ICNote}
				AND ztitle1 IS NOT NULL
				AND zfolder NOT IN (${this.trashFolders})
		`;
		this.noteCount = notes.length;

		for (let n of notes) {

---

### bear-bear2bk.ts

import { DataWriteOptions, normalizePath, Notice, TFile, Setting } from 'obsidian';
import { path, parseFilePath } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { readZip, ZipEntryFile } from '../zip';

type Metadata = {
	id: string;
	ctime?: number;
	mtime?: number;
	archivedtime?: number;
	trashedtime?: number;
};

type IDMappingValue = {
	filename: string;
	metadata: Metadata;
	file: TFile;
};

export class Bear2bkImporter extends FormatImporter {
	private attachmentMap: Record<string, string> = {};
	private flattenTags: boolean = false;
	private storeId: boolean = false;

	init() {
		this.addFileChooserSetting('Bear2bk', ['bear2bk']);
		this.addOutputLocationSetting('Bear');

		new Setting(this.modal.contentEl)
			.setName('Flatten nested tags')
			.setDesc(
				'When enabled, tags will be split on slashes (/) during import.'
			)
			.addToggle(t => t
				.setValue(false)
				.onChange(async v => this.flattenTags = v)
			);

		new Setting(this.modal.contentEl)
			.setName('Store note identifiers in front matter')
			.setDesc(
				'Links will be automatically updated. Enable this if the note identifier is used outside of linking between notes.'
			)
			.addToggle(t => t
				.setValue(false)
				.onChange(async v => this.storeId = v)
			);
	}

	private extractTagsFromContent(content: string): string[] {
		const tags = new Set<string>();

		// Extract simple #tags (alphanumeric, underscore, hyphen, and slash, no spaces)
		//    Ensures it's not part of a URL or an already processed enclosed tag.
		//    Allows / in the middle of the tag, but not at the start or end of the simple tag.
		//    Diacritics regex range from https://stackoverflow.com/questions/30225552/regex-for-diacritics
		const simpleTagRegex = /(?<!\S)#([A-Za-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿ0-9_][A-Za-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿ0-9_/\-]*[A-Za-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿ0-9_]|[A-Za-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿ0-9_]+)(?![#\w/])/g;
		let matchSimple;
		while ((matchSimple = simpleTagRegex.exec(content)) !== null) {
			const rawSimpleTag = matchSimple[1].trim();
			if (rawSimpleTag !== '') {
				if (this.flattenTags && rawSimpleTag.includes('/')) {
					const parts = rawSimpleTag.split('/');
					for (const part of parts) {
						tags.add(part);
					}
				}
				else {
					tags.add(rawSimpleTag);
				}
			}
		}

		const finalTags = Array.from(tags);
		return finalTags;
	}

	async import(ctx: ImportContext): Promise<void> {

		// Keep track of Bear IDs to new Obsidian file names to update links based on the identifier
		let idMapping: Record<string, IDMappingValue> = {};

		let { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		let folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		let outputFolder = folder;

		// match 1: assets/something.jpg
		const assetMatcher = new RegExp('\\[[^\\]]*\\]\\((assets/[^\\)]+)\\)', 'gm');

		const archiveFolder = await this.createFolders(`${folder.path}/archive`);
		const trashFolder = await this.createFolders(`${folder.path}/trash`);

		for (let file of files) {
			if (ctx.isCancelled()) return;
			ctx.status('Processing ' + file.name);
			await readZip(file, async (zip, entries) => {
				const metadataLookup = await this.collectMetadata(ctx, entries);
				for (let entry of entries) {
					if (ctx.isCancelled()) return;
					let { fullpath, filepath, parent, name, extension } = entry;
					if (name === 'info.json' || name === 'tags.json' || name === 'backup.json') {
						continue;
					}
					ctx.status('Processing ' + name);
					try {
						if (extension === 'md' || extension === 'markdown') {
							const mdFilename = parseFilePath(parent).basename;
							ctx.status('Importing note ' + mdFilename);
							let mdContent = await entry.readText();
							mdContent = this.removeMarkdownHeader(mdFilename, mdContent);

							const assetMatches = [...mdContent.matchAll(assetMatcher)];
							if (assetMatches.length > 0) {
								for (const match of assetMatches) {
									const [fullMatch, linkPath] = match;
									let assetPath = path.join(parent, decodeURI(linkPath));
									let replacementPath = await this.getAttachmentStoragePath(assetPath);

									// Don't allow spaces in the file name.
									replacementPath = encodeURI(replacementPath);

									// NOTE: We can't use metadataCache.fileToLinktext to potentially shorten
									// the path because the attachment might not yet exist, so we can't get a TFile.

									const replacement = fullMatch.replace(linkPath, replacementPath);
									mdContent = mdContent.replace(fullMatch, replacement);
								}
							}

							// Replace spaces in enclosed tags with underscores and make them classic tags
							mdContent = mdContent.replace(/#([^\n#]+?[^\s])#/g, (_match, tag) => { // require non-space before closing to avoid using next tag's opening #
								return '#' + tag.replace(/\s+/g, '_');
							});

							// Remove special characters in simple tags
							mdContent = mdContent.replace(/#([^0-9\s#]+)/g, (_match, tag) => {
								let cleanTag = tag.replace(/[^A-Za-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿ0-9_/\-]/g, '_');
								cleanTag = cleanTag.replace(/_+/g, '_'); // collapse multiple underscores
								return '#' + cleanTag;
							});

							// Extract tags from content
							const tags = this.extractTagsFromContent(mdContent);

							// Use just the filename without extension
							const fileName = mdFilename;
							const metadata = metadataLookup[parent];
							let targetFolder = outputFolder;
							if (metadata?.archivedtime !== undefined) {
								targetFolder = archiveFolder;
							}
							else if (metadata?.trashedtime !== undefined) {
								targetFolder = trashFolder;
							}

							const file = await this.saveAsMarkdownFile(targetFolder, fileName, mdContent);

							if (this.storeId || metadata?.archivedtime || metadata?.trashedtime || tags.length > 0) {
								await this.updateNoteFrontmatter(metadata, file, tags);
							}
							if (metadata?.ctime && metadata?.mtime) {
								await this.modifFileTimestamps(metadata, file);
							}

							idMapping[metadata?.id] = {
								filename: fileName,
								metadata: metadata,
								file: file,
							};

							ctx.reportNoteSuccess(mdFilename);
						}
						else if (filepath.match(/\/assets\//g)) {
							ctx.status('Importing asset ' + entry.name);
							const outputPath = await this.getAttachmentStoragePath(entry.filepath);
							const assetData = await entry.read();

							const writeOptions: DataWriteOptions = {};
							if (entry.ctime) {
								writeOptions.ctime = entry.ctime.getTime();
							}
							if (entry.mtime) {
								writeOptions.mtime = entry.mtime.getTime();
							}

							if (Object.keys(writeOptions).length > 0) {
								await this.vault.createBinary(outputPath, assetData, writeOptions);
							}
							else {

---

### csv.ts

import { BasesConfigFile, Notice, Setting, TFolder } from 'obsidian';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import {
	TemplateConfigurator,
	TemplateConfig,
	TemplateField,
	applyTemplate,
	generateFrontmatter
} from '../template';
import { createBaseFile } from '../base';

interface CSVRow {
	[key: string]: string;
}

export class CSVImporter extends FormatImporter {
	private csvHeaders: string[] = [];
	private csvRows: CSVRow[] = [];
	private config: TemplateConfig | null = null;
	private hasHeaderRow: boolean;

	init() {
		this.addFileChooserSetting('CSV', ['csv']);
		this.addOutputLocationSetting('CSV import');

		this.hasHeaderRow = true;
		new Setting(this.modal.contentEl)
			.setName('CSV has header row')
			.setDesc('If enabled, the first row of the CSV file will be treated as column headers.')
			.addToggle(toggle => {
				toggle.setValue(this.hasHeaderRow);
				toggle.onChange(async (value) => {
					this.hasHeaderRow = value;
				});
			});
	}

	async showTemplateConfiguration(ctx: ImportContext, container: HTMLElement): Promise<boolean> {
		const { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one CSV file to import.');
			return false;
		}

		if (files.length > 1) {
			// NOTE: This shouldn't be possible due to the file chooser settings.
			new Notice('CSV files must be imported one at a time.');
			return false;
		}

		// Parse CSV files to extract headers
		const file = files[0];
		if (ctx.isCancelled()) return false;

		ctx.status('Parsing ' + file.name);
		const csvContent = await file.readText();
		const parsedData = this.parseCSV(csvContent);

		// Store all rows for later processing
		if (this.csvHeaders.length === 0 && parsedData.rows.length > 0) {
			this.csvHeaders = parsedData.headers;
		}
		this.csvRows.push(...parsedData.rows);

		if (this.csvHeaders.length === 0 || this.csvRows.length === 0) {
			new Notice('No data found in CSV file(s).');
			return false;
		}

		// Prepare template fields
		const fields: TemplateField[] = this.csvHeaders.map(header => ({
			id: header,
			label: header,
			exampleValue: this.findExampleValue(header),
		}));

		// Set up defaults
		const propertyNames = new Map<string, string>();
		const propertyValues = new Map<string, string>();
		this.csvHeaders.forEach(header => {
			propertyNames.set(header, this.sanitizeYAMLKey(header));
			propertyValues.set(header, `{{${header}}}`);
		});

		const titleTemplate = this.csvHeaders.length > 0 ? `{{${this.csvHeaders[0]}}}` : '';

		// Create and show configurator
		const configurator = new TemplateConfigurator({
			fields,
			defaults: {
				titleTemplate,
				locationTemplate: '',
				bodyTemplate: '',
				propertyNames,
				propertyValues,
			},
			placeholderSyntax: '{{column_name}}',
		});

		this.config = await configurator.show(container);

		// Return false if user cancelled
		return this.config !== null;
	}

	async import(ctx: ImportContext): Promise<void> {
		// Config was already set by showTemplateConfiguration.
		if (!this.config) {
			new Notice('Configuration is missing.');
			return;
		}

		// Process all rows
		await this.processRows(ctx);
	}

	/**
	 * Look for a non-empty example value for the given header.
	 */
	private findExampleValue(header: string): string {
		for (const row of this.csvRows) {
			const value = row[header];
			if (value && value.trim().length > 0) {
				return value;
			}
		}
		return '';
	}

	private parseCSV(content: string): { headers: string[], rows: CSVRow[] } {
		const lines = this.splitCSVLines(content);
		if (lines.length === 0) {
			return { headers: [], rows: [] };
		}

		let headers: string[];
		let startIndex: number;

		if (this.hasHeaderRow) {
			// First row contains headers
			headers = this.parseCSVLine(lines[0]);
			startIndex = 1;
		}
		else {
			// No header row - generate column names
			const firstRowValues = this.parseCSVLine(lines[0]);
			headers = firstRowValues.map((_, index) => `Column ${index + 1}`);
			startIndex = 0;
		}

		const rows: CSVRow[] = [];

		for (let i = startIndex; i < lines.length; i++) {
			const values = this.parseCSVLine(lines[i]);
			if (values.length === 0) continue; // Skip empty lines

			const row: CSVRow = {};
			for (let j = 0; j < headers.length; j++) {
				row[headers[j]] = values[j] || '';
			}
			rows.push(row);
		}

		return { headers, rows };
	}

	private splitCSVLines(content: string): string[] {
		const lines: string[] = [];
		let currentLine = '';
		let inQuotes = false;

		for (let i = 0; i < content.length; i++) {
			const char = content[i];
			const nextChar = content[i + 1];

			if (char === '"') {
				currentLine += char; // Always add the quote to the line
				if (inQuotes && nextChar === '"') {
					// Escaped quote - add the second quote too
					currentLine += '"';
					i++; // Skip next quote
				}
				else {
					// Toggle quote state
					inQuotes = !inQuotes;
				}
			}
			else if (char === '\n' && !inQuotes) {
				// End of line
				if (currentLine.trim().length > 0) {
					lines.push(currentLine);
				}
				currentLine = '';
			}
			else if (char === '\r' && nextChar === '\n' && !inQuotes) {
				// Windows line ending
				if (currentLine.trim().length > 0) {
					lines.push(currentLine);
				}

---

### evernote-enex.ts

import { FileSystemAdapter, Notice } from 'obsidian';
import { path } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { defaultYarleOptions, dropTheRope } from './yarle/yarle';

export class EvernoteEnexImporter extends FormatImporter {
	init() {
		this.addFileChooserSetting('Evernote', ['enex'], true);
		this.addOutputLocationSetting('Evernote');
	}

	async import(ctx: ImportContext) {
		let { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		let folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		let { app } = this;
		let adapter = app.vault.adapter;
		if (!(adapter instanceof FileSystemAdapter)) return;

		let yarleOptions = {
			...defaultYarleOptions,
			...{
				enexSources: files,
				outputDir: path.join(adapter.getBasePath(), folder.path),
			},
		};

		await dropTheRope(yarleOptions, ctx);
	}
}


---

### html.ts

import { CachedMetadata, htmlToMarkdown, normalizePath, Notice, parseLinktext, requestUrl, Setting, TFile, TFolder } from 'obsidian';
import {
	fsPromises,
	nodeBufferToArrayBuffer,
	NodePickedFile,
	parseFilePath,
	PickedFile,
	url as nodeUrl,
} from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { extensionForMime } from '../mime';
import { parseHTML, stringToUtf8 } from '../util';

export class HtmlImporter extends FormatImporter {
	attachmentSizeLimit: number;
	minimumImageSize: number;

	init() {
		this.addFileChooserSetting('HTML', ['htm', 'html'], true);
		this.addAttachmentSizeLimit(0);
		this.addMinimumImageSize(65); // 65 so that 64×64 are excluded
		this.addOutputLocationSetting('HTML import');
	}

	addAttachmentSizeLimit(defaultInMB: number) {
		this.attachmentSizeLimit = defaultInMB * 10 ** 6;
		new Setting(this.modal.contentEl)
			.setName('Attachment size limit (MB)')
			.setDesc('Set 0 to disable.')
			.addText(text => text
				.then(({ inputEl }) => {
					inputEl.type = 'number';
					inputEl.step = '0.1';
				})
				.setValue(defaultInMB.toString())
				.onChange(value => {
					const num = ['+', '-'].includes(value) ? 0 : Number(value);
					if (Number.isNaN(num) || num < 0) {
						text.setValue((this.attachmentSizeLimit / 10 ** 6).toString());
						return;
					}
					this.attachmentSizeLimit = num * 10 ** 6;
				}));
	}

	addMinimumImageSize(defaultInPx: number) {
		this.minimumImageSize = defaultInPx;
		new Setting(this.modal.contentEl)
			.setName('Minimum image size (px)')
			.setDesc('Set 0 to disable.')
			.addText(text => text
				.then(({ inputEl }) => inputEl.type = 'number')
				.setValue(defaultInPx.toString())
				.onChange(value => {
					const num = ['+', '-'].includes(value) ? 0 : Number(value);
					if (!Number.isInteger(num) || num < 0) {
						text.setValue(this.minimumImageSize.toString());
						return;
					}
					this.minimumImageSize = num;
				}));
	}

	async import(ctx: ImportContext): Promise<void> {
		const { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		const folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		const fileLookup = new Map<string, { file: PickedFile, tFile: TFile }>;

		ctx.reportProgress(0, files.length);
		for (let i = 0; i < files.length; i++) {
			if (ctx.isCancelled()) return;

			const file = files[i];
			const tFile = await this.processFile(ctx, folder, file);
			if (tFile) {
				fileLookup.set(
					file instanceof NodePickedFile
						? nodeUrl.pathToFileURL(file.filepath).href
						: file.name,
					{ file, tFile });
			}

			ctx.reportProgress(i+1, files.length);
		}

		const { metadataCache } = this.app;

		let resolveUpdatesCompletePromise: () => void;
		const updatesCompletePromise = new Promise<void>((resolve) => {
			resolveUpdatesCompletePromise = resolve;
		});

		// @ts-ignore
		metadataCache.onCleanCache(async () => {
			// This function must call resolveUpdatesCompletePromise() before returning.
			for (const [fileKey, { file, tFile }] of fileLookup) {
				if (ctx.isCancelled()) break;

				try {
					// Attempt to parse links using MetadataCache
					let mdContent = await this.app.vault.cachedRead(tFile);

					// @ts-ignore
					const cache = metadataCache.computeMetadataAsync
						// @ts-ignore
						? await metadataCache.computeMetadataAsync(stringToUtf8(mdContent)) as CachedMetadata
						: metadataCache.getFileCache(tFile);
					if (!cache) continue;

					// Gather changes to make to the document
					const changes = [];
					if (cache.links) {
						for (const { link, position, displayText } of cache.links) {
							const { path, subpath } = parseLinktext(link);
							let linkKey: string;
							if (nodeUrl) {
								const url = new URL(encodeURI(path), fileKey);
								url.hash = '';
								url.search = '';
								linkKey = decodeURIComponent(url.href);
							}
							else {
								linkKey = parseFilePath(path.replace(/#/gu, '%23')).name;
							}
							const linkFile = fileLookup.get(linkKey);
							if (linkFile) {
								const newLink = this.app.fileManager.generateMarkdownLink(linkFile.tFile, tFile.path, subpath, displayText);
								changes.push({ from: position.start.offset, to: position.end.offset, text: newLink });
							}
						}
					}

					// Apply changes from last to first
					changes.sort((a, b) => b.from - a.from);
					for (const change of changes) {
						mdContent = mdContent.substring(0, change.from) + change.text + mdContent.substring(change.to);
					}

					await this.vault.modify(tFile, mdContent);
				}
				catch (e) {
					ctx.reportFailed(file.fullpath, e);
				}
			}

			resolveUpdatesCompletePromise();
		});

		await updatesCompletePromise;
	}

	async processFile(ctx: ImportContext, folder: TFolder, file: PickedFile) {
		ctx.status('Processing ' + file.name);
		try {
			const htmlContent = await file.readText();

			const dom = parseHTML(htmlContent);
			fixDocumentUrls(dom);

			// Find all the attachments and download them
			const baseUrl = file instanceof NodePickedFile ? nodeUrl.pathToFileURL(file.filepath) : undefined;
			// Get the directory URL for path traversal validation (URL resolves './' to parent directory)
			const allowedBaseDirUrl = baseUrl ? new URL('./', baseUrl.href).href : undefined;
			const attachments = new Map<string, TFile | null>;
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

					let key = url.href;
					let attachmentFile = attachments.get(key);
					if (!attachments.has(key)) {
						ctx.status('Downloading attachment for ' + file.name);
						attachmentFile = await this.downloadAttachment(folder, el, url, allowedBaseDirUrl);
						attachments.set(key, attachmentFile);
						if (attachmentFile) {
							attachmentLookup.set(attachmentFile.path, attachmentFile);
							ctx.reportAttachmentSuccess(attachmentFile.name);
						}
						else {

---

### keep-json.ts

import { FrontMatterCache, Notice, Setting, TFolder } from 'obsidian';
import { PickedFile } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ATTACHMENT_EXTS, ImportContext } from '../main';
import { serializeFrontMatter } from '../util';
import { readZip, ZipEntryFile } from '../zip';
import { KeepJson } from './keep/models';
import { sanitizeTag, sanitizeTags, toSentenceCase } from './keep/util';


const BUNDLE_EXTS = ['zip'];
const NOTE_EXTS = ['json'];
// Ignore the following files:
// - Html duplicates
// - Another html summary
// - A text file with labels summary
const ZIP_IGNORED_EXTS = ['html', 'txt'];

export class KeepImporter extends FormatImporter {
	importArchivedSetting: Setting;
	importTrashedSetting: Setting;
	importArchived: boolean = false;
	importTrashed: boolean = false;

	init() {
		this.addFileChooserSetting('Notes & attachments', [...BUNDLE_EXTS, ...NOTE_EXTS, ...ATTACHMENT_EXTS], true);

		this.importArchivedSetting = new Setting(this.modal.contentEl)
			.setName('Import archived notes')
			.setDesc('If imported, files archived in Google Keep will be tagged as archived.')
			.addToggle(toggle => {
				toggle.setValue(this.importArchived);
				toggle.onChange(async (value) => {
					this.importArchived = value;
				});
			});

		this.importTrashedSetting = new Setting(this.modal.contentEl)
			.setName('Import deleted notes')
			.setDesc('If imported, files deleted in Google Keep will be tagged as deleted. Deleted notes will only exist in your Google export if deleted recently.')
			.addToggle(toggle => {
				toggle.setValue(this.importTrashed);
				toggle.onChange(async (value) => {
					this.importTrashed = value;
				});
			});

		this.addOutputLocationSetting('Google Keep');

	}

	async import(ctx: ImportContext): Promise<void> {
		let { files } = this;

		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		let folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to import your files to.');
			return;
		}
		let assetFolderPath = `${folder.path}/Assets`;

		for (let file of files) {
			if (ctx.isCancelled()) return;
			await this.handleFile(file, folder, assetFolderPath, ctx);
		}
	}

	async handleFile(file: PickedFile, folder: TFolder, assetFolderPath: string, ctx: ImportContext) {
		let { fullpath, name, extension } = file;
		ctx.status('Processing ' + name);
		try {
			if (extension === 'zip') {
				await this.readZipEntries(file, folder, assetFolderPath, ctx);
			}
			else if (extension === 'json') {
				await this.importKeepNote(file, folder, ctx);
			}
			else if (ATTACHMENT_EXTS.contains(extension)) {
				ctx.status('Importing attachment ' + name);
				await this.copyFile(file, assetFolderPath);
				ctx.reportAttachmentSuccess(fullpath);
			}
			// Don't mention skipped files when parsing zips, because
			else if (!(file instanceof ZipEntryFile) && !ZIP_IGNORED_EXTS.contains(extension)) {
				ctx.reportSkipped(fullpath);
			}
		}
		catch (e) {
			ctx.reportFailed(fullpath, e);
		}
	}

	async readZipEntries(file: PickedFile, folder: TFolder, assetFolderPath: string, ctx: ImportContext) {
		await readZip(file, async (zip, entries) => {
			for (let entry of entries) {
				if (ctx.isCancelled()) return;
				await this.handleFile(entry, folder, assetFolderPath, ctx);
			}
		});
	}

	async importKeepNote(file: PickedFile, folder: TFolder, ctx: ImportContext) {
		let { fullpath, basename } = file;
		ctx.status('Importing note ' + basename);

		let content = await file.readText();

		const keepJson = JSON.parse(content) as KeepJson;
		if (!keepJson || !keepJson.userEditedTimestampUsec || !keepJson.createdTimestampUsec) {
			ctx.reportFailed(fullpath, 'Invalid Google Keep JSON');
			return;
		}
		if (keepJson.isArchived && !this.importArchived) {
			ctx.reportSkipped(fullpath, 'Archived note');
			return;
		}
		if (keepJson.isTrashed && !this.importTrashed) {
			ctx.reportSkipped(fullpath, 'Deleted note');
			return;
		}

		await this.convertKeepJson(keepJson, folder, basename);
		ctx.reportNoteSuccess(fullpath);
	}

	// Keep assets have filenames that appear unique, so no duplicate handling isn't implemented
	async copyFile(file: PickedFile, folderPath: string) {
		let assetFolder = await this.createFolders(folderPath);
		let data = await file.read();
		await this.vault.createBinary(`${assetFolder.path}/${file.name}`, data);
	}

	async convertKeepJson(keepJson: KeepJson, folder: TFolder, filename: string) {
		let mdContent: string[] = [];

		// First let's gather some metadata
		let frontMatter: FrontMatterCache = {};

		// Aliases
		if (keepJson.title) {
			let aliases = keepJson.title.split('\n').filter(a => a !== filename);

			if (aliases.length > 0) {
				frontMatter['aliases'] = aliases;
			}
		}

		let tags: string[] = [];
		// Add in tags to represent Keep properties
		if (keepJson.color && keepJson.color !== 'DEFAULT') {
			let colorName = keepJson.color.toLowerCase();
			colorName = toSentenceCase(colorName);
			tags.push(`Keep/Color/${colorName}`);
		}
		if (keepJson.isPinned) tags.push('Keep/Pinned');
		if (keepJson.attachments) tags.push('Keep/Attachment');
		if (keepJson.isArchived) tags.push('Keep/Archived');
		if (keepJson.isTrashed) tags.push('Keep/Deleted');
		if (keepJson.labels) {
			for (let label of keepJson.labels) {
				tags.push(`Keep/Label/${label.name}`);
			}
		}

		if (tags.length > 0) {
			frontMatter['tags'] = tags.map(tag => sanitizeTag(tag));
		}

		mdContent.push(serializeFrontMatter(frontMatter));

		// Actual content

		if (keepJson.textContent) {
			mdContent.push('\n');
			mdContent.push(sanitizeTags(keepJson.textContent));
		}

		if (keepJson.listContent) {
			let mdListContent = [];
			for (const listItem of keepJson.listContent) {
				// Don't put in blank checkbox items
				if (!listItem.text) continue;

				let listItemContent = `- [${listItem.isChecked ? 'X' : ' '}] ${listItem.text}`;
				mdListContent.push(sanitizeTags(listItemContent));
			}

			mdContent.push('\n\n');
			mdContent.push(mdListContent.join('\n'));
		}

		if (keepJson.attachments) {
			mdContent.push('\n\n');
			for (const attachment of keepJson.attachments) {
				mdContent.push(`![[${attachment.filePath}]]`);

---

### notion-api.ts

import { Notice, Setting, normalizePath, requestUrl, TFile, TFolder, setIcon, DataWriteOptions, Vault } from 'obsidian';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { Client, PageObjectResponse } from '@notionhq/client';
import { extractErrorMessage, sanitizeFileName, serializeFrontMatter } from '../util';
import { parseFilePath } from '../filesystem';

// Import helper modules
import { createPlaceholder, PlaceholderType } from './notion-api/utils';
import {
	makeNotionRequest,
	fetchAllBlocks,
	extractPageTitle,
	extractFrontMatter,
	hasChildPagesOrDatabases
} from './notion-api/api-helpers';
import { convertBlocksToMarkdown } from './notion-api/block-converter';
import { getUniqueFolderPath, getUniqueFilePath } from './notion-api/vault-helpers';
import { processDatabasePlaceholders, importDatabaseCore } from './notion-api/database-helpers';
import { DatabaseInfo, RelationPlaceholder, DatabaseProcessingContext, FetchAndImportPageParams } from './notion-api/types';
import { downloadAttachment } from './notion-api/attachment-helpers';

export type FormulaImportStrategy = 'static' | 'hybrid';

// Notion API parent types (based on @notionhq/client internal types)
type NotionParent =
	| { type: 'page_id', page_id: string }
	| { type: 'data_source_id', data_source_id: string, database_id: string }
	| { type: 'database_id', database_id: string }
	| { type: 'workspace', workspace: true }
	| { type: 'block_id', block_id: string };

// Tree node for page/database selection
interface NotionTreeNode {
	id: string; // For pages: page ID; For databases: data_source ID
	title: string;
	type: 'page' | 'database';
	parentId: string | null;
	children: NotionTreeNode[];
	selected: boolean;
	disabled: boolean; // Disabled when parent is selected
	collapsed: boolean; // Whether the node's children are collapsed
}

export class NotionAPIImporter extends FormatImporter {
	notionToken: string = '';
	formulaStrategy: FormulaImportStrategy = 'hybrid'; // Default strategy
	downloadExternalAttachments: boolean = false; // Download external attachments
	singleLineBreaks: boolean = false; // Single line breaks between blocks (default: disabled)
	coverPropertyName: string = 'cover'; // Custom property name for page cover
	databasePropertyName: string = 'base'; // Property name for linking pages to their database
	incrementalImport: boolean = false; // Incremental import: skip files with same notion-id (default: disabled)
	private notionClient: Client | null = null;
	private processedPages: Set<string> = new Set();
	private requestCount: number = 0;
	private totalNodesToImport: number = 0; // Total number of nodes selected for import
	private selectedNodeIds: Set<string> = new Set(); // IDs of nodes selected in tree for progress tracking
	// Page/database tree for selection
	private pageTree: NotionTreeNode[] = [];
	private pageTreeContainer: HTMLElement | null = null;
	private listPagesButton: any = null;  // ButtonComponent from obsidian
	private toggleSelectButton: any = null;  // ButtonComponent from obsidian
	// save output root path for database handling
	//  we will flatten all database in this folder later
	private outputRootPath: string = '';
	// Track all processed databases for relation resolution
	private processedDatabases: Map<string, DatabaseInfo> = new Map();
	// Track all relation placeholders that need to be replaced
	private relationPlaceholders: RelationPlaceholder[] = [];
	// Progress counters: separate tracking for pages and attachments
	private processedPagesCount: number = 0; // Total processed (imported + skipped) for progress tracking
	private attachmentsDownloaded: number = 0;
	// Track Notion ID (page/database) to file path mapping for mention replacement
	// Stores path relative to vault root without extension: "folder/subfolder/Page Title"
	// This allows wiki links to work correctly even with duplicate filenames: [[folder/Page Title]]
	private notionIdToPath: Map<string, string> = new Map();
	// Track mention placeholders for efficient replacement (similar to relationPlaceholders)
	// Maps source file path to the set of mentioned page/database IDs
	// Using file path as key allows O(1) file lookup instead of O(n) search
	private mentionPlaceholders: Map<string, Set<string>> = new Map();
	// Track synced blocks mapping (original block ID -> file path)
	// Used to reference synced block content across the vault
	private syncedBlocksMap: Map<string, string> = new Map();
	// Track synced child placeholders (file path -> Set of child IDs)
	// Used to efficiently replace synced child placeholders without scanning all files
	// Separated by type to avoid unnecessary placeholder checks
	private syncedChildPagePlaceholders: Map<string, Set<string>> = new Map();
	private syncedChildDatabasePlaceholders: Map<string, Set<string>> = new Map();

	init() {
		// No file chooser needed since we're importing via API
		this.addOutputLocationSetting('Notion');

		// Notion API Token input
		new Setting(this.modal.contentEl)
			.setName('Notion API token')
			.setDesc(this.createTokenDescription())
			.addText(text => text
				.setPlaceholder('ntn_...')
				.setValue(this.notionToken)
				.onChange(value => {
					this.notionToken = value.trim();
				})
				.then(textComponent => {
					// Set as password input
					textComponent.inputEl.type = 'password';
				}));

		// List pages and toggle selection buttons
		const listPagesSetting = new Setting(this.modal.contentEl)
			.setName('Select pages to import')
			.setDesc('Click "Load" to see data you can import. If a page or database is missing, check that your Notion integration has access to it.');

		// Store button references in closure to avoid constructor timing issues
		let toggleButtonRef: any = null;
		let listButtonRef: any = null;

		// Toggle select all/none button
		listPagesSetting.addButton(button => {
			toggleButtonRef = button;
			button
				.setButtonText('Select all')
				.onClick(() => {
					this.toggleSelectButton = toggleButtonRef;
					this.handleToggleSelectClick();
				});

			// Add custom class for fixed width and initially hide
			if (button.buttonEl) {
				button.buttonEl.addClass('notion-toggle-button');
				button.buttonEl.style.display = 'none'; // Hide until tree is loaded
			}

			return button;
		});

		// List pages button
		listPagesSetting.addButton(button => {
			listButtonRef = button;
			button
				.setButtonText('Load')
				.onClick(async () => {
					try {
						this.listPagesButton = listButtonRef;
						this.toggleSelectButton = toggleButtonRef;
						await this.loadPageTree();
					}
					catch (error) {
						console.error('[Notion Importer] Error in loadPageTree:', error);
						new Notice(`Failed to load pages: ${extractErrorMessage(error)}`);
					}
				});

			// Add custom class for fixed width
			if (button.buttonEl) {
				button.buttonEl.addClass('notion-load-button');
				button.buttonEl.addClass('mod-cta');
			}

			return button;
		});


		// Page tree container (using Publish plugin's style with proper hierarchy)
		// Create the section wrapper
		const publishSection = this.modal.contentEl.createDiv();
		publishSection.addClass('file-tree', 'publish-section');

		// Create the change list container
		this.pageTreeContainer = publishSection.createDiv('publish-change-list');
		this.pageTreeContainer.style.maxHeight = '200px';
		this.pageTreeContainer.style.overflowY = 'auto';
		this.pageTreeContainer.style.border = '1px solid var(--background-modifier-border)';
		this.pageTreeContainer.style.borderRadius = 'var(--radius-s)';
		this.pageTreeContainer.style.backgroundColor = 'var(--background-primary-alt)';
		this.pageTreeContainer.style.padding = 'var(--size-4-2)';

		// Add placeholder text
		const placeholder = this.pageTreeContainer.createDiv();
		placeholder.style.color = 'var(--text-muted)';
		placeholder.style.fontSize = 'var(--font-ui-small)';
		placeholder.style.textAlign = 'center';
		placeholder.style.padding = '30px 10px';
		placeholder.setText('Click "Load" to load your Notion pages and databases.');

		// Incremental import setting
		new Setting(this.modal.contentEl)
			.setName('Incremental import')
			.setDesc('Adds a notion-id property to pages so that future imports can skip pages that have already been imported.')
			.addToggle(toggle => toggle
				.setValue(false) // Default to disabled
				.onChange(value => {
					this.incrementalImport = value;
				}));

		// Formula import strategy
		new Setting(this.modal.contentEl)
			.setName('Convert formulas')
			.setDesc(this.createFormulaStrategyDescription())
			.addDropdown(dropdown => {

---

### notion.ts

import { normalizePath, Notice, Setting, DataWriteOptions } from 'obsidian';
import { PickedFile } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { extractErrorMessage } from '../util';
import { readZip, ZipEntryFile } from '../zip';
import { cleanDuplicates } from './notion/clean-duplicates';
import { readToMarkdown } from './notion/convert-to-md';
import { NotionResolverInfo } from './notion/notion-types';
import { getNotionId } from './notion/notion-utils';
import { parseFileInfo } from './notion/parse-info';

export class NotionImporter extends FormatImporter {


	parentsInSubfolders: boolean;
	singleLineBreaks: boolean;

	init() {
		this.parentsInSubfolders = true;
		this.addFileChooserSetting('Exported Notion', ['zip']);
		this.addOutputLocationSetting('Notion');
		new Setting(this.modal.contentEl)
			.setName('Save parent pages in subfolders')
			.setDesc('Places the parent database pages in the same folder as the nested content.')
			.addToggle((toggle) => toggle
				.setValue(this.parentsInSubfolders)
				.onChange((value) => (this.parentsInSubfolders = value)));

		new Setting(this.modal.contentEl)
			.setName('Single line breaks')
			.setDesc('Separate Notion blocks with only one line break (default is 2).')
			.addToggle((toggle) => toggle
				.setValue(this.singleLineBreaks)
				.onChange((value) => {
					this.singleLineBreaks = value;
				}));
	}

	async import(ctx: ImportContext): Promise<void> {
		const { vault, parentsInSubfolders, files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		const folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		let targetFolderPath = folder.path;
		targetFolderPath = normalizePath(targetFolderPath);
		// As a convention, all parent folders should end with "/" in this importer.
		if (!targetFolderPath?.endsWith('/')) targetFolderPath += '/';

		const info = new NotionResolverInfo(vault.getConfig('attachmentFolderPath') ?? '', this.singleLineBreaks);

		// loads in only path & title information to objects
		ctx.status('Looking for files to import');
		let total = 0;
		await processZips(ctx, files, async (file) => {
			try {
				await parseFileInfo(info, file);
				total = Object.keys(info.idsToFileInfo).length + Object.keys(info.pathsToAttachmentInfo).length;
				ctx.reportProgress(0, total);
			}
			catch {
				ctx.reportSkipped(file.fullpath);
			}
		});
		if (ctx.isCancelled()) return;

		ctx.status('Resolving links and de-duplicating files');

		cleanDuplicates({
			vault,
			info,
			targetFolderPath,
			parentsInSubfolders,
		});

		const flatFolderPaths = new Set<string>([targetFolderPath]);
		const allFolderPaths = Object.values(info.idsToFileInfo)
			.map((fileInfo) => targetFolderPath + info.getPathForFile(fileInfo))
			.concat(Object.values(info.pathsToAttachmentInfo).map(
				(attachmentInfo) => attachmentInfo.targetParentFolder
			));
		for (let folderPath of allFolderPaths) {
			flatFolderPaths.add(folderPath);
		}
		for (let path of flatFolderPaths) {
			if (ctx.isCancelled()) return;
			await this.createFolders(path);
		}

		let current = 0;
		ctx.status('Starting import');
		await processZips(ctx, files, async (file) => {
			current++;
			ctx.reportProgress(current, total);

			try {
				if (file.extension === 'html') {
					const id = getNotionId(file.name);
					if (!id) {
						throw new Error('ids not found for ' + file.filepath);
					}
					const fileInfo = info.idsToFileInfo[id];
					if (!fileInfo) {
						throw new Error('file info not found for ' + file.filepath);
					}

					ctx.status(`Importing note ${fileInfo.title}`);

					const markdownBody = await readToMarkdown(info, file);
					let writeOptions: DataWriteOptions = {};

					if (fileInfo.ctime) {
						writeOptions.ctime = fileInfo.ctime.getTime();
						writeOptions.mtime = fileInfo.ctime.getTime();
					}

					if (fileInfo.mtime) {
						writeOptions.mtime = fileInfo.mtime.getTime();
					}

					const path = `${targetFolderPath}${info.getPathForFile(fileInfo)}${fileInfo.title}.md`;
					await vault.create(path, markdownBody, writeOptions);
					ctx.reportNoteSuccess(file.fullpath);
				}
				else {
					const attachmentInfo = info.pathsToAttachmentInfo[file.filepath];
					if (!attachmentInfo) {
						throw new Error('attachment info not found for ' + file.filepath);
					}

					ctx.status(`Importing attachment ${file.name}`);

					const data = await file.read();
					await vault.createBinary(`${attachmentInfo.targetParentFolder}${attachmentInfo.nameWithExtension}`, data);
					ctx.reportAttachmentSuccess(file.fullpath);
				}
			}
			catch (e) {
				if (extractErrorMessage(e) === 'page body was not found') {
					ctx.reportSkipped(file.fullpath, 'page body was not found');
					return;
				}

				ctx.reportFailed(file.fullpath, e);
			}
		});
	}
}

async function processZips(ctx: ImportContext, files: PickedFile[], callback: (file: ZipEntryFile) => Promise<void>) {
	for (let zipFile of files) {
		if (ctx.isCancelled()) return;
		try {
			await readZip(zipFile, async (zip, entries) => {
				for (let entry of entries) {
					if (ctx.isCancelled()) return;

					// throw an error for Notion Markdown exports
					if (entry.extension === 'md' && getNotionId(entry.name)) {
						new Notice('Notion Markdown export detected. Please export Notion data to HTML instead.');
						ctx.cancel();
						throw new Error('Notion importer uses only HTML exports. Please use the correct format.');
					}

					// Skip databses in CSV format
					if (entry.extension === 'csv' && getNotionId(entry.name)) continue;

					// Skip summary files
					if (entry.name === 'index.html') continue;

					// Only recurse into zip files if they are at the root of the parent zip
					// because users can attach zip files to Notion, and they should be considered
					// attachment files.
					if (entry.extension === 'zip' && entry.parent === '') {
						try {
							await processZips(ctx, [entry], callback);
						}
						catch {
							ctx.reportFailed(entry.fullpath);
						}
					}
					else {
						await callback(entry);
					}
				}
			});
		}
		catch {
			ctx.reportFailed(zipFile.fullpath);
		}
	}
}

---

### onenote.ts

import { OnenotePage, SectionGroup, User, PublicError, Notebook, OnenoteSection } from '@microsoft/microsoft-graph-types';
import { DataWriteOptions, Notice, Setting, TFolder, htmlToMarkdown, ObsidianProtocolData, requestUrl, moment } from 'obsidian';
import { genUid, extractErrorMessage, parseHTML, sanitizeFileName } from '../util';
import { FormatImporter } from '../format-importer';
import { ATTACHMENT_EXTS, AUTH_REDIRECT_URI, ImportContext } from '../main';
import { AccessTokenResponse } from './onenote/models';
import { getSiblingsInSameCodeBlock, isFenceCodeBlock, isInlineCodeSpan, isBRElement, isParagraphWrappingOnlyCode } from './onenote/code';
import { inkmlToSvg } from './onenote/inkml';
import { MathMLToLaTeX } from 'mathml-to-latex';

const LOCAL_STORAGE_KEY = 'onenote-importer-refresh-token';
const GRAPH_CLIENT_ID: string = '66553851-08fa-44f2-8bb1-1436f121a73d';
const GRAPH_SCOPES: string[] = ['user.read', 'notes.read'];
// Regex for fixing broken HTML returned by the OneNote API
const SELF_CLOSING_REGEX = /<(object|iframe)([^>]*)\/>/g;
// Regex for fixing whitespace and paragraphs
const PARAGRAPH_REGEX = /(<\/p>)\s*(<p[^>]*>)|\n  \n/g;
// Maximum amount of request retries, before they're marked as failed. Does not include 429 backoff errors.
const MAX_RETRY_ATTEMPTS = 5;

const BASE64_REGEX = new RegExp(/^data:[\w\d]+\/[\w\d]+;base64,/);

type JSONWrappedResponse<T> = {
	value: T[];
} | {
	'@odata.nextLink': string;
	value: T[];
};

function assertUnreachable(x: never): never {
	throw new Error(`Didn't expect to get here`);
}

function assertJSONWrappedResponse<T>(res: unknown): asserts res is JSONWrappedResponse<T> {
	if (res == null) {
		throw new Error(`response is nullish`);
	}
	if (typeof res !== 'object') {
		throw new Error(`response is not an object type`);
	}

	if ('@odata.nextLink' in res) {
		const link = (res as Record<string, unknown>)['@odata.nextLink']; // cast only required because TS version is old
		if (typeof link !== 'string') {
			throw new Error(`Link of unknown type: ${typeof link}`);
		}
	}

	if (!('value' in res)) {
		throw new Error(`Expected response to have a 'value' property`);
	}

	// cast only required because TS version is old
	if (!Array.isArray((res as Record<string, unknown>).value)) {
		throw new Error(`Expected response to have an error in 'value' property`);
	}
}

function isHTMLElement(node: Node): node is HTMLElement {
	return node instanceof HTMLElement;
}

export class OneNoteImporter extends FormatImporter {
	// Settings
	importPreviouslyImported: boolean = false;
	importIncompatibleAttachments: boolean = false;
	// UI
	microsoftAccountSetting: Setting;
	switchUserSetting: Setting;
	loadingArea: HTMLDivElement;
	contentArea: HTMLDivElement;
	// Internal
	selectedIds: string[] = [];
	notebooks: Notebook[] = [];
	graphData = {
		state: genUid(32),
		accessToken: '',
	};
	attachmentDownloadPauseCounter = 0;
	rememberMe = false;
	refreshToken?: string;
	lastSuccessfulFetchTime: number = performance.now();

	async init() {
		this.addOutputLocationSetting('OneNote');

		new Setting(this.modal.contentEl)
			.setName('Import incompatible attachments')
			.setDesc('Imports incompatible attachments which cannot be embedded in Obsidian, such as .exe files.')
			.addToggle((toggle) => toggle
				.setValue(false)
				.onChange((value) => (this.importIncompatibleAttachments = value))
			);

		new Setting(this.modal.contentEl)
			.setName('Skip previously imported')
			.setDesc('If enabled, notes imported previously by this plugin will be skipped.')
			.addToggle((toggle) => toggle
				.setValue(true)
				.onChange((value) => (this.importPreviouslyImported = !value))
			);

		let authenticated = false;
		if (this.retrieveRefreshToken()) {
			try {
				await this.updateAccessToken();
				authenticated = true;
			}
			catch {
				// Failed to auth with refresh token. Proceed with normal sign in flow.
			}
		}

		this.microsoftAccountSetting =
			new Setting(this.modal.contentEl)
				.setName('Sign in with your Microsoft account')
				.setDesc('You need to sign in to import your OneNote data.')
				.addButton((button) => button
					.setCta()
					.setButtonText('Sign in')
					.onClick(() => {
						this.registerAuthCallback(this.authenticateUser.bind(this));

						const requestBody = new URLSearchParams({
							client_id: GRAPH_CLIENT_ID,
							scope: 'offline_access ' + GRAPH_SCOPES.join(' '),
							response_type: 'code',
							redirect_uri: AUTH_REDIRECT_URI,
							response_mode: 'query',
							state: this.graphData.state,
						});
						window.open(`https://login.microsoftonline.com/common/oauth2/v2.0/authorize?${requestBody.toString()}`);
					})
				);
		this.microsoftAccountSetting.settingEl.toggle(!authenticated);

		const rememberMeSetting = new Setting(this.modal.contentEl)
			.setName('Remember me')
			.setDesc('If checked, you will be automatically logged in for subsequent imports.')
			.addToggle((toggle) => {
				toggle.onChange((value) => {
					this.rememberMe = value;
					if (value && this.refreshToken) {
						this.storeRefreshToken(this.refreshToken);
					}
					else {
						this.clearStoredRefreshToken();
					}
				});
			});
		rememberMeSetting.settingEl.toggle(!authenticated);

		this.switchUserSetting = new Setting(this.modal.contentEl)
			.addButton((button) => button
				.setCta()
				.setButtonText('Switch user')
				.onClick(() => {
					this.microsoftAccountSetting.settingEl.show();
					rememberMeSetting.settingEl.show();
					this.clearStoredRefreshToken();
					this.switchUserSetting.settingEl.hide();
					this.contentArea.empty();
				})
			);

		this.loadingArea = this.modal.contentEl.createDiv({
			text: 'Loading notebooks...',
		});
		this.loadingArea.hide();
		this.contentArea = this.modal.contentEl.createDiv();
		this.contentArea.hide();

		if (authenticated) {
			await this.setSwitchUser();
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
			}

			await this.updateAccessToken(protocolData['code']);
			await this.setSwitchUser();
			await this.showSectionPickerUI();
		}
		catch (e) {
			console.error('An error occurred while we were trying to sign you in. Error details: ', e);
			this.modal.contentEl.createEl('div', { text: 'An error occurred while trying to sign you in.' })
				.createEl('details', { text: String(e) })
				.createEl('summary', { text: 'Click here to show error details' });
		}
	}

	async setSwitchUser() {

---

### roam-json.ts

import { ImportContext } from 'main';
import { Notice, Setting, TFile } from 'obsidian';
import { parseFilePath } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { sanitizeFileName } from '../util';
import { BlockInfo, RoamBlock, RoamPage } from './roam/models/roam-json';
import { convertDateString, sanitizeFileNameKeepPath } from './roam/utils';
import { blockRefRegex, extractBlockReferenceUIDs } from './roam/block-refs';
import { moment } from 'obsidian';

const roamSpecificMarkup = ['POMO', 'word-count', 'date', 'slider', 'encrypt', 'TaoOfRoam', 'orphans', 'count', 'character-count', 'comment-button', 'query', 'streak', 'attr-table', 'mentions', 'search', 'roam\/render', 'calc'];
const roamSpecificMarkupRe = new RegExp(`\\{\\{(\\[\\[)?(${roamSpecificMarkup.join('|')})(\\]\\])?.*?\\}\\}(\\})?`, 'g');

const regex = /{{pdf:|{{\[\[pdf|{{\[\[audio|{{audio:|{{video:|{{\[\[video/;
const imageRegex = /https:\/\/firebasestorage(.*?)\?alt(.*?)\)/;
const binaryRegex = /https:\/\/firebasestorage(.*?)\?alt(.*?)/;

export class RoamJSONImporter extends FormatImporter {
	downloadAttachments: boolean = false;
	progress: ImportContext;
	userDNPFormat: string;

	// YAML options
	fileDateYAML: boolean = false;
	titleYAML: boolean = false;

	init() {
		this.addFileChooserSetting('Roam (.json)', ['json']);
		this.addOutputLocationSetting('Roam');
		this.userDNPFormat = this.getUserDNPFormat();

		new Setting(this.modal.contentEl)
			.setName('Import settings')
			.setHeading();

		new Setting(this.modal.contentEl)
			.setName('Download all attachments')
			.setDesc('If enabled, all attachments uploaded to Roam will be downloaded to your attachments folder.')
			.addToggle(toggle => {
				toggle.setValue(this.downloadAttachments);
				toggle.onChange(async (value) => {
					this.downloadAttachments = value;
				});
			});

		new Setting(this.modal.contentEl)
			.setName('Add YAML created/update date')
			.setDesc('If enabled, notes will have the create-time and edit-time from Roam added as properties.')
			.addToggle(toggle => {
				toggle.setValue(this.fileDateYAML);
				toggle.onChange(async (value) => {
					this.fileDateYAML = value;
				});
			});

		new Setting(this.modal.contentEl)
			.setName('Add YAML title')
			.setDesc('If enabled, notes will have the full title added as a property (regardless of illegal file name characters).')
			.addToggle(toggle => {
				toggle.setValue(this.titleYAML);
				toggle.onChange(async (value) => {
					this.titleYAML = value;
				});
			});
	}

	async import(progress: ImportContext) {
		this.progress = progress;
		let { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		let outputFolder = await this.getOutputFolder();
		if (!outputFolder) {
			new Notice('Please select a location to export to.');
			return;
		}

		for (let file of files) {
			if (progress.isCancelled()) {
				return;
			}

			const graphName = sanitizeFileName(file.basename);
			const graphFolder = `${outputFolder.path}/${graphName}`;
			const attachmentsFolder = `${outputFolder.path}/${graphName}/Attachments`;

			// create the base graph folders
			await this.createFolders(graphFolder);
			await this.createFolders(attachmentsFolder);

			// read the graph
			const data = await file.readText();
			const allPages = JSON.parse(data) as RoamPage[];

			// PRE-PROCESS: map the blocks for easy lookup //
			const [blockLocations, toPostProcess] = this.preprocess(allPages);

			const markdownPages: Map<string, string> = new Map();
			for (let index in allPages) {
				const pageData = allPages[index];

				let pageName = convertDateString(sanitizeFileNameKeepPath(pageData.title), this.userDNPFormat).trim();
				if (pageName === '') {
					progress.reportFailed(pageData.uid, 'Title is empty');
					console.error('Cannot import data with an empty title', pageData);
					continue;
				}
				const filename = `${graphFolder}/${pageName}.md`;

				// if title option is enabled
				const YAMLtitle = this.titleYAML ? pageData.title : '';

				// if timestamp option is enabled
				// set up numbers to pass, default to 0
				let pageCreateTimestamp: number = 0;
				let pageEditTimestamp: number = 0;
				if (this.fileDateYAML) {
					// get page creation time and update time
					let pageCreateTime = pageData['create-time'];
					let pageEditTime = pageData['edit-time'];

					// type check both for numbers, set to 0 if there's a type mismatch
					if (typeof pageCreateTime === 'number') {
						pageCreateTimestamp = pageCreateTime;
					}

					if (typeof pageEditTime === 'number') {
						pageEditTimestamp = pageEditTime;
					}
				}

				const markdownOutput = await this.jsonToMarkdown(graphFolder, attachmentsFolder, pageData, '', false, YAMLtitle, pageCreateTimestamp, pageEditTimestamp);
				markdownPages.set(filename, markdownOutput);
			}

			// POST-PROCESS: fix block refs //
			for (const callingBlock of toPostProcess.values()) {
				const callingBlockStringScrubbed = await this.roamMarkupScrubber(graphFolder, attachmentsFolder, callingBlock.blockString, true);
				const newCallingBlockReferences = await this.extractAndProcessBlockReferences(markdownPages, blockLocations, graphFolder, callingBlockStringScrubbed);

				const callingBlockFilePath = `${graphFolder}/${callingBlock.pageName}.md`;
				const callingBlockMarkdown = markdownPages.get(callingBlockFilePath);
				if (callingBlockMarkdown) {
					let lines = callingBlockMarkdown.split('\n');

					let index = lines.findIndex((item: string) => item.contains('* ' + callingBlockStringScrubbed));
					if (index !== -1) {
						lines[index] = lines[index].replace(callingBlockStringScrubbed, newCallingBlockReferences);
					}

					markdownPages.set(callingBlockFilePath, lines.join('\n'));
				}
			}

			// WRITE-PROCESS: create the actual pages //
			const { vault } = this;
			const totalCount = markdownPages.size;
			let index = 1;
			for (const [filename, markdownOutput] of markdownPages.entries()) {
				if (progress.isCancelled()) {
					return;
				}

				try {
					//create folders for nested pages [[some/nested/subfolder/page]]
					const { parent } = parseFilePath(filename);
					await this.createFolders(parent);
					const existingFile = vault.getAbstractFileByPath(filename) as TFile;
					if (existingFile) {
						await vault.modify(existingFile, markdownOutput);
					}
					else {
						await vault.create(filename, markdownOutput);
					}
					progress.reportNoteSuccess(filename);
					progress.reportProgress(index, totalCount);
				}
				catch (error) {
					console.error('Error saving Markdown to file:', filename, error);
					progress.reportFailed(filename);
				}

				index++;
			}
		}
	}

	private getUserDNPFormat(): string {
		// @ts-expect-error : Internal Method
		const dailyNotePluginInstance = this.app.internalPlugins.getPluginById('daily-notes').instance;
		if (!dailyNotePluginInstance) {
			console.log('Daily note plugin is not enabled. Roam import defaulting to "YYYY-MM-DD" format.');
			return 'YYYY-MM-DD';
		}

		let dailyPageFormat = dailyNotePluginInstance.options.format;
		return dailyPageFormat || 'YYYY-MM-DD';

---

### textbundle.ts

import { normalizePath, Notice, TFolder, Platform } from 'obsidian';
import { parseFilePath, NodePickedFolder, NodePickedFile, PickedFile, PickedFolder } from '../filesystem';
import { FormatImporter } from '../format-importer';
import { ProgressReporter } from '../main';
import { readZip, ZipEntryFile } from 'zip';

const assetMatcher = /!\[\]\(assets\/([^)]*)\)/g;

export class TextbundleImporter extends FormatImporter {
	private attachmentsFolderPath: TFolder;

	init() {
		if (!Platform.isMacOS) {
			this.modal.contentEl.createEl('p', {
				text:
					'Due to platform limitations, only textpack and zip files can be imported from this device.' +
					' Open your vault on a Mac to import textbundle files.'
			});
		}

		const formats = Platform.isMacOS
			? ['textbundle', 'textpack', 'zip']
			: ['textpack', 'zip'];

		this.addFileChooserSetting('Textbundle', formats, true);
		this.addOutputLocationSetting('Textbundle');
	}

	async import(progress: ProgressReporter): Promise<void> {
		let { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		let folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		this.attachmentsFolderPath = await this.createFolders(`${folder.path}/assets`);

		for (let file of files) {
			if (file.extension === 'textpack') {
				await readZip(file, async (zip, entries) => {
					await this.process(progress, file.name, entries);
				});
			}
			else if (file.extension === 'zip') {
				await readZip(file, async (zip, entries) => {
					const textbundles = this.groupFilesByTextbundle(file.name, entries);
					for (const textbundle of textbundles) {
						await this.process(progress, file.name, textbundle);
					}
				});
			}
			else {
				let textbundleFolder = new NodePickedFolder(`${file.toString()}/`);
				let entries = await textbundleFolder.list();
				await this.process(progress, file.name, entries);
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
			}

			const path = entry.fullpath.slice(prefix.length);
			if (path.startsWith('._') || path.startsWith('__MACOSX')) {
				console.log('Skipping', entry.fullpath);
				continue;
			}

			const idx = path.indexOf(dotTextbundle);
			if (idx === -1) {
				console.log('Skipping', entry.fullpath);
				continue;
			}

			const textBundle = path.slice(0, idx) + '.textbundle';
			const rest = path.slice(idx + dotTextbundle.length + 1); // Skip the '.textbundle' and path separator

			if (rest.startsWith('._')) {
				console.log('Skipping', entry.fullpath);
				continue;
			}

			if (textBundle in buckets) {
				buckets[textBundle].push(entry);
			}
			else {
				buckets[textBundle] = [entry];
			}
		}

		return Object.values(buckets);
	}

	async process(progress: ProgressReporter, bundleName: string, entries: (PickedFile | PickedFolder | ZipEntryFile)[]) {
		// First look for the info.json and check that the file type is Markdown
		const infojson = entries.find((entry) => entry.name === 'info.json');
		if (infojson) {
			const text = await (infojson as NodePickedFile).readText();
			const parsed = JSON.parse(text);
			if (parsed.hasOwnProperty('type') && parsed.type !== 'net.daringfireball.markdown') {
				progress.reportSkipped(bundleName, 'The textbundle does not contain markdown');
				return;
			}
		}

		for (let entry of entries) {
			if (entry.name.startsWith('._')) {
				// We don't need to notify users that we're skipping these hidden files.
				// progress.reportSkipped(entry.name, 'skipping system file.');
				continue;
			}

			try {
				if (entry.type === 'file' && (entry.extension === 'md' || entry.extension === 'markdown')) {
					let mdFilename = 'parent' in entry
						? entry.parent
						: bundleName;
					mdFilename = mdFilename.replace(/.textbundle$/, '');

					let mdContent = await (entry as NodePickedFile).readText();
					if (mdContent.match(assetMatcher)) {
						// Replace asset paths with new asset folder path.
						mdContent = mdContent.replace(assetMatcher, `![[${this.attachmentsFolderPath.path}/$1]]`);
					}
					let filePath = normalizePath(mdFilename);
					const outputFolder = await this.getOutputFolder();
					// We already asserted previously that the result from getOutputFolder is not null.
					await this.saveAsMarkdownFile(outputFolder!, filePath, mdContent);
					progress.reportNoteSuccess(mdFilename);
				}
				else if (entry.type === 'file' && entry.fullpath.contains('assets/')) {
					await this.importAsset(progress, entry);
				}
				else if (entry.type === 'folder') {
					let { basename } = parseFilePath(entry.toString());
					if (basename !== 'assets') {
						continue;
					}

					let assetFolder = new NodePickedFolder(`${entry.toString()}/`);
					let entries = await assetFolder.list();
					for (let entry of entries) {
						await this.importAsset(progress, entry);
					}
				}
				else if (entry.name !== 'info.json') {
					progress.reportSkipped(entry.name, 'the file is not a media or markdown file.');
				}
			}
			catch (e) {
				progress.reportFailed(entry.name, e);
			}
		}
	}

	async importAsset(progress: ProgressReporter, entry: PickedFile | PickedFolder | ZipEntryFile): Promise<void> {
		if (entry.type === 'folder') {
			progress.reportSkipped(entry.name);
			return;
		}

		let assetFileVaultPath = `${this.attachmentsFolderPath.path}/${entry.name}`;
		let existingFile = this.vault.getAbstractFileByPath(assetFileVaultPath);
		if (existingFile) {
			progress.reportSkipped(entry.name, 'the file already exists.');
		}

		let assetData = await entry.read();
		await this.vault.createBinary(assetFileVaultPath, assetData);
		progress.reportAttachmentSuccess(entry.name);
	}
}


---

### tomboy.ts

import { Notice, Setting, ToggleComponent, DropdownComponent, Platform } from 'obsidian';
import { FormatImporter } from '../format-importer';
import { ImportContext } from '../main';
import { TomboyCoreConverter, KeepTitleMode } from './tomboy/core';
import { os, path } from '../filesystem';

export class TomboyImporter extends FormatImporter {
	private coreConverter: TomboyCoreConverter;
	private todoEnabled: boolean;
	private keepTitleMode: KeepTitleMode;

	/**
	 * Get the default Tomboy/Gnote directory path based on the current OS
	 */
	private getDefaultTomboyPath(): string {
		if (!Platform.isDesktopApp || !os || !path) {
			return '';
		}

		try {
			if (Platform.isMacOS) {
				const macPath = path.join(os.homedir(), 'Library', 'Application Support', 'Tomboy');
				return macPath;
			}
			else if (Platform.isWin) {
				const windowsPath = path.join(process.env.APPDATA || '', 'Roaming', 'Tomboy');
				return windowsPath;
			}
			else if (Platform.isLinux) {
				const homeDir = os.homedir();
				return path.join(homeDir, '.local', 'share', 'tomboy');
			}
		}
		catch (e) {
			console.warn('Error detecting default Tomboy path:', e);
		}
		
		return '';
	}

	/**
	 * Get descriptive text for OS-specific Tomboy/Gnote locations
	 */
	private getOSSpecificDescription(): string {
		if (Platform.isMacOS) {
			return 'Tomboy notes are typically found in: ~/Library/Application Support/Tomboy';
		}
		else if (Platform.isWin) {
			return 'Tomboy notes are typically found in: %APPDATA%\\Tomboy';
		}
		else if (Platform.isLinux) {
			return 'Tomboy notes are typically found in: ~/.local/share/tomboy - or GNote: ~/.local/share/gnote';
		}
		return 'Pick the files that you want to import.';
	}

	init() {
		this.todoEnabled = true;
		this.coreConverter = new TomboyCoreConverter();
		this.keepTitleMode = 'automatic';

		this.addFileChooserSetting('Tomboy/Gnote', ['note'], true, this.getOSSpecificDescription(), this.getDefaultTomboyPath());
		this.addOutputLocationSetting('Tomboy');

		new Setting(this.modal.contentEl)
			.setName('Convert TODO lists to checkboxes')
			.setDesc('When enabled, lists in notes with "TODO" in the title will be converted to task lists with checkboxes. Strikethrough items will be marked as completed.')
			.addToggle((toggle: ToggleComponent) => {
				toggle.setValue(this.todoEnabled)
					.onChange((value: boolean) => this.todoEnabled = value);
			});

		new Setting(this.modal.contentEl)
			.setName('Keep title in Markdown')
			.setDesc('Choose whether to keep the note title in the Markdown content. "Automatic" keeps titles only when special characters are lost in filename conversion.')
			.addDropdown((dropdown: DropdownComponent) => {
				dropdown.addOption('automatic', 'Automatic')
					.addOption('yes', 'Keep titles')
					.addOption('no', 'Filename only')
					.setValue(this.keepTitleMode)
					.onChange((value: string) => this.keepTitleMode = value as KeepTitleMode);
			});
	}

	async import(ctx: ImportContext): Promise<void> {
		const { files } = this;
		if (files.length === 0) {
			new Notice('Please pick at least one file to import.');
			return;
		}

		const folder = await this.getOutputFolder();
		if (!folder) {
			new Notice('Please select a location to export to.');
			return;
		}

		this.coreConverter.setTodoEnabled(this.todoEnabled);
		this.coreConverter.setKeepTitleMode(this.keepTitleMode);

		ctx.reportProgress(0, files.length);
		for (let i = 0; i < files.length; i++) {
			if (ctx.isCancelled()) return;

			const file = files[i];
			ctx.status('Processing ' + file.name);
			try {
				await this.processFile(ctx, folder, file);
				ctx.reportNoteSuccess(file.fullpath);
			}
			catch (e) {
				ctx.reportFailed(file.fullpath, e);
			}

			ctx.reportProgress(i + 1, files.length);
		}
	}

	private async processFile(ctx: ImportContext, folder: any, file: any): Promise<void> {
		const xmlContent = await file.readText();

		const tomboyNote = this.coreConverter.parseTomboyXML(xmlContent);
		const markdownContent = this.coreConverter.convertToMarkdown(tomboyNote);

		await this.saveAsMarkdownFile(folder, tomboyNote.title, markdownContent);
	}
}


---



## Base Importer Interface

import { path } from './filesystem';
import { TFolder, TFile, BasesConfigFile, stringifyYaml, normalizePath } from 'obsidian';

/**
 * Creates a Base file in the specified folder.
 * 
 * @param folder - The folder to create the Base file in
 * @param fileName - Name of the Base file (without .base extension)
 * @param options - Configuration for the Base file content
 * @param vault - Obsidian vault instance
 * @returns The created TFile
 * 
 * @example
 * ```ts
 * await createBaseFile(folder, 'CSV import', {
 *   filters: 'file.folder == "CSV import"',
 *   views: [{
 *     type: 'table',
 *     name: 'Table',
 *     order: ['file.name', 'title', 'date', 'category']
 *   }]
 * }, this.app.vault);
 * ```
 */
export async function createBaseFile(
	folder: TFolder,
	fileName: string,
	contents: BasesConfigFile,
	vault: any
): Promise<TFile> {
	const yamlContent = stringifyYaml(contents);
	const filePath = normalizePath(path.join(folder.path, fileName + '.base'));

	// Check if file already exists
	const existingFile = vault.getAbstractFileByPath(filePath);
	if (existingFile instanceof TFile) {
		// Update existing file
		await vault.modify(existingFile, yamlContent);
		return existingFile;
	}

	// Create new file
	return await vault.create(filePath, yamlContent);
}



## Filesystem Utilities

import { BlobReader, configure, Reader, ZipReader } from '@zip.js/zip.js';
import type * as NodeFS from 'node:fs';
import type * as NodeOS from 'node:os';
import type * as NodePath from 'node:path';
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
	readonly name: string;
	/** Base file name, without extension */
	readonly basename: string;
	/** Lowercase extension */
	readonly extension: string;

	/** Read the file as utf8 text */
	readText(): Promise<string>;

	/** Read the file as binary */
	read(): Promise<ArrayBuffer>;

	/** Read the file as zip, processing the zip in the callback */
	readZip(callback: (zip: ZipReader<any>) => Promise<void>): Promise<void>;
}

export interface PickedFolder {
	readonly type: 'folder';
	/** Folder name */
	readonly name: string;
	/** List files in this folder */
	list: () => Promise<(PickedFile | PickedFolder)[]>;
}

export const fs: typeof NodeFS = Platform.isDesktopApp ? window.require('node:original-fs') : null;
export const fsPromises: typeof NodeFS.promises = Platform.isDesktopApp ? fs.promises : null!;
export const os: typeof NodeOS = Platform.isDesktopApp ? window.require('node:os') : null;
export const path: typeof NodePath = Platform.isDesktopApp ? window.require('node:path') : null;
export const url: typeof NodeUrl = Platform.isDesktopApp ? window.require('node:url') : null;
export const zlib: typeof NodeZlib = Platform.isDesktopApp ? window.require('node:zlib') : null;

export function nodeBufferToArrayBuffer(buffer: Buffer<ArrayBuffer>, offset = 0, length = buffer.byteLength - offset): ArrayBuffer {
	return buffer.buffer.slice(buffer.byteOffset + offset, buffer.byteOffset + offset + length);
}

export class NodePickedFile implements PickedFile {
	readonly type: 'file' = 'file';
	readonly filepath: string;

	readonly fullpath: string;
	readonly name: string;
	readonly basename: string;
	readonly extension: string;

	constructor(filepath: string) {
		this.filepath = filepath;
		let name = this.name = path.basename(filepath);
		// Use only the name here since the parent folder isn't relevant
		this.fullpath = name;
		// Extension with dot
		let extension = path.extname(name);
		// Extension without dot
		this.extension = extension.substring(1).toLowerCase();
		this.basename = path.basename(name, extension);
	}

	async readText(): Promise<string> {
		return fsPromises.readFile(this.filepath, 'utf8');
	}

	async read(): Promise<ArrayBuffer> {
		let buffer = await fsPromises.readFile(this.filepath);
		return nodeBufferToArrayBuffer(buffer);
	}

	async readZip(callback: (zip: ZipReader<any>) => Promise<void>): Promise<void> {
		let fd: NodeFS.promises.FileHandle | null = null;
		try {
			fd = await fsPromises.open(this.filepath, 'r');
			let stat = await fd.stat();
			return await callback(new ZipReader(new FSReader(fd, stat.size)));
		}
		finally {
			await fd?.close();
		}
	}

	createReadStream() {
		return fs.createReadStream(this.filepath);
	}

	toString(): string {
		return this.filepath;
	}
}

export class NodePickedFolder implements PickedFolder {
	readonly type: 'folder' = 'folder';
	readonly filepath: string;

	readonly name: string;

	constructor(filepath: string) {
		this.filepath = filepath;
		this.name = path.basename(filepath);
	}

	async list(): Promise<(PickedFile | PickedFolder)[]> {
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
		}

		return results;
	}

	toString(): string {
		return this.filepath;
	}
}

export class WebPickedFile implements PickedFile {
	readonly type: 'file' = 'file';
	readonly file: File;

	readonly fullpath: string;
	readonly name: string;
	readonly basename: string;
	readonly extension: string;

	constructor(file: File) {
		this.file = file;
		let name = this.name = file.name;
		this.fullpath = name;

		let { basename, extension } = parseFilePath(name);

		this.basename = basename;
		this.extension = extension;
	}

	readText(): Promise<string> {
		let { file } = this;
		if (file.text) {
			return file.text();
		}
		return new Promise((resolve, reject) => {
			let reader = new FileReader();
			reader.addEventListener('load', () => resolve(reader.result as string));
			reader.addEventListener('error', reject);
			reader.readAsText(this.file);
		});
	}

	async read(): Promise<ArrayBuffer> {
		let { file } = this;
		if (file.arrayBuffer) {
			return file.arrayBuffer();
		}
		return new Promise((resolve, reject) => {
			let reader = new FileReader();
			reader.addEventListener('load', () => resolve(reader.result as ArrayBuffer));
			reader.addEventListener('error', reject);
			reader.readAsArrayBuffer(this.file);
		});
	}

	async readZip(callback: (zip: ZipReader<any>) => Promise<void>): Promise<void> {
		return callback(new ZipReader(new BlobReader(this.file)));
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
			else if (file.type === 'file') {
				if (!filter || filter(file)) {
					results.push(file);
				}
			}
		}
		catch (e) {
			console.log('Skipping path: ', file.name, e);
		}
	}
	return results;
}

/**
 * Parse a filepath to get a file's parent path, name, basename (name without extension), and extension (lowercase).
 * For example, "path/to/my/file.md" would become `{parent: "path/to/my", name: "file.md", basename: "file", extension: "md"}`
 */
export function parseFilePath(filepath: string): { parent: string, name: string, basename: string, extension: string } {
	let lastIndex = Math.max(filepath.lastIndexOf('/'), filepath.lastIndexOf('\\'));
	let name = filepath;
	let parent = '';
	if (lastIndex >= 0) {
		name = filepath.substring(lastIndex + 1);
		parent = filepath.substring(0, lastIndex);
	}

	let [basename, extension] = splitext(name);
	return { parent, name, basename, extension };
}

export function splitext(name: string) {
	let dotIndex = name.lastIndexOf('.');
	let basename = name;
	let extension = '';
	
	if (dotIndex > 0) {
		basename = name.substring(0, dotIndex);
		extension = name.substring(dotIndex + 1).toLowerCase();
	}
	
	return [basename, extension];
}

class FSReader extends Reader<NodeFS.promises.FileHandle> {
	fd: NodeFS.promises.FileHandle;

	constructor(fd: NodeFS.promises.FileHandle, size: number) {
		super(fd);
		this.fd = fd;
		this.size = size;
	}

	async readUint8Array(offset: number, length: number) {
		let buffer = Buffer.alloc(length);
		let result = await this.fd.read(buffer, 0, length, offset);
		return new Uint8Array(nodeBufferToArrayBuffer(buffer, 0, result.bytesRead));
	}
}


## File Format Importer Interface

import { App, normalizePath, Platform, Setting, TFile, TFolder, Vault } from 'obsidian';
import { getAllFiles, NodePickedFile, NodePickedFolder, path, parseFilePath, PickedFile, WebPickedFile } from './filesystem';
import { ImporterModal, ImportContext, AuthCallback } from './main';
import { sanitizeFileName } from './util';

const MAX_PATH_DESCRIPTION_LENGTH = 300;

export abstract class FormatImporter {
	app: App;
	vault: Vault;
	modal: ImporterModal;

	files: PickedFile[] = [];
	outputLocation: string = '';
	notAvailable: boolean = false;

	/** Cached value for getOutputFolder. Do not use directly. */
	private outputFolder: TFolder | null = null;

	constructor(app: App, modal: ImporterModal) {
		this.app = app;
		this.vault = app.vault;
		this.modal = modal;
		this.init();
	}

	abstract init(): void;

	/**
	 * Optional: Show template configuration UI and prepare data for import.
	 * This will be called as a configuration step before the import progress.
	 *
	 * Overriding functions are responsible for displaying errors before returning false.
	 *
	 * @param ctx The import context
	 * @param container The container element to show the configuration UI in
	 * @returns true if configuration was successful, false if cancelled or failed, null if no configuration needed
	 */
	async showTemplateConfiguration(ctx: ImportContext, container: HTMLElement): Promise<boolean | null> {
		return null;
	}

	/**
	 * Register a function to be called when the `obsidian://importer-auth/` open
	 * event is received by Obsidian.
	 *
	 * Note: The callback will be cleared after being called. It must be
	 * reregistered if a subsequent auth event is expected.
	 */
	registerAuthCallback(callback: AuthCallback): void {
		this.modal.plugin.registerAuthCallback(callback);
	}

	addFileChooserSetting(name: string, extensions: string[], allowMultiple: boolean = false, description?: string, defaultPath?: string) {
		let fileLocationSetting = new Setting(this.modal.contentEl)
			.setName('Files to import')
			.setDesc(description || 'Pick the files that you want to import.')
			.addButton(button => button
				.setButtonText(allowMultiple ? 'Choose files' : 'Choose file')
				.onClick(async () => {
					if (Platform.isDesktopApp) {
						let properties = ['openFile', 'dontAddToRecent'];
						if (allowMultiple) {
							properties.push('multiSelections');
						}
						let filePaths: string[] = window.electron.remote.dialog.showOpenDialogSync({
							title: 'Pick files to import', properties,
							filters: [{ name, extensions }],
							defaultPath: defaultPath || undefined,
						});

						if (filePaths && filePaths.length > 0) {
							this.files = filePaths.map((filepath: string) => new NodePickedFile(filepath));
							updateFiles();
						}
					}
					else {
						let inputEl = createEl('input');
						inputEl.type = 'file';
						inputEl.accept = extensions.map(e => '.' + e.toLowerCase()).join(',');
						inputEl.addEventListener('change', () => {
							if (!inputEl.files) return;
							let files = Array.from(inputEl.files);
							if (files.length > 0) {
								this.files = files.map(file => new WebPickedFile(file))
									.filter(file => extensions.contains(file.extension));
								updateFiles();
							}
						});
						inputEl.click();
					}
				}));

		if (allowMultiple && Platform.isDesktopApp) {
			fileLocationSetting.addButton(button => button
				.setButtonText('Choose folders')
				.onClick(async () => {
					if (Platform.isDesktopApp) {
						let filePaths: string[] = window.electron.remote.dialog.showOpenDialogSync({
							title: 'Pick folders to import',
							properties: ['openDirectory', 'multiSelections', 'dontAddToRecent'],
							defaultPath: defaultPath || undefined,
						});

						if (filePaths && filePaths.length > 0) {
							fileLocationSetting.setDesc('Reading folders...');
							let folders = filePaths.map((filepath: string) => new NodePickedFolder(filepath));
							this.files = await getAllFiles(folders, (file: PickedFile) => extensions.contains(file.extension));
							updateFiles();
						}
					}
				}));
		}

		let updateFiles = () => {
			let descriptionFragment = document.createDocumentFragment();
			let fileCount = this.files.length;
			let pathText = this.files.map(f => f.name).join(', ');
			if (pathText.length > MAX_PATH_DESCRIPTION_LENGTH) {
				pathText = pathText.substring(0, MAX_PATH_DESCRIPTION_LENGTH) + '...';
			}
			descriptionFragment.createEl('span', { text: `These ${fileCount} files will be imported: ` });
			descriptionFragment.createEl('br');
			descriptionFragment.createEl('span', { cls: 'u-pop', text: pathText });
			fileLocationSetting.setDesc(descriptionFragment);
		};
	}

	addOutputLocationSetting(defaultExportFolderName: string) {
		this.outputLocation = defaultExportFolderName;
		new Setting(this.modal.contentEl)
			.setName('Output folder')
			.setDesc('Choose a folder in the vault to put the imported files. Leave empty to output to vault root.')
			.addText(text => text
				.setValue(defaultExportFolderName)
				.onChange(value => {
					this.outputLocation = value;
					this.outputFolder = null;
				}));
	}

	async getOutputFolder(): Promise<TFolder | null> {
		if (this.outputFolder) {
			return this.outputFolder;
		}

		let { vault } = this.app;

		let folderPath = this.outputLocation;
		if (folderPath === '') {
			folderPath = '/';
		}
		folderPath = normalizePath(folderPath);

		let folder = vault.getAbstractFileByPath(folderPath);

		if (folder === null || !(folder instanceof TFolder)) {
			await vault.createFolder(folderPath);
			folder = vault.getAbstractFileByPath(folderPath);
		}

		if (folder instanceof TFolder) {
			this.outputFolder = folder;
			return folder;
		}

		return null;
	}

	/**
	 * Resolves a unique path for the attachment file being saved.
	 * Ensures that the parent directory exists and dedupes the
	 * filename if the destination filename already exists.
	 *
	 * NOTE: This is a duplicate of `fileManager.getAvailablePathForAttachment`
	 * which adds two key adjustments to aid Importer:
	 *   - Use the provided `sourcePath` even if the file doesn't exist yet.
	 *   - Avoid duplicating a list of provided filesnames that do not yet exist, but will in the future.
	 *
	 * @param filename Name of the attachment being saved
	 * @param claimedPaths List of filepaths that may not exist yet but will in the future.
	 * @param sourcePath Optional path of the current file being imported (for "Same folder as current file" setting)
	 * @returns Full path for where the attachment should be saved, according to the user's settings
	 */
	async getAvailablePathForAttachment(filename: string, claimedPaths: string[], sourcePath?: string): Promise<string> {
		let sourceFile: TFile | null = null;
		
		// If sourcePath is provided, use its parent folder for attachment placement
		// This is important for respecting user's "Same folder as current file" setting
		if (sourcePath) {
			const { parent } = parseFilePath(sourcePath);
			if (parent) {
				const parentFolder = this.vault.getAbstractFileByPath(normalizePath(parent));
				if (parentFolder instanceof TFolder) {
					sourceFile = { parent: parentFolder } as TFile;
				}
			}
		}
		
		// Fallback to outputFolder if sourcePath not provided or parent folder not found
		if (!sourceFile) {
			const outputFolder = await this.getOutputFolder();
			// XXX: (Ab)use the fact that getAvailablePathForAttachments only looks sourceFile.parent.
			sourceFile = !!outputFolder
				? { parent: outputFolder } as TFile
				: null;
		}

		const { basename, extension } = parseFilePath(filename);

		// Use getAvailablePathForAttachments because it can give us the configured output path.
		//@ts-ignore
		const prelimOutPath = await this.vault.getAvailablePathForAttachments(basename, extension, sourceFile);
		const parsedPrelimOutPath = parseFilePath(prelimOutPath);

		const fullExt = parsedPrelimOutPath.extension ?
			'.' + parsedPrelimOutPath.extension
			: '.' + extension;

		// Increase number until the path is unique.
		let i = 1;
		let outputPath = prelimOutPath;
		while (claimedPaths.includes(outputPath) || !!this.vault.getAbstractFileByPath(outputPath)) {
			outputPath = path.join(parsedPrelimOutPath.parent, `${parsedPrelimOutPath.name} ${i}${fullExt}`);
			i++;
		}

		// Normalize the final outputPath before returning
		return normalizePath(outputPath);
	}

	async pause(durationSeconds: number, reason: string, ctx: ImportContext | undefined): Promise<void> {
		const promise = new Promise(resolve => setTimeout(resolve, durationSeconds * 1_000));

		if (ctx) {
			const previousStatusMessage = ctx.statusMessage;
			ctx.status(`⏸️ Pausing import for ${durationSeconds} seconds (${reason})`);
			await promise;
			ctx.status(previousStatusMessage);
		}
		else {
			await promise;
		}
	}

	abstract import(ctx: ImportContext): Promise<any>;

	// Utility functions for vault

	/** Remove any characters that would be illegal on any platform. */
	sanitizeFilePath(path: string): string {
		return path.replace(/[:|?<>*\\]/g, '');
	}

	/**
	 * Recursively create folders, if they don't exist.
	 */
	async createFolders(path: string): Promise<TFolder> {
		// can't create folders starting with a dot
		const sanitizedPath = path.split('/').map(segment => segment.replace(/^\.+/, '')).join('/');
		let normalizedPath = normalizePath(sanitizedPath);
		let folder = this.vault.getAbstractFileByPathInsensitive(normalizedPath);
		if (folder && folder instanceof TFolder) {
			return folder;
		}

		await this.vault.createFolder(normalizedPath);
		folder = this.vault.getAbstractFileByPathInsensitive(normalizedPath);
		if (!(folder instanceof TFolder)) {
			throw new Error(`Failed to create folder at "${path}"`);
		}

		return folder;
	}

	async saveAsMarkdownFile(folder: TFolder, title: string, content: string): Promise<TFile> {
		let sanitizedName = sanitizeFileName(title);
		// @ts-ignore
		return await this.app.fileManager.createNewMarkdownFile(folder, sanitizedName, content);
	}
}


## README

![Obsidian Importer screenshot](/images/social.png)

This Obsidian plugin allows you to import notes from other apps and file formats into your Obsidian vault. Notes are converted to plain text Markdown files.

## Get started

Install Importer in Obsidian → Community Plugins.

Import guides are hosted on the [official Obsidian Help site](https://help.obsidian.md/import). You can help contribute to the guides on the [obsidian-help](https://github.com/obsidianmd/obsidian-help) repo.

- [Import from Apple Notes](https://help.obsidian.md/import/apple-notes)
- [Import from Bear](https://help.obsidian.md/import/bear)
- [Import from CSV files](https://help.obsidian.md/import/csv)
- [Import from Evernote](https://help.obsidian.md/import/evernote)
- [Import from Google Keep](https://help.obsidian.md/import/google-keep)
- [Import from Microsoft OneNote](https://help.obsidian.md/import/onenote)
- [Import from Notion](https://help.obsidian.md/import/notion)
- [Import from Roam Research](https://help.obsidian.md/import/roam)
- [Import from HTML files](https://help.obsidian.md/import/html)
- [Import from Markdown files](https://help.obsidian.md/import/markdown)
- Import from Apple Journal (HTML export)

## Contributing

Importer is a community-led project. You can explore pull requests and see the credits below for reference. The Obsidian team is not actively working on adding new import capabilities, but we welcome pull requests for new formats and improvements.

Is a format missing? You can help! See our [Contribution guidelines](/CONTRIBUTING.md).

Some issues have been [tagged with #bounty](https://github.com/obsidianmd/obsidian-importer/labels/bounty).

## Credits

This plugin relies on important contributions:

- [@akosbalasko](https://github.com/akosbalasko) for Evernote import via [Yarle](https://github.com/akosbalasko/yarle) (MIT)
- [@daledesilva](https://github.com/daledesilva) for Google Keep import
- [@arthurtyukayev](https://github.com/arthurtyukayev) for Bear import
- [@xheldon](https://github.com/Xheldon) for Notion API import
- [@joshuatazrein](https://github.com/joshuatazrein) for Notion file-based import
- [@polyipseity](https://github.com/polyipseity) for HTML attachments
- [@8bitgentleman](https://github.com/8bitgentleman) for Roam import
- [@p3rid0t](https://github.com/p3rid0t) for Microsoft OneNote import
- [@mirnovov](https://github.com/mirnovov) for Apple Notes import
- [@wzs](https://github.com/wzs) for Apple Journal import

