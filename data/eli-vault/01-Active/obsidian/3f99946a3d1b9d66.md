---
id: 3f99946a3d1b9d66
source: "skill-harness-manager-reference.md"
"title: Skill and Harness Manager — Obsidian Plugin Reference"
category: obsidian
skillTags: []
containmentHash: bccd64df1cdd13db466b
createdAt: 1786051359181
embeddingSig: "await:this:walkfs|catch:isdir:false|false:isdir:await|full:isdirectory:catch|full:rootreal:depth|isdir:await:this|isdir:false:isdir|isdirectory:catch:isdir|rootreal:depth:seen|stat:full:isdirectory|this:walkfs:full|walkfs:full:rootreal"
---
es.stat(full)).isDirectory();
          } catch {
            isDir = false;
          }
        }
        if (isDir) await this.walkFs(full, rootReal, depth + 1, out, seen);
      } else if (entry.isFile()) {
        out.push(full);
      }
    }
  }
private makeSkill(
    fields: SkillFields,
    absPath: string,
    vaultPath: string | null,
    sourceRoot: string,
    detection: DetectionMethod,