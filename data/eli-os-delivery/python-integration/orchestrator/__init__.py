"""Eli-OS Orchestrator package.

Exposes the Kimi K2.7 Code Orchestrator that decomposes tasks,
routes sub-tasks to agents, and synthesizes results.
"""

from .eli_orchestrator import (
    EscalationDecision,
    EliOrchestrator,
    SubTask,
    TaskDAG,
)

__all__ = [
    "EliOrchestrator",
    "TaskDAG",
    "SubTask",
    "EscalationDecision",
]
