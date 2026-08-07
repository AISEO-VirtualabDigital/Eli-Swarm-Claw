---
id: adb7f9df56c6b21d
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: ["tool"]
containmentHash: bed0e321940aad9dc40d
createdAt: 1786051359181
embeddingSig: "boolean:enabledplugins:yaml|enabledplugins:yaml:viewer|null:undefined:return|plugin:plugins:yaml|plugins:yaml:viewer|record:string:unknown|return:boolean:enabledplugins|string:unknown:null|undefined:return:boolean|unknown:null:undefined|viewer:plugin:plugins|yaml:viewer:plugin"
---
ins?: Record<string, unknown>;
      }
    | null
    | undefined;
  return Boolean(
    p?.enabledPlugins?.has?.(YAML_VIEWER_PLUGIN_ID) &&
      p?.plugins?.[YAML_VIEWER_PLUGIN_ID],
  );
}
/** Filesystem path helpers main.ts injects (node `path`) so this stays pure. */
export interface PathDeps {
  relative: (from: string, to: string) => string;
  isAbsolute: (p: string) => boolean;
  sep: string;