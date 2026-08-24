#!/usr/bin/env python3
"""Plugin hook: ArchiPy scaffold hygiene reminders for consumer apps."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

# Any adapters/*.py outside repositories/{domain}/adapters/ is forbidden for ArchiPy apps.
ADAPTERS_FILE_RE = re.compile(r"(^|/)adapters/[^/]+\.py$")
REPO_ADAPTERS_RE = re.compile(r"(^|/)repositories/[^/]+/adapters/")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)

HARD_RULES = (
    "ArchiPy apps: follow architecture-for-apps rule + skills/archipy-docs/reference.md. "
    "Domain adapters under repositories/{domain}/adapters/ only. Prefer /scaffold-* commands."
)

# Cursor event names (camelCase). Claude Code uses PascalCase and a different hooks.json schema.
CURSOR_SESSION = "sessionStart"
CURSOR_POST = "postToolUse"
CLAUDE_SESSION = "SessionStart"
CLAUDE_POST = "PostToolUse"


def _plugin_root() -> Path:
    for key in ("CLAUDE_PLUGIN_ROOT", "CURSOR_PLUGIN_ROOT"):
        raw = os.environ.get(key)
        if raw:
            return Path(raw)
    return Path(__file__).resolve().parents[1]


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
    return bool(ADAPTERS_FILE_RE.search(normalized))


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


def _parse_rule(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    meta: dict[str, str] = {}
    body = text
    if match:
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        body = text[match.end() :].lstrip("\n")
    return meta, body


def _path_matches(file_path: str, glob_field: str) -> bool:
    normalized = file_path.replace("\\", "/").lstrip("./")
    candidate = PurePosixPath(normalized)
    prefixed = PurePosixPath(f"_/{normalized}")
    for pattern in (part.strip() for part in glob_field.split(",") if part.strip()):
        variants = [pattern]
        if pattern.startswith("**/"):
            variants.append(pattern[3:])
        for variant in variants:
            try:
                if candidate.match(variant) or prefixed.match(variant):
                    return True
            except ValueError:
                continue
    return False


def _always_apply_rules() -> list[str]:
    chunks: list[str] = []
    rules_dir = _plugin_root() / "rules"
    if not rules_dir.is_dir():
        return chunks
    for rule in sorted(rules_dir.glob("*.mdc")):
        meta, body = _parse_rule(rule)
        if meta.get("alwaysApply", "").lower() == "true" and body.strip():
            chunks.append(body.strip())
    return chunks


def _matching_rules(file_paths: list[str]) -> list[str]:
    rules_dir = _plugin_root() / "rules"
    if not rules_dir.is_dir():
        return []
    chunks: list[str] = []
    seen: set[str] = set()
    for rule in sorted(rules_dir.glob("*.mdc")):
        meta, body = _parse_rule(rule)
        globs = meta.get("globs", "")
        if not globs or not body.strip():
            continue
        if any(_path_matches(path, globs) for path in file_paths):
            if rule.name not in seen:
                seen.add(rule.name)
                chunks.append(body.strip())
    return chunks


def handle_cursor_session_start(_payload: dict[str, Any]) -> dict[str, Any]:
    return {"additional_context": HARD_RULES}


def handle_claude_session_start(_payload: dict[str, Any]) -> dict[str, Any]:
    # Claude Code plugins do not load Cursor `.mdc` rules; inject always-on rule bodies.
    parts = [HARD_RULES, *_always_apply_rules()]
    return {"additional_context": "\n\n".join(parts)}


def handle_post_tool_use(payload: dict[str, Any], *, inject_rules: bool) -> dict[str, Any]:
    paths = _paths_from_payload(payload)
    parts: list[str] = []
    for path in paths:
        if _is_forbidden_adapters_path(path):
            parts.append(
                f"ArchiPy hygiene: `{Path(path).as_posix()}` is under adapters/ but not "
                "repositories/{domain}/adapters/. Move domain adapters there."
            )
    if inject_rules:
        parts.extend(_matching_rules(paths))
    if not parts:
        return {}
    return {"additional_context": "\n\n".join(parts)}


def main() -> int:
    payload = _read_stdin()
    event = ""
    if len(sys.argv) > 1:
        event = sys.argv[1]
    event = event or str(payload.get("hook_event_name") or payload.get("event") or "")

    if event == CLAUDE_SESSION:
        _emit(handle_claude_session_start(payload))
    elif event in {CURSOR_SESSION, "session_start"}:
        _emit(handle_cursor_session_start(payload))
    elif event == CLAUDE_POST:
        _emit(handle_post_tool_use(payload, inject_rules=True))
    elif event in {CURSOR_POST, "post_tool_use"}:
        _emit(handle_post_tool_use(payload, inject_rules=False))
    else:
        _emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
