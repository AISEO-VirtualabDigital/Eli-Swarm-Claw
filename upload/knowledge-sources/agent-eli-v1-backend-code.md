# Agent Eli v1 — Backend Code Reference

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Agent Eli",
    version="1.0.0",
    description="Human-led, approval-gated AI SEO operating system.",
)
app.include_router(router, prefix="/api")

@app.get("/health")
def health() -> dict:
    return {
        "system": "Agent Eli",
        "status": "online",
        "safe_mode": True,
        "execution": "approval_gated",
        "legacy_core": "Orange Orbit",
    }


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.policy import evaluate_action
from app.services.registry import load_integrations, load_skills

router = APIRouter()

class ActionRequest(BaseModel):
    action: str
    resource: str
    production: bool = False
    destructive: bool = False

@router.get("/status")
def status():
    return {
        "safe_mode": True,
        "state_model": ["OBSERVE","ANALYZE","PLAN","PREVIEW","APPROVAL","EXECUTE","VERIFY","RECORD"],
        "production_writes": "blocked_without_owner_approval",
    }

@router.get("/integrations")
def integrations():
    return load_integrations()

@router.get("/skills")
def skills():
    return load_skills()

@router.post("/policy/evaluate")
def policy_evaluate(payload: ActionRequest):
    return evaluate_action(payload.model_dump())

@router.post("/execute")
def execute(payload: ActionRequest):
    decision = evaluate_action(payload.model_dump())
    if not decision["allowed"]:
        raise HTTPException(status_code=403, detail=decision)
    return {"ok": True, "state": "STAGED", "decision": decision}


HIGH_RISK_ACTIONS = {
    "publish", "delete", "send_email", "send_message", "change_budget",
    "deploy", "bulk_submit", "modify_production", "purchase", "create_user"
}

def evaluate_action(request: dict) -> dict:
    action = request.get("action", "").lower()
    production = bool(request.get("production"))
    destructive = bool(request.get("destructive"))
    requires_approval = production or destructive or action in HIGH_RISK_ACTIONS
    return {
        "allowed": not requires_approval,
        "requires_owner_approval": requires_approval,
        "safe_mode": True,
        "reason": "Owner approval required for production, destructive or external side-effect actions."
        if requires_approval else "Read-only or staging action permitted.",
    }


from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]

def _load(folder: str) -> list[dict]:
    items = []
    for path in sorted((ROOT / "registry" / folder).glob("*.json")):
        items.append(json.loads(path.read_text()))
    return items

def load_integrations() -> list[dict]:
    return _load("integrations")

def load_skills() -> list[dict]:
    return _load("skills")


## Requirements

fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1


## Dockerfile

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY ../registry /registry
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]


## Environment Variables

OWNER_TOKEN=replace_me
POSTGRES_PASSWORD=replace_me
DATABASE_URL=postgresql://eli:replace_me@postgres:5432/agent_eli
REDIS_URL=redis://redis:6379/0
OPENROUTER_API_KEY=
OPENAI_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
N8N_API_URL=
N8N_API_KEY=
BASEROW_API_URL=
BASEROW_API_TOKEN=
WORDPRESS_URL=
WORDPRESS_APPLICATION_PASSWORD=
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
