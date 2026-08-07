---
id: bfe4f19caccc592a
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["code"]
containmentHash: 66d5098fb4ba57927adc
createdAt: 1786051359181
embeddingSig: "binname:string:homedir|export:function:terminalbincandidates|function:terminalbincandidates:binname|homedir:string:platform|posix:windows:export|probed:posix:windows|string:homedir:string|string:platform:nodejs|terminal:tmux:probed|terminalbincandidates:binname:string|tmux:probed:posix|windows:export:function"
---
I terminal (tmux) is probed in (POSIX / Windows). */
export function terminalBinCandidates(
  binName: string,
  homedir: string,
  platform: NodeJS.Platform = process.platform,
): string[] {
  if (platform === "win32") {
    return [".exe", ".cmd", ".bat", ""].map((ext) =>
      nodePath.join(homedir, ".local", "bin", binName + ext),
    );
  }
  return [
    `/opt/homebrew/bin/${binName}`,
    `/usr/local/bin/${binName}`,