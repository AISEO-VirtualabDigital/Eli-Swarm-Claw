# Integration Notes: OpenClaw + Kimi K2.7 Code + Eli-OS

## 1. OpenClaw SKILL.md Standard Adoption

### What We Adopted

The Eli-Swarm-Claw project adopts the OpenClaw SKILL.md paradigm as the foundational mechanism for declarative agent boundaries. This means:

- **Each of the 12 SEO agents** is defined by a SKILL.md file in `/etc/eli-os/skills/`
- **The Rust control plane** parses these files at startup to build a dynamic capability manifest
- **Agents declare their own boundaries** rather than having them imposed by hardcoded Rust policy
- **Hot-reload** is supported: update a SKILL.md file and signal the kernel to reload without recompilation

### Divergences from OpenClaw

| Aspect | OpenClaw | Eli-OS |
|--------|----------|--------|
| Skill location | Any directory | `/etc/eli-os/skills/` (configurable) |
| Enforcement | No native enforcement | Rust kernel enforces via IPC interception |
| Tool invocation | Agent self-validates | Kernel validates before execution |
| Cross-agent comm | Direct messaging | Event bus (kernel-mediated, pub/sub) |
| Policy granularity | Single allow/deny | Three-tier (Green/Amber/Red) |
| Error responses | Generic | Structured PolicyViolation with SKILL.md section reference |

### SKILL.md Schema Extensions

The Eli-OS SKILL.md schema extends the OpenClaw standard with four additional sections:

1. **IPC Policy** — Explicit table and endpoint access lists with read/write granularity
2. **Resource Limits** — Memory, CPU, and duration constraints per agent
3. **Escalation Triggers** — Domain-specific conditions for Orchestrator/human escalation
4. **Knowledge Base Scope** — Bounded corpus definition with exclusion lists

These extensions are necessary because the Eli-OS Rust kernel enforces boundaries at the IPC level, whereas OpenClaw relies on agent self-discipline.

## 2. Kimi K2.7 Code as the Orchestrator

### Why This Model

Kimi K2.7 Code (by Moonshot AI) is selected as the Orchestrator AI for four reasons:

1. **Open-weight** — Hostable within VirtuaLab Digital's sovereign infrastructure; no data leaves the system
2. **Terminal-first agentic design** — Optimized for multi-step tool calling, task decomposition, and decision trees
3. **1M token context window** — Via Kimi-Linear architecture; can hold complete outputs from multiple agents simultaneously
4. **Production validation** — First open-weight model in GitHub Copilot's model picker

### Deployment Architecture

```
Kimi K2.7 Code (1T parameters, INT4 quantized)
    |
    v
vLLM or SGLang inference server (single GPU, ~40GB VRAM at INT4)
    |
    | OpenAI-compatible API at http://localhost:8001/v1
    |
    v
EliOrchestrator (Python class in Eli Claw application plane)
    |
    |-- decompose() -- breaks tasks into sub-task DAG
    |-- route() -- selects agent based on SKILL.md Purpose
    |-- synthesize() -- merges multi-agent outputs
    |-- handle_escalation() -- decides retry/reroute/compose/escalate_to_human
```

### Model Endpoints Used

| Orchestrator Method | Kimi API Call | Input | Output |
|---------------------|---------------|-------|--------|
| `decompose` | `POST /v1/chat/completions` | Task string + agent registry | JSON sub-task DAG |
| `route` | `POST /v1/chat/completions` | Sub-task description + agent registry | Agent name |
| `synthesize` | `POST /v1/chat/completions` | Original task + all sub-task results | Unified response |
| `handle_escalation` | `POST /v1/chat/completions` | Escalation event context | Decision enum |

### Resource Requirements

- **GPU**: 1x NVIDIA A100 80GB or 2x NVIDIA L40S (INT4 quantized)
- **VRAM**: ~40GB at INT4, ~80GB at FP16
- **Inference engine**: vLLM 0.6+ or SGLang for high-throughput batching
- **Latency budget**: <5 seconds per Orchestrator decision (decompose takes longest)

## 3. awesome-ai-coding-tools Mapping

The awesome-ai-coding-tools repository (referenced by the user) contains a curated list of AI coding tools. The following tools from that list are directly relevant to the Eli-OS stack:

| Tool | Role in Eli-OS | Integration Point |
|------|---------------|-------------------|
| **vLLM** | Kimi K2.7 Code inference server | Orchestrator model serving |
| **SGLang** | Alternative inference server | Orchestrator model serving |
| **CrewAI** | Existing Python multi-agent framework (in Eli Claw) | Application-plane agent coordination (to be gradually replaced by Eli-OS kernel governance) |
| **FastAPI** | API framework (existing in Eli Claw) | REST API layer above the Orchestrator |
| **PostgreSQL** | Primary database (existing) | Agent data stores, audit logs |
| **Redis** | Planned queue and cache layer | Task queue, Orchestrator state, IPC response caching |
| **gRPC** | IPC transport (new) | Rust kernel <-> Python agent communication |
| **Protocol Buffers** | Serialization format (new) | IPC message definitions |
| **Docker** | Containerization (existing) | Deployment of kernel + agents + model server |

## 4. Existing Repository Mapping

The deliverables in this package map to the existing Eli-Swarm-Claw repository structure:

| Deliverable | Maps To | Action Required |
|-------------|---------|----------------|
| `skill-templates/*.md` | `eli-os/skills/` (new directory) | Copy all 12 files, customize for your environment |
| `rust-control-plane/eli-skill-parser/` | `eli-os/crates/eli-skill-parser/` | Add as new crate to workspace Cargo.toml |
| `rust-control-plane/eli-policy-engine/` | `eli-os/crates/eli-policy-engine/` | Add as new crate, depends on eli-skill-parser |
| `rust-control-plane/eli-ipc-handler/` | `eli-os/crates/eli-ipc-handler/` | Add as new crate, depends on eli-policy-engine |
| `python-integration/agents/base.py` | `apps/api/app/agents/base.py` | Replace or extend existing agent base class |
| `python-integration/agents/ipc_client.py` | `apps/api/app/core/ipc_client.py` | New file, add to core module |
| `python-integration/orchestrator/` | `apps/api/app/agents/orchestrator/` | New directory, integrates with existing agents/ module |
| Architecture PDF | `docs/ARCHITECTURE_V2.md` | Reference document, not code |

## 5. Implementation Priority Order

Based on the diagnosis that Eli-OS is blocking orders, the recommended implementation sequence is:

1. **Week 1**: Copy SKILL.md files to `eli-os/skills/`, implement `eli-skill-parser` crate, verify parsing
2. **Week 2**: Implement `eli-policy-engine` crate with Green-tier enforcement only, integrate with existing Python agent via StubIpcClient
3. **Week 3**: Replace StubIpcClient with real gRPC IPC, implement `eli-ipc-handler` crate
4. **Week 4**: Add Amber/Red tiers, implement human approval queue
5. **Week 5**: Set up Kimi K2.7 Code inference server, implement EliOrchestrator
6. **Week 6**: End-to-end testing, performance benchmarking, deployment

## 6. Key Risks and Mitigations

- **SKILL.md drift**: CI/CD pipeline must compare agent test queries against IPC Policy declarations
- **Orchestrator hallucination**: QA Agent samples routing decisions; agent domain refusal invariant as safety net
- **Model latency**: vLLM batching + INT4 quantization keeps decisions under 5 seconds
- **gRPC connection overhead**: Connection multiplexing via HTTP/2 mitigates concurrency scaling concerns
