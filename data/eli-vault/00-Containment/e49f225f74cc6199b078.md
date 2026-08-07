---
id: 63ed8c6fff0d0ab6
source: "virtuallab-strategy-doc.md"
"title: VirtuaLab Strategy Document"
category: knowledge
skillTags: ["tool"]
containmentHash: e49f225f74cc6199b078
createdAt: 1786051359689
embeddingSig: "approvalpolicy:containmentpolicy:executionpolicy|attach:audit:context|audit:context:policy|containmentpolicy:executionpolicy:specific|context:policy:tools|executionpolicy:specific:checks|input:attach:audit|malformed:input:attach|policy:approvalpolicy:containmentpolicy|policy:tools:policy|specific:checks:approval|tools:policy:approvalpolicy"
---
ent malformed input ✔ Attach audit context --- B. Policy Tools (eli-policy) ApprovalPolicy ContainmentPolicy ExecutionPolicy Specific checks: ✔ approval_required() ✔ is_allowed() ✔ is_contained() ✔ classify_command() These are your decision engines. --- C. Runtime Tools (eli-runtime) RuntimeExecutionCommand RuntimeExecutionResult RuntimeExecutor