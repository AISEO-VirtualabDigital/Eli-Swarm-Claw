---
id: 8f79b4fcf8fe8bca
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["pattern"]
containmentHash: be8686e3dfa5ac67786b
createdAt: 1786051359181
embeddingSig: "binpath:else:hasapp|binpath:push:binpath|effective:preferred:terminal|else:hasapp:push|failing:closed:auto|hasapp:push:return|preferred:terminal:failing|push:binpath:else|push:return:resolve|resolve:effective:preferred|return:resolve:effective|terminal:failing:closed"
---
)));
    if (binPath) out.push({ def, binPath });
    else if (hasApp) out.push({ def });
  }
  return out;
}
/**
 * Resolve the effective preferred terminal, FAILING CLOSED to `auto`. Returns the
 * DetectedTerminal for `preferredId` when still available, else the `auto` entry
 * (always present).