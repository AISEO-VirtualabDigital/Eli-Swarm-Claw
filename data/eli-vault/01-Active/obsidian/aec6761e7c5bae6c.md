---
id: aec6761e7c5bae6c
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 26df85a1d7722051ac5a
createdAt: 1786051359181
embeddingSig: "able:export:function|export:function:omnigentcandidatepaths|function:omnigentcandidatepaths:override|homedir:string:platform|nodejs:platform:process|omnigentcandidatepaths:override:string|override:string:undefined|platform:nodejs:platform|platform:process:platform|string:platform:nodejs|string:undefined:homedir|undefined:homedir:string"
---
able.
 */
export function omnigentCandidatePaths(
  override: string | undefined,
  homedir: string,
  platform: NodeJS.Platform = process.platform,
): string[] {
  const candidates: string[] = [];
  const ov = override?.trim();
  if (ov) candidates.push(ov);
  if (platform === "win32") {
    // Windows: uv-installed tools live under %USERPROFILE%\.local\bin; the binary
    // carries an executable extension.