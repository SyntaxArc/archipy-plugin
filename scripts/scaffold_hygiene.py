#!/usr/bin/env python3
"""Plugin hook: ArchiPy scaffold hygiene reminders for consumer apps."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Top-level app adapters package (forbidden). Domain adapters under repositories/*/adapters/ are OK.
TOP_LEVEL_ADAPTERS_RE = re.compile(
    r"(^|/)adapters/[^/]+\.py$",
)
REPO_ADAPTERS_RE = re.compile(r"(^|/)repositories/[^/]+/adapters/")

HARD_RULES = (
    "ArchiPy app hard rules: call flow services → logics → repositories → adapters → ArchiPy. "
    "Import direction: configs ← models ← helpers ← repositories / logics / services. "
    "Domain adapters live under repositories/{domain}/adapters/ — never invent a top-level app adapters/ package. "
    "Prefer plugin scaffolds (/scaffold-*, /redis-search) and skills/archipy-docs/reference.md."
)


def _read_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload))


def _is_forbidden_adapters_path(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    if REPO_ADAPTERS_RE.search(normalized):
        return False
    return bool(TOP_LEVEL_ADAPTERS_RE.search(normalized))


def _paths_from_payload(payload: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    if file_path := payload.get("file_path"):
        paths.append(str(file_path))
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in ("path", "file_path", "target_notebook"):
            value = tool_input.get(key)
            if value:
                paths.append(str(value))
    elif isinstance(tool_input, str):
        try:
            parsed = json.loads(tool_input)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            for key in ("path", "file_path"):
                value = parsed.get(key)
                if value:
                    paths.append(str(value))
    return paths


def handle_session_start(_payload: dict[str, Any]) -> dict[str, Any]:
    return {"additional_context": HARD_RULES}


def handle_post_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    for path in _paths_from_payload(payload):
        if _is_forbidden_adapters_path(path):
            warnings.append(
                f"ArchiPy hygiene: `{Path(path).as_posix()}` looks like a top-level adapters/ file. "
                "Move domain adapters to repositories/{domain}/adapters/ instead."
            )
    if not warnings:
        return {}
    return {"additional_context": " ".join(warnings)}


def main() -> int:
    payload = _read_stdin()
    # Cursor may pass hook event name via argv or payload fields.
    event = ""
    if len(sys.argv) > 1:
        event = sys.argv[1]
    event = event or str(payload.get("hook_event_name") or payload.get("event") or "")

    if event in {"sessionStart", "session_start"}:
        _emit(handle_session_start(payload))
    elif event in {"postToolUse", "post_tool_use"}:
        _emit(handle_post_tool_use(payload))
    else:
        # Fail open for unknown events / empty stdin.
        _emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
