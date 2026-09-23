#!/usr/bin/env python3
"""Plugin hook: ArchiPy scaffold hygiene reminders for consumer apps."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

# Any adapters/*.py outside repositories/{domain}/adapters/ is forbidden for ArchiPy apps.
ADAPTERS_FILE_RE = re.compile(r"(^|/)adapters/[^/]+\.py$")
REPO_ADAPTERS_RE = re.compile(r"(^|/)repositories/[^/]+/adapters/")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)

HARD_RULES = (
    "ArchiPy apps: follow architecture-for-apps rule + skills/archipy-docs/reference.md. "
    "Domain adapters under repositories/{domain}/adapters/ only. "
    "Prefer the plugin skills (/scaffold-*, /redis-search, archipy-docs)."
)

# Cursor event names (camelCase). Claude Code uses PascalCase and a different hooks.json schema.
CURSOR_SESSION = "sessionStart"
CURSOR_POST = "postToolUse"
CLAUDE_SESSION = "SessionStart"
CLAUDE_POST = "PostToolUse"
CLAUDE_PRE = "PreToolUse"
CURSOR_PRE = "preToolUse"

# Markers that identify an ArchiPy consumer app; rules stay out of unrelated projects.
ARCHIPY_MARKERS = ("pyproject.toml", "uv.lock", "requirements.txt")
UV_LOCK_ARCHIPY_RE = re.compile(r'^\[\[package\]\]\nname = "archipy"\nversion = "([^"]+)"', re.MULTILINE)
PYPROJECT_ARCHIPY_RE = re.compile(r"""["']archipy(?:\[([^\]]*)\])?\s*([<>=~!][^"']*)?["']""")
ARCHIPY_DEP_RE = re.compile(r"""(^|[\s"'\[,])archipy([\s"'\[\]=<>~!,]|$)""", re.MULTILINE)


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


def _emit_claude(event: str, context: str) -> dict[str, Any]:
    """Build Claude Code hook output; Claude ignores Cursor's top-level `additional_context`."""
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}


def _project_dir(payload: dict[str, Any]) -> Path:
    """Claude sends `cwd`; Cursor sends `cwd` on tool events and `workspace_roots` on every event."""
    roots = payload.get("workspace_roots")
    root = roots[0] if isinstance(roots, list) and roots else None
    return Path(str(payload.get("cwd") or root or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()))


def _archipy_app_root(payload: dict[str, Any]) -> Path | None:
    """Return the project directory when it (or a parent up to the repo root) depends on ArchiPy."""
    start = _project_dir(payload)
    for directory in (start, *start.parents):
        found_marker = False
        for marker in ARCHIPY_MARKERS:
            path = directory / marker
            if not path.is_file():
                continue
            found_marker = True
            try:
                if ARCHIPY_DEP_RE.search(path.read_text(encoding="utf-8", errors="ignore")):
                    return directory
            except OSError:
                continue
        if found_marker or (directory / ".git").exists():
            return None
    return None


def _is_archipy_app(payload: dict[str, Any]) -> bool:
    return _archipy_app_root(payload) is not None


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _archipy_version_line(app_root: Path) -> str:
    """Describe the app's pinned ArchiPy version and extras; empty when unknown."""
    locked = UV_LOCK_ARCHIPY_RE.search(_read(app_root / "uv.lock"))
    declared = PYPROJECT_ARCHIPY_RE.search(_read(app_root / "pyproject.toml"))
    version = locked.group(1) if locked else (declared.group(2) or "").strip() if declared else ""
    extras = (declared.group(1) or "").replace(" ", "") if declared else ""
    if not version:
        return ""
    line = f"This app uses archipy {version}"
    if extras:
        line += f" with extras [{extras}]"
    return line + ". Only suggest APIs and extras available in that version; check live docs when unsure."


def _dedupe_key(payload: dict[str, Any]) -> str:
    # Subagents share the parent session_id; key them separately so the main thread still gets rules.
    return "-".join(str(payload.get(key) or "") for key in ("session_id", "agent_id")).rstrip("-")


def _seen_rules_file(session_id: str) -> Path | None:
    safe = re.sub(r"[^A-Za-z0-9_-]", "", session_id)
    if not safe:
        return None
    return Path(tempfile.gettempdir()) / f"archipy-plugin-rules-{safe}.json"


def _unseen_rules(session_id: str, rule_names: list[str]) -> list[str]:
    """Filter rules already injected this session and record the new ones."""
    state = _seen_rules_file(session_id)
    if state is None:
        return rule_names
    try:
        seen = set(json.loads(state.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        seen = set()
    fresh = [name for name in rule_names if name not in seen]
    if fresh:
        try:
            state.write_text(json.dumps(sorted(seen | set(fresh))), encoding="utf-8")
        except OSError:
            pass
    return fresh


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


def _matching_rules(file_paths: list[str]) -> list[tuple[str, str]]:
    rules_dir = _plugin_root() / "rules"
    if not rules_dir.is_dir():
        return []
    chunks: list[tuple[str, str]] = []
    seen: set[str] = set()
    for rule in sorted(rules_dir.glob("*.mdc")):
        meta, body = _parse_rule(rule)
        globs = meta.get("globs", "")
        if not globs or not body.strip():
            continue
        if any(_path_matches(path, globs) for path in file_paths):
            if rule.name not in seen:
                seen.add(rule.name)
                chunks.append((rule.name, body.strip()))
    return chunks


def _session_context(app_root: Path, *, include_rules: bool) -> str:
    parts = [HARD_RULES]
    if version_line := _archipy_version_line(app_root):
        parts.append(version_line)
    if include_rules:
        parts.extend(_always_apply_rules())
    return "\n\n".join(parts)


def handle_cursor_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    # Cursor loads `.mdc` rules natively; only add the reminder and version line in ArchiPy apps.
    app_root = _archipy_app_root(payload)
    if app_root is None:
        return {}
    return {"additional_context": _session_context(app_root, include_rules=False)}


def handle_claude_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    # Startup/resume/clear/compact may drop earlier rule context; let path-scoped rules inject again.
    state = _seen_rules_file(_dedupe_key(payload))
    if state is not None:
        state.unlink(missing_ok=True)
    # Claude Code plugins do not load Cursor `.mdc` rules; inject always-on rule bodies in ArchiPy apps only.
    app_root = _archipy_app_root(payload)
    if app_root is None:
        return {}
    return _emit_claude(CLAUDE_SESSION, _session_context(app_root, include_rules=True))


def _hygiene_warnings(paths: list[str]) -> list[str]:
    parts: list[str] = []
    for path in paths:
        if _is_forbidden_adapters_path(path):
            parts.append(
                f"ArchiPy hygiene: `{Path(path).as_posix()}` is under adapters/ but not "
                "repositories/{domain}/adapters/. Move domain adapters there."
            )
    return parts


def _relative_to_cwd(file_path: str, cwd: str) -> str | None:
    """Return file_path relative to cwd, or None when it lies outside the project."""
    path = Path(file_path)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(Path(cwd)).as_posix()
    except ValueError:
        return None


def _new_adapter_violation(payload: dict[str, Any]) -> str | None:
    """Reason to block a Write that creates a domain adapter outside repositories/{domain}/adapters/.

    Only new files are blocked: legacy apps must still be able to edit an existing top-level adapters/ package.
    """
    if payload.get("tool_name") != "Write" or not _is_archipy_app(payload):
        return None
    cwd = str(_project_dir(payload))
    for file_path in _paths_from_payload(payload):
        relative = _relative_to_cwd(file_path, cwd)
        if relative is None or not _is_forbidden_adapters_path(relative):
            continue
        if (Path(cwd) / relative).exists():
            continue
        return (
            f"ArchiPy apps keep domain adapters under repositories/{{domain}}/adapters/, not `{relative}`. "
            "Write it as repositories/<domain>/adapters/<name>_adapter.py instead."
        )
    return None


def handle_claude_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    reason = _new_adapter_violation(payload)
    if reason is None:
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": CLAUDE_PRE,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def handle_cursor_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    reason = _new_adapter_violation(payload)
    if reason is None:
        return {}
    return {"permission": "deny", "user_message": reason, "agent_message": reason}


def handle_cursor_post_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    parts = _hygiene_warnings(_paths_from_payload(payload))
    if not parts:
        return {}
    return {"additional_context": "\n\n".join(parts)}


def handle_claude_post_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_archipy_app(payload):
        return {}
    paths = _paths_from_payload(payload)
    parts = _hygiene_warnings(paths)
    rules = dict(_matching_rules(paths))
    # Inject each path-scoped rule once per session instead of on every edit.
    for name in _unseen_rules(_dedupe_key(payload), list(rules)):
        parts.append(rules[name])
    if not parts:
        return {}
    return _emit_claude(CLAUDE_POST, "\n\n".join(parts))


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
    elif event == CLAUDE_PRE:
        _emit(handle_claude_pre_tool_use(payload))
    elif event in {CURSOR_PRE, "pre_tool_use"}:
        _emit(handle_cursor_pre_tool_use(payload))
    elif event == CLAUDE_POST:
        _emit(handle_claude_post_tool_use(payload))
    elif event in {CURSOR_POST, "post_tool_use"}:
        _emit(handle_cursor_post_tool_use(payload))
    else:
        _emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
