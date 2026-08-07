---
absorbedFrom: https://github.com/Panniantong/Agent-Reach
absorbedAt: 2026-08-08
chunkType: capability-routing-pattern
tags: [agent-reach, multi-backend-routing, channel-registry, probe-dont-guess, symlink-safety, ssrf-protection, skill-md, url-hardening, atomic-config, tier-model]
---

# Agent-Reach — Capability Layer for Internet Access

## Core Concept
Agent Reach gives any AI agent the ability to read/search 15+ internet platforms from CLI. It's a **capability layer** (not a tool wrapper) — it selects, installs, health-checks, and routes to upstream platform tools. Agents then call those tools directly with zero wrapper layer.

"Give your AI Agent eyes to see the entire internet. One CLI, zero API fees."

## Pattern 1: Ordered Multi-Backend Routing
Each platform has an ordered candidate list. `check()` probes each in sequence; first fully-usable one wins. Switching backends = reordering the list.

```python
class Channel(ABC):
    backends: List[str] = []  # ordered: backends[0] = preferred
    active_backend: Optional[str] = None
    
    def ordered_backends(self, config=None) -> List[str]:
        # Honors user override via config key
```

**Absorb into Eli**: This is the same pattern as Open Claw's provider failover (guerrilla → mailtm → openinbox). Validate and strengthen — add config override so users can set preferred provider.

## Pattern 2: Three-Tier Channel Model
| Tier | Meaning | Examples |
|------|---------|----------|
| 0 | Zero config | Web (Jina), YouTube (yt-dlp), GitHub (gh), RSS, V2EX |
| 1 | Needs free key/login | Twitter (cookies), Reddit, Bilibili, Exa |
| 2 | Complex setup | LinkedIn (MCP), Facebook/IG (OpenCLI+browser), XHS |

**Absorb into Eli**: Tag each Open Claw provider with a tier. Guerrilla = Tier 0, mail.tm = Tier 0, OpenInbox read = Tier 1 (needs paid key).

## Pattern 3: Probe-Don't-Guess Health Checking
Actually EXECUTES upstream CLIs with side-effect-free commands (`--version`) rather than just checking `shutil.which()`. Catches stale venv shims.

```python
@dataclass
class ProbeResult:
    status: str  # "ok" | "missing" | "broken" | "timeout" | "error"
```

**Absorb into Eli**: Add health probes to Open Claw providers. Don't just try to create an inbox — first probe the API with a lightweight request to check if it's alive.

## Pattern 4: Symlink-Hardened Credential Storage
- Refuses symlinks at every path component via `ensure_no_symlink_path()`
- Atomic writes via `tempfile.mkstemp()` → write → `os.replace()` → `fsync` directory
- Owner-only permissions: `fchmod(fd, 0o600)`
- `O_NOFOLLOW` on directory opens to prevent TOCTOU races

```python
def ensure_no_symlink_path(path, label="路径"):
    for part in absolute.parts[1:]:
        current /= part
        if stat.S_ISLNK(os.lstat(current).st_mode):
            raise PrivatePathError(f"{label}不能经过符号链接：{current}")
```

**Absorb into Eli**: When Eli persists keys or config to disk, use the symlink check + atomic write pattern.

## Pattern 5: URL Security Hardening
- `normalize_public_http_url()` rejects SSRF targets (localhost, internal IPs, private ranges, cloud metadata)
- `host_matches()` uses `urlsplit().hostname` (not substring match) to prevent lookalikes
- Rejects URLs with `userinfo`

**Absorb into Eli**: Add URL validation to any endpoint that accepts URLs (e.g., vault-sync if it fetches remote content).

## Pattern 6: SKILL.md as Agent Interface
Markdown file as the interface contract between tool and AI agent. Contains YAML frontmatter with trigger patterns, routing table mapping intents to reference docs.

**Absorb into Eli**: Eli's skill templates already use YAML frontmatter. Add a trigger patterns field so Eli's chat can auto-suggest relevant skills.

## Pattern 7: Two-Phase Backend Selection
Collect ALL findings from every candidate, then select by priority: first `ok` wins, then first `warn`. Prevents an installed-but-unconfigured primary from hiding a working fallback.

**Absorb into Eli**: Open Claw currently tries providers sequentially and breaks on first success. Change to: probe all providers, then select the best one.

## Pattern 8: Anti-Bot Detection in Content
Scans first 4KB of responses for captcha signatures before returning content.

## Pattern 9: Config with Env Fallback + Sensitive Redaction
`Config.get()` checks config file first, then `os.environ`. `to_dict()` masks any key containing `key|token|password|proxy|cookie|secret|session|csrf|auth|cred`.

**Absorb into Eli**: Add sensitive redaction to Omni Route's getState() — mask keys more aggressively.

## Pattern 10: Atomic Config Writes with Rollback
Temp file beside target (same filesystem for atomic replace) + fsync on both file and directory + symlink re-check after serialization. Rollback on failure.
