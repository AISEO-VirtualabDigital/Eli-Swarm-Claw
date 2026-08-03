"""Eli-OS Python agent layer.

This package provides the base agent class, IPC client, and
exception types that all 12 Eli-OS SEO agents inherit from.
"""

from .base import (
    EliAgent,
    EscalationRequiredError,
    PolicyViolationError,
    TechnicalSeoAgent,
)
from .ipc_client import EliIpcClient, StubIpcClient

__all__ = [
    "EliAgent",
    "EliIpcClient",
    "EscalationRequiredError",
    "PolicyViolationError",
    "StubIpcClient",
    "TechnicalSeoAgent",
]
