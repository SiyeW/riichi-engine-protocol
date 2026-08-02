#!/usr/bin/env python3
"""Dependency-free repository consistency checks for the protocol draft."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    json_files = sorted(ROOT.rglob("*.json"))
    documents = {path: load_json(path) for path in json_files}

    project = documents[ROOT / "protocol.json"]
    require(isinstance(project, dict), "protocol.json must contain an object")
    require(project.get("name") == "riichi-engine-protocol", "unexpected protocol name")

    schema_ids: set[str] = set()
    for path in sorted((ROOT / "schemas").glob("*.json")):
        document = documents[path]
        require(isinstance(document, dict), f"{path.name} must contain an object")
        schema_id = document.get("$id")
        require(isinstance(schema_id, str), f"{path.name} has no $id")
        require(schema_id.startswith("urn:riichi-engine-protocol:schema:"), f"unexpected $id in {path.name}")
        require(schema_id not in schema_ids, f"duplicate schema $id: {schema_id}")
        schema_ids.add(schema_id)

    example = ROOT / "examples" / "mock-decision-engine"
    engine = documents[example / "engine.json"]
    model = documents[example / "model.json"]
    require(isinstance(engine, dict) and isinstance(model, dict), "example metadata must be objects")
    require(model.get("engineId") == engine.get("id"), "example model engineId mismatch")
    require(engine.get("protocol", {}).get("name") == project.get("name"), "example protocol name mismatch")

    model_path = example / str(model.get("file"))
    require(model_path.is_file(), "example model file is missing")
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    require(digest == model.get("sha256"), "example model SHA-256 mismatch")
    require(model_path.stat().st_size == model.get("sizeBytes"), "example model size mismatch")

    print(f"OK: parsed {len(json_files)} JSON files and checked the mock package")


if __name__ == "__main__":
    main()
