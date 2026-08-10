#!/usr/bin/env python3
"""Dependency-free repository consistency checks for the protocol."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def iter_public_json_files() -> list[Path]:
    """Return repository JSON files tracked or eligible for tracking."""
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "*.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        paths = (ROOT / Path(item) for item in result.stdout.decode("utf-8").split("\0") if item)
        return sorted(path for path in paths if path.is_file())

    excluded_directories = {".build", ".git", ".venv", "build", "dist", "runtime", "__pycache__"}
    return sorted(
        path
        for path in ROOT.rglob("*.json")
        if not any(part in excluded_directories or part.startswith(".conda") for part in path.relative_to(ROOT).parts)
    )


def main() -> None:
    json_files = iter_public_json_files()
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

    print(f"OK: parsed {len(json_files)} JSON files and checked {len(schema_ids)} schemas")


if __name__ == "__main__":
    main()
