---
id: 82ea36553f4cacf3
source: "obsidian-importer-reference.md"
"title: Obsidian Importer — Format Conversion Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: ee37dbf5201a58cac5ca
createdAt: 1786051357436
embeddingSig: "application:support:tomboy|const:macpath:path|homedir:library:application|isdesktopapp:path:return|ismacos:const:macpath|join:homedir:library|library:application:support|macpath:path:join|path:join:homedir|path:return:platform|platform:ismacos:const|return:platform:ismacos"
---
orm.isDesktopApp || !os || !path) {
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