---
id: 7c7c95a5a6b44506
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool", "code"]
containmentHash: 0bd7cb863ea27ea4e3cc
createdAt: 1786051359181
embeddingSig: "agentarg:argv:push|agentarg:isvalidomnigentserver:server|argv:binarypath:agentarg|argv:push:agentarg|binarypath:agentarg:argv|const:argv:binarypath|isvalidomnigentserver:server:argv|omnigent:const:argv|push:agentarg:isvalidomnigentserver|ssion:string:tool|string:tool:omnigent|tool:omnigent:const"
---
ssion): string[] {
  if (s.tool === "omnigent") {
    const argv = [s.binaryPath, "run"];
    if (s.agentArg) argv.push(s.agentArg);
    if (isValidOmnigentServer(s.server)) argv.push("--server", s.server.trim());
    if (s.harness) argv.push("--harness", s.harness);
    argv.push("-c");
    return argv;
  }
  if (s.tool === "claude") return [s.binaryPath, "--continue"];