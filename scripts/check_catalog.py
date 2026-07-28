#!/usr/bin/env python3
"""Catalog and version sync checks for the ArchiPy consumer plugin."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = (
    ROOT / ".cursor-plugin" / "plugin.json",
    ROOT / ".claude-plugin" / "plugin.json",
    ROOT / ".cursor-plugin" / "marketplace.json",
    ROOT / ".claude-plugin" / "marketplace.json",
)

AGENTS_COMMAND_RE = re.compile(r"`(/[a-z0-9-]+)`")
README_SKILLS_HEADER_RE = re.compile(r"### Skills \((\d+)\)")
README_COMMANDS_HEADER_RE = re.compile(r"### Commands \((\d+)\)")
README_SKILL_ROW_RE = re.compile(r"^\| `([a-z0-9-]+)`\s+\|", re.MULTILINE)
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*([^\s#]+)", re.MULTILINE)


def _fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_version(path: Path) -> str:
    data = _load_json(path)
    if path.name == "marketplace.json":
        plugins = data.get("plugins") or []
        if not plugins:
            raise ValueError(f"{path}: missing plugins[]")
        version = plugins[0].get("version")
    else:
        version = data.get("version")
    if not version:
        raise ValueError(f"{path}: missing version")
    return str(version)


def check_versions() -> list[str]:
    errors: list[str] = []
    versions: dict[Path, str] = {}
    for path in MANIFESTS:
        if not path.is_file():
            errors.append(f"missing manifest: {path.relative_to(ROOT)}")
            continue
        try:
            versions[path] = _manifest_version(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    unique = set(versions.values())
    if len(unique) > 1:
        detail = ", ".join(f"{p.relative_to(ROOT)}={v}" for p, v in sorted(versions.items()))
        errors.append(f"version mismatch across manifests: {detail}")
    return errors


def check_agents_commands() -> list[str]:
    errors: list[str] = []
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    commands_dir = ROOT / "commands"
    mentioned = sorted({m.group(1) for m in AGENTS_COMMAND_RE.finditer(agents) if m.group(1).startswith("/")})
    # AGENTS uses `/command` in a table — keep only slash-command tokens
    for command in mentioned:
        stem = command.lstrip("/")
        path = commands_dir / f"{stem}.md"
        if not path.is_file():
            errors.append(f"AGENTS.md advertises `{command}` but missing commands/{stem}.md")
    return errors


def check_skills() -> list[str]:
    errors: list[str] = []
    skills_root = ROOT / "skills"
    skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        match = FRONTMATTER_NAME_RE.search(text)
        if not match:
            errors.append(f"{skill_dir.name}/SKILL.md missing frontmatter name")
            continue
        name = match.group(1).strip().strip("\"'")
        if name != skill_dir.name:
            errors.append(f"skill folder `{skill_dir.name}` != frontmatter name `{name}`")
    return errors


def check_readme_catalog() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skills_on_disk = sorted(
        p.name for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )
    commands_on_disk = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))

    skills_header = README_SKILLS_HEADER_RE.search(readme)
    commands_header = README_COMMANDS_HEADER_RE.search(readme)
    if not skills_header:
        errors.append("README.md missing `### Skills (N)` header")
    elif int(skills_header.group(1)) != len(skills_on_disk):
        errors.append(
            f"README Skills count {skills_header.group(1)} != disk {len(skills_on_disk)}"
        )
    if not commands_header:
        errors.append("README.md missing `### Commands (N)` header")
    elif int(commands_header.group(1)) != len(commands_on_disk):
        errors.append(
            f"README Commands count {commands_header.group(1)} != disk {len(commands_on_disk)}"
        )

    # Parse skill names from the Skills table only (between Skills and Commands headers)
    skills_section = ""
    if skills_header and commands_header:
        skills_section = readme[skills_header.end() : commands_header.start()]
    readme_skills = README_SKILL_ROW_RE.findall(skills_section)
    missing = sorted(set(skills_on_disk) - set(readme_skills))
    extra = sorted(set(readme_skills) - set(skills_on_disk))
    if missing:
        errors.append(f"README skills table missing: {', '.join(missing)}")
    if extra:
        errors.append(f"README skills table unknown: {', '.join(extra)}")

    for stem in commands_on_disk:
        if f"`/{stem}`" not in readme:
            errors.append(f"README.md missing command `/{stem}`")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_versions())
    errors.extend(check_agents_commands())
    errors.extend(check_skills())
    errors.extend(check_readme_catalog())
    if errors:
        for error in errors:
            _fail(error)
        return 1
    version = _manifest_version(MANIFESTS[0])
    skill_count = len([p for p in (ROOT / "skills").iterdir() if p.is_dir()])
    command_count = len(list((ROOT / "commands").glob("*.md")))
    print(f"OK: version={version} skills={skill_count} commands={command_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
