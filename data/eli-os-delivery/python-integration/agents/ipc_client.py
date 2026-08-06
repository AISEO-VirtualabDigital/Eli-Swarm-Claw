"""Eli-OS gRPC IPC Client.

This module provides the async gRPC client that Python agents use to
communicate with the Eli-OS Rust control plane over a Unix Domain Socket.

Architecture
-----------

```text
  Python Agent Process              Rust Control Plane
  ─────────────────────              ─────────────────

  EliIpcClient                     IpcServer
       │                               │
       │  gRPC/UDS (Unix Domain Socket) │
       │                               │
       ├─ evaluate()   ──▶  evaluate_request RPC
       ├─ report()     ──▶  report_result RPC
       ├─ escalate()   ──▶  escalate RPC
       └─ heartbeat()  ──▶  heartbeat RPC
```

Two implementations are provided:

1. **``EliIpcClient``** — The production class skeleton.  It defines the
   interface and documents how generated protobuf stubs would be used.
   In production, replace the ``_call_stub`` method body with actual
   ``grpc.aio`` stub invocations against the compiled ``.proto`` service.

2. **``StubIpcClient``** — A fully functional prototype that simulates
   gRPC calls locally.  This allows agents to be developed and tested
   without a running Rust kernel.  All responses are deterministic
   (``approved`` at ``GREEN`` tier).

Production Setup
---------------

When protobuf stubs are available, the client will be instantiated as::

    client = EliIpcClient(socket_path='/tmp/eli-os.ipc')
    async with client:
        response = await client.evaluate({"agent_id": "technical_seo", ...})

The ``.proto`` service definition (from the Rust crate) is::

    service EliIpcService {
      rpc EvaluateRequest(IpcRequest) returns (IpcResponse);
      rpc ReportResult(ResultReport) returns (Acknowledgement);
      rpc Escalate(EscalationEvent) returns (Acknowledgement);
      rpc Heartbeat(Heartbeat) returns (HeartbeatAck);
    }

Dependencies
------------
- ``grpcio`` or ``grpcio-health-checking`` (production)
- No external dependencies for ``StubIpcClient``
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import structlog

__all__ = [
    "EliIpcClient",
    "StubIpcClient",
]

logger = structlog.get_logger(__name__)

# Maximum number of retries for transient failures.
_MAX_RETRIES: int = 3

# Base delay in seconds for exponential backoff (100ms).
_BASE_DELAY: float = 0.1

# Default per-call timeout in seconds.
_DEFAULT_TIMEOUT: float = 30.0


# ============================================================================
# Abstract base
# ============================================================================

class _BaseIpcClient(ABC):
    """Abstract interface for the Eli-OS IPC client.

    Both the production ``EliIpcClient`` and the prototype
    ``StubIpcClient`` implement this interface.
    """

    @abstractmethod
    async def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a policy evaluation request to the Rust kernel."""
        ...  # pragma: no cover

    @abstractmethod
    async def report_result(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Report an execution result to the Rust kernel."""
        ...  # pragma: no cover

    @abstractmethod
    async def escalate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send an escalation event to the Rust kernel."""
        ...  # pragma: no cover

    @abstractmethod
    async def heartbeat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a heartbeat to the Rust kernel."""
        ...  # pragma: no cover

    @abstractmethod
    async def close(self) -> None:
        """Close the IPC channel and release resources."""
        ...  # pragma: no cover


# ============================================================================
# Production client (skeleton)
# ============================================================================

class EliIpcClient(_BaseIpcClient):
    """Production gRPC IPC client for the Eli-OS control plane.

    Connects to the Rust kernel over a Unix Domain Socket using
    ``grpc.aio``.  In the current prototype phase, this class provides
    the full interface and retry/timeout logic but falls back to the
    ``StubIpcClient`` for actual call execution.

    To switch to real gRPC:

    1. Generate Python protobuf stubs from ``eli_ipc.proto``::

         python -m grpc_tools.protoc \
             --python_out=. \
             --grpc_python_out=. \
             eli_ipc.proto

    2. Import the generated stub and replace ``_call_stub`` body.

    Parameters
    ----------
    socket_path:
        Path to the Unix Domain Socket the Rust kernel listens on.
    timeout:
        Default per-call timeout in seconds.
    """

    def __init__(
        self,
        socket_path: str = "/tmp/eli-os.ipc",
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._socket_path = socket_path
        self._timeout = timeout
        self._channel = None
        self._stub = None

        # Fall back to stub for prototype phase
        self._fallback = StubIpcClient()

        self._log = structlog.get_logger("eli_ipc_client")
        self._log.debug(
            "ipc_client_initialized",
            socket_path=socket_path,
            timeout=timeout,
        )

        self._connect()

    def _connect(self) -> None:
        """Establish the gRPC channel over the Unix Domain Socket.

        In production, this creates a ``grpc.aio.insecure_channel``
        targeting the UDS path.  The generated protobuf stub is then
        instantiated from this channel.

        For now, we log the connection attempt and note that the
        fallback stub is in use.
        """
        try:
            import grpc.aio

            # In production, uncomment the following:
            # self._channel = grpc.aio.insecure_channel(
            #     f"unix://{self._socket_path}",
            #     options=[
            #         ("grpc.keepalive_time_ms", 10000),
            #         ("grpc.keepalive_timeout_ms", 5000),
            #         ("grpc.http2.max_pings_without_data", 0),
            #     ],
            # )
            # from eli_ipc_pb2_grpc import EliIpcServiceStub
            # self._stub = EliIpcServiceStub(self._channel)

            self._log.info(
                "grpc_module_available",
                note="Using StubIpcClient fallback; generate .proto stubs for production.",
            )
        except ImportError:
            self._log.warning(
                "grpc_not_installed",
                note="grpc module not found; using StubIpcClient fallback.",
            )

    def _serialize_request(self, method: str, data: Dict[str, Any]) -> bytes:
        """Serialize a request dict to bytes for gRPC transmission.

        In production this uses protobuf serialization.  For the
        prototype, we use JSON encoding.

        Parameters
        ----------
        method:
            The RPC method name (for future protobuf message routing).
        data:
            The request dictionary to serialize.

        Returns
        -------
        bytes
            JSON-encoded bytes.
        """
        return json.dumps(data, default=str).encode("utf-8")

    def _deserialize_response(self, data: bytes) -> Dict[str, Any]:
        """Deserialize a response from bytes.

        In production this uses protobuf deserialization.  For the
        prototype, we use JSON decoding.

        Parameters
        ----------
        bytes
            JSON-encoded bytes.

        Returns
        -------
        dict
            The deserialized response dictionary.
        """
        return json.loads(data.decode("utf-8"))

    async def _call_stub(
        self,
        method: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke a gRPC stub method with retry and timeout logic.

        Implements exponential backoff with jitter:

        - Attempt 1: immediate
        - Attempt 2: wait ~100ms + jitter
        - Attempt 3: wait ~200ms + jitter

        Parameters
        ----------
        method:
            The RPC method name (``"evaluate"``, ``"report_result"``, etc.).
        request:
            The request dictionary.

        Returns
        -------
        dict
            The response dictionary from the kernel.

        Raises
        ------
        RuntimeError
            If all retries are exhausted.
        asyncio.TimeoutError
            If the call times out on every attempt.
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                self._log.debug(
                    "ipc_call_attempt",
                    method=method,
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                )

                # In production, replace with:
                #   serialized = self._serialize_request(method, request)
                #   proto_request = eval(f"eli_ipc_pb2.{_proto_msg_name(method)}()")
                #   proto_request.ParseFromString(serialized)
                #   response_proto = await asyncio.wait_for(
                #       getattr(self._stub, f"{_grpc_method_name(method)}")(proto_request),
                #       timeout=self._timeout,
                #   )
                #   return self._deserialize_response(response_proto.SerializeToString())

                # Prototype: delegate to the stub
                response = await asyncio.wait_for(
                    self._fallback._dispatch(method, request),
                    timeout=self._timeout,
                )
                return response

            except asyncio.TimeoutError as exc:
                last_error = exc
                self._log.warning(
                    "ipc_call_timeout",
                    method=method,
                    attempt=attempt,
                )

            except ConnectionError as exc:
                last_error = exc
                self._log.warning(
                    "ipc_connection_error",
                    method=method,
                    attempt=attempt,
                    error=str(exc),
                )

            except Exception as exc:
                last_error = exc
                self._log.error(
                    "ipc_call_unexpected_error",
                    method=method,
                    attempt=attempt,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )

            # Exponential backoff with jitter before retrying
            if attempt < _MAX_RETRIES:
                delay = _BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 0.05)
                self._log.debug("ipc_retry_backoff", delay=delay)
                await asyncio.sleep(delay)

        # All retries exhausted
        raise RuntimeError(
            f"IPC call '{method}' failed after {_MAX_RETRIES} retries: {last_error}"
        )

    async def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a policy evaluation request to the Rust kernel.

        Maps to the ``EvaluateRequest`` gRPC RPC.

        Parameters
        ----------
        request:
            An ``IpcRequest`` dict with keys: ``agent_id``,
            ``operation_type``, ``target_resource``, ``payload``,
            ``request_ulid``, ``timestamp``.

        Returns
        -------
        dict
            An ``IpcResponse`` dict with keys: ``approved``, ``tier``,
            ``violation_detail``, ``escalation_reason``.
        """
        return await self._call_stub("evaluate", request)

    async def report_result(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Report an execution result to the Rust kernel.

        Maps to the ``ReportResult`` gRPC RPC.

        Parameters
        ----------
        request:
            A ``ResultReport`` dict with keys: ``agent_id``, ``task_id``,
            ``result_type``, ``payload``, ``timestamp``.

        Returns
        -------
        dict
            An ``Acknowledgement`` dict with keys: ``success``,
            ``message``, ``audit_ulid``.
        """
        return await self._call_stub("report_result", request)

    async def escalate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send an escalation event to the Rust kernel.

        Maps to the ``Escalate`` gRPC RPC.

        Parameters
        ----------
        request:
            An ``EscalationEvent`` dict with keys: ``agent_id``,
            ``trigger_reason``, ``context``, ``severity``, ``timestamp``.

        Returns
        -------
        dict
            An ``Acknowledgement`` dict.
        """
        return await self._call_stub("escalate", request)

    async def heartbeat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a heartbeat to the Rust kernel.

        Maps to the ``Heartbeat`` gRPC RPC.

        Parameters
        ----------
        request:
            A ``Heartbeat`` dict with keys: ``agent_id``, ``status``,
            ``tasks_completed``, ``memory_usage_mb``.

        Returns
        -------
        dict
            A ``HeartbeatAck`` dict with keys: ``acknowledged``,
            ``resource_warning``.
        """
        return await self._call_stub("heartbeat", request)

    async def close(self) -> None:
        """Close the gRPC channel and release resources.

        In production, this calls ``self._channel.close()``.
        """
        if self._channel is not None:
            await self._channel.close()
            self._log.info("grpc_channel_closed")

    async def __aenter__(self) -> "EliIpcClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[Any] = None,
    ) -> None:
        """Async context manager exit — ensures channel cleanup."""
        await self.close()


# ============================================================================
# Prototype stub client
# ============================================================================

class StubIpcClient(_BaseIpcClient):
    """Prototype IPC client that simulates gRPC calls locally.

    **This is a development/testing stub.**  It does **not** connect to
    the Rust kernel.  Instead, it simulates the four RPCs with
    deterministic responses:

    - ``evaluate`` → always returns ``approved`` at ``GREEN`` tier.
    - ``report_result`` → always returns ``success: True``.
    - ``escalate`` → always returns ``success: True``.
    - ``heartbeat`` → always returns ``acknowledged: True``.

    The stub includes a local policy simulation that can be configured
    to trigger violations for testing error handling paths.

    Parameters
    ----------
    socket_path:
        Accepted for interface compatibility; not used.
    simulate_violations:
        If ``True``, the ``evaluate`` method will simulate policy
        violations for certain operation types to test error handling.
    """

    def __init__(
        self,
        socket_path: str = "/tmp/eli-os.ipc",  # noqa: ARG002
        simulate_violations: bool = False,
    ) -> None:
        self._simulate_violations = simulate_violations
        self._log = structlog.get_logger("stub_ipc_client")
        self._log.info(
            "stub_ipc_client_initialized",
            note="Prototype mode — no Rust kernel connection.",
        )

    async def _dispatch(
        self,
        method: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Route a method call to the appropriate handler.

        This is the internal dispatch used by ``EliIpcClient._call_stub``
        when operating in prototype/fallback mode.
        """
        handlers = {
            "evaluate": self._handle_evaluate,
            "report_result": self._handle_report_result,
            "escalate": self._handle_escalate,
            "heartbeat": self._handle_heartbeat,
        }
        handler = handlers.get(method)
        if handler is None:
            raise ValueError(f"Unknown IPC method: {method}")
        return await handler(request)

    async def _handle_evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the ``EvaluateRequest`` RPC.

        Returns an ``IpcResponse`` dict.  If ``simulate_violations`` is
        ``True`` and the agent attempts a ``DELETE`` operation, a
        ``PolicyViolation`` is returned instead.
        """
        agent_id = request.get("agent_id", "unknown")
        operation_type = request.get("operation_type", "READ")
        target_resource = request.get("target_resource", "unknown")

        self._log.debug(
            "stub_evaluate",
            agent_id=agent_id,
            operation_type=operation_type,
            target_resource=target_resource,
        )

        # Simulate a RED-tier violation for DELETE operations when testing
        if self._simulate_violations and operation_type == "DELETE":
            return {
                "approved": False,
                "tier": "RED",
                "violation_detail": {
                    "agent_id": agent_id,
                    "operation_type": operation_type,
                    "target_resource": target_resource,
                    "violated_section": "Forbidden Actions",
                    "rule_text": (
                        f"Agent '{agent_id}' is not authorized to perform "
                        f"DELETE operations on '{target_resource}'."
                    ),
                    "tier": "RED",
                    "explanation": (
                        f"The DELETE operation type is not listed in the agent's "
                        f"IPC Policy allowed operations for '{target_resource}'."
                    ),
                    "suggested_resolution": (
                        f"Remove the DELETE operation or request an IPC policy "
                        f"update for agent '{agent_id}' to include DELETE access "
                        f"to '{target_resource}'."
                    ),
                },
                "escalation_reason": None,
            }

        # Simulate escalation for cross-domain access
        if self._simulate_violations and "cross_domain" in str(request.get("payload", {})):
            return {
                "approved": False,
                "tier": "RED",
                "violation_detail": None,
                "escalation_reason": (
                    f"Agent '{agent_id}' attempted cross-domain resource access "
                    f"on '{target_resource}'. Requires human operator review."
                ),
            }

        # Default: approved at GREEN tier for reads, AMBER for writes
        tier = "GREEN" if operation_type == "READ" else "AMBER"

        return {
            "approved": True,
            "tier": tier,
            "violation_detail": None,
            "escalation_reason": None,
        }

    async def _handle_report_result(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the ``ReportResult`` RPC.

        Returns an ``Acknowledgement`` dict.
        """
        import ulid

        agent_id = request.get("agent_id", "unknown")
        result_type = request.get("result_type", "unknown")

        self._log.debug(
            "stub_report_result",
            agent_id=agent_id,
            result_type=result_type,
        )

        return {
            "success": True,
            "message": f"Result of type '{result_type}' from agent '{agent_id}' accepted.",
            "audit_ulid": str(ulid.new()),
        }

    async def _handle_escalate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the ``Escalate`` RPC.

        Returns an ``Acknowledgement`` dict.
        """
        import ulid

        agent_id = request.get("agent_id", "unknown")
        trigger = request.get("trigger_reason", "unknown")
        severity = request.get("severity", "high")

        self._log.warning(
            "stub_escalate",
            agent_id=agent_id,
            trigger_reason=trigger,
            severity=severity,
        )

        return {
            "success": True,
            "message": (
                f"Escalation from agent '{agent_id}' (severity={severity}) "
                f"accepted and queued for operator review."
            ),
            "audit_ulid": str(ulid.new()),
        }

    async def _handle_heartbeat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the ``Heartbeat`` RPC.

        Returns a ``HeartbeatAck`` dict.  Simulates a resource warning
        if ``memory_usage_mb`` exceeds 400 MB.
        """
        agent_id = request.get("agent_id", "unknown")
        memory_mb = request.get("memory_usage_mb", 0.0)

        self._log.debug(
            "stub_heartbeat",
            agent_id=agent_id,
            memory_usage_mb=memory_mb,
        )

        # Simulate a resource warning at high memory usage
        resource_warning: Optional[str] = None
        if memory_mb > 400:
            resource_warning = (
                f"Agent '{agent_id}' is approaching its memory limit: "
                f"{memory_mb:.1f} MB used / 512 MB allowed (78% utilization)."
            )

        return {
            "acknowledged": True,
            "resource_warning": resource_warning,
        }

    # -- Public interface (matches _BaseIpcClient) --------------------------

    async def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a policy evaluation request (stub implementation)."""
        return await self._dispatch("evaluate", request)

    async def report_result(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Report an execution result (stub implementation)."""
        return await self._dispatch("report_result", request)

    async def escalate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send an escalation event (stub implementation)."""
        return await self._dispatch("escalate", request)

    async def heartbeat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a heartbeat (stub implementation)."""
        return await self._dispatch("heartbeat", request)

    async def close(self) -> None:
        """No-op for the stub client (no resources to release)."""
        self._log.debug("stub_ipc_client_closed")

    async def __aenter__(self) -> "StubIpcClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[Any] = None,
    ) -> None:
        """Async context manager exit."""
        await self.close()
