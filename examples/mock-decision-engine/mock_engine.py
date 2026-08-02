"""Minimal decision-v1 JSON-RPC engine used by the public protocol example."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ENGINE_ID = "third-party.example-decision"
ENGINE_VERSION = "1.0.0"


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=True, separators=(",", ":")), flush=True)


def notify(method: str, params: dict[str, Any]) -> None:
    emit({"jsonrpc": "2.0", "method": method, "params": params})


def sha256_file(file_path: str) -> str:
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class MockDecisionEngine:
    def __init__(self) -> None:
        self.state = "starting"
        self.fingerprint = ""
        self.initialize_params: dict[str, Any] | None = None
        self.running = True

    def set_state(self, state: str) -> None:
        self.state = state
        notify("engine.status", {"state": state})

    def hello(self) -> dict[str, Any]:
        return {
            "protocol": {
                "name": "riichi-engine-protocol",
                "major": 1,
                "minor": 0,
            },
            "engine": {
                "id": ENGINE_ID,
                "name": "Reference Decision Engine",
                "version": ENGINE_VERSION,
                "kinds": ["decision"],
            },
            "capabilities": {
                "multipleSessions": True,
                "incrementalHistory": False,
                "concurrentRequests": False,
                "cancellation": False,
                "reload": True,
                "rawValues": True,
                "probabilities": True,
            },
        }

    def initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        self.set_state("loading")
        model = params.get("model") or {}
        actual_sha256 = sha256_file(str(model.get("path") or ""))
        expected_sha256 = str(model.get("expectedSha256") or "").lower()
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise ValueError("model SHA-256 does not match expectedSha256")
        fingerprint_payload = json.dumps(
            {
                "engineId": ENGINE_ID,
                "engineVersion": ENGINE_VERSION,
                "modelSha256": actual_sha256,
                "options": params.get("options") or {},
                "outputSchema": "decision-v1",
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.fingerprint = "sha256:" + hashlib.sha256(fingerprint_payload).hexdigest()
        self.initialize_params = dict(params)
        self.set_state("ready")
        return {
            "state": "ready",
            "engineId": ENGINE_ID,
            "engineVersion": ENGINE_VERSION,
            "model": {
                "id": model.get("id"),
                "format": model.get("format"),
                "sha256": actual_sha256,
            },
            "effectiveOptions": params.get("options") or {},
            "outputSchema": "decision-v1",
            "outputSchemaVersion": 1,
            "fingerprint": self.fingerprint,
            "capabilities": self.hello()["capabilities"],
            "device": {
                "type": "cpu",
                "displayName": "CPU",
            },
        }

    def analyze(self, params: dict[str, Any], request_id: Any) -> dict[str, Any]:
        candidates = params.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("candidates must be a non-empty array")
        task = {
            "requestId": request_id,
            "sessionId": params.get("sessionId"),
            "kind": "decision",
            "seat": params.get("seat"),
            "role": params.get("role"),
            "queueDepth": 0,
        }
        notify("task.status", {**task, "state": "running"})
        raw_values = [float(index) for index in range(len(candidates))]
        maximum = max(raw_values)
        exponentials = [math.exp(value - maximum) for value in raw_values]
        total = sum(exponentials)
        result = {
            "sessionId": params.get("sessionId"),
            "positionId": params.get("positionId"),
            "historyDigest": params.get("historyDigest"),
            "engineFingerprint": self.fingerprint,
            "bestCandidateId": candidates[-1]["candidateId"],
            "choices": [
                {
                    "candidateId": candidate["candidateId"],
                    "rawValue": raw_value,
                    "probability": exponential / total,
                }
                for candidate, raw_value, exponential in zip(
                    candidates,
                    raw_values,
                    exponentials,
                )
            ],
        }
        notify("task.status", {**task, "state": "completed"})
        return result

    def dispatch(
        self,
        method: str,
        params: dict[str, Any],
        request_id: Any,
    ) -> dict[str, Any]:
        if method == "engine.hello":
            return self.hello()
        if method == "engine.initialize":
            return self.initialize(params)
        if method == "engine.getStatus":
            return {
                "state": self.state,
                "activeTasks": 0,
                "queuedTasks": 0,
                "lastError": None,
            }
        if method == "engine.reload":
            if self.initialize_params is None:
                raise RuntimeError("engine is not initialized")
            return self.initialize(self.initialize_params)
        if method in ("session.reset", "session.close"):
            return {"ok": True}
        if method == "request.cancel":
            return {"canceled": False}
        if method == "engine.shutdown":
            self.set_state("stopping")
            self.running = False
            return {"ok": True}
        if self.initialize_params is None:
            raise RuntimeError("engine is not initialized")
        if method == "decision.analyze":
            return self.analyze(params, request_id)
        raise ValueError(f"unsupported method: {method}")


def main() -> None:
    engine = MockDecisionEngine()
    engine.set_state("starting")
    for raw_line in sys.stdin:
        request_id = None
        try:
            request = json.loads(raw_line)
            request_id = request.get("id")
            result = engine.dispatch(
                str(request.get("method") or ""),
                request.get("params") or {},
                request_id,
            )
            if request_id is not None:
                emit({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                })
        except Exception as error:  # pylint: disable=broad-except
            if request_id is not None:
                emit({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32019,
                        "message": " ".join(str(error).split()),
                    },
                })
        if not engine.running:
            break


if __name__ == "__main__":
    main()
