---
id: fec8ad0d4f622de7
source: "agent-eli-v1-backend-code.md"
"title: Agent Eli v1 — Backend Code Reference"
category: ai-agent
skillTags: ["warning"]
containmentHash: 55db916430f2346418e2
createdAt: 1786051352661
embeddingSig: "budget:deploy:bulk|bulk:submit:modify|change:budget:deploy|deploy:bulk:submit|email:send:message|message:change:budget|modify:production:purchase|production:purchase:create|purchase:create:user|send:email:send|send:message:change|submit:modify:production"
---
", "send_email", "send_message", "change_budget",
    "deploy", "bulk_submit", "modify_production", "purchase", "create_user"
}
def evaluate_action(request: dict) -> dict:
    action = request.get("action", "").lower()
    production = bool(request.get("production"))
    destructive = bool(request.get("destructive"))
    requires_approval = production or destructive or action in HIGH_RISK_ACTIONS
    return {