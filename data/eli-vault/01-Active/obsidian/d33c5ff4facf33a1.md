---
id: d33c5ff4facf33a1
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 3fd5a43990d7cd1ae393
createdAt: 1786051357436
embeddingSig: "content:string:headers|headers:string:rows|length:return:value|parsecsv:content:string|private:parsecsv:content|return:private:parsecsv|return:value:return|rows:csvrow:const|string:headers:string|string:rows:csvrow|trim:length:return|value:return:private"
---
e.trim().length > 0) {
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