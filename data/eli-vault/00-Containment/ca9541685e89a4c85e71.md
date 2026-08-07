---
id: b6d6eacab3927feb
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: ca9541685e89a4c85e71
createdAt: 1786051359181
embeddingSig: "args:bash:macopener|args:bash:wezterm|args:kitty:args|bash:macopener:open|bash:wezterm:label|kitty:args:bash|label:wezterm:appname|macopener:open:args|open:args:kitty|opener:args:bash|wezterm:appname:wezterm|wezterm:label:wezterm"
---
Opener: (bin, s) => ({ bin, args: ["bash", s] }),
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-na", "kitty", "--args", "bash", s] }),
  },
  {
    id: "wezterm",
    label: "WezTerm",
    appName: "WezTerm",
    binName: "wezterm",
    binOpener: (bin, s) => ({ bin, args: ["start", "--", "bash", s] }),
    macOpener: (s) => ({ bin: "/usr/bin/open", args: ["-na", "WezTerm", "--args", "start", "--", "bash", s] }),