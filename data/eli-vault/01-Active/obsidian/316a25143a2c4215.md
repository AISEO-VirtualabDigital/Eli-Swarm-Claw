---
id: 316a25143a2c4215
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["pattern"]
containmentHash: 3beaa179a7f3cc9a3a3e
createdAt: 1786051357436
embeddingSig: "always:quote:line|char:always:quote|currentline:skip:next|escaped:quote:second|inquotes:nextchar:escaped|line:char:always|line:inquotes:nextchar|nextchar:escaped:quote|quote:currentline:skip|quote:line:inquotes|quote:second:quote|second:quote:currentline"
---
Line += char; // Always add the quote to the line
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