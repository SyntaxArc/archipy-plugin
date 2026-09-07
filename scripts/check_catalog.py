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
README_RULES_HEADER_RE = re.compile(r"### Rules \((\d+)\)")
README_SKILL_ROW_RE = re.compile(r"^\| `([a-z0-9-]+)`\s+\|", re.MULTILINE)
README_RULE_ROW_RE = re.compile(r"^\| `([a-z0-9-]+\.mdc)`\s+\|", re.MULTILINE)
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*([^\s#]+)", re.MULTILINE)
FRONTMATTER_DESC_RE = re.compile(
    r"^description:\s*(?:>-\s*)?(.*?)(?=\n[a-zA-Z_]+\s*:|\n---)",
    re.MULTILINE | re.DOTALL,
)
SKILL_NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
REFERENCE_FILE_RE = re.compile(r"`(reference/[A-Za-z0-9_.\-/]+)`")
ARCHIPY_REFERENCE_VERSION_RE = re.compile(r"Verified against `archipy` (\d+)\.(\d+)\.x")
COMMAND_SKILL_RE = re.compile(r"Follow the \*\*([a-z0-9-]+)\*\* skill", re.IGNORECASE)
DOCS_SKILL_RE = re.compile(r"Use the \*\*([a-z0-9-]+)\*\* skill", re.IGNORECASE)
CHANGELOG_VERSION_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)

ARCHIPY_5_REMOVED_GUIDANCE = (
    "`elastic-apm`",
    "`prometheus`",
    "`sentry`",
    "`TracingUtils`",
    "`PrometheusUtils`",
    "`capture_span`",
    "`capture_transaction`",
    "`FastAPIRateLimitConfig`",
)
ARCHIPY_5_REQUIRED_GUIDANCE = ("`OtelUtils`", "`trace_span`", "`otel-fastapi`", "`otel-grpc`")
REQUIRED_APP_RULES = {
    "architecture-for-apps.mdc",
    "contributing-for-apps.mdc",
    "python-code-style-for-apps.mdc",
    "rules-index-for-apps.mdc",
    "security-for-apps.mdc",
    "tooling-for-apps.mdc",
    "typing-for-apps.mdc",
}


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


def _plugin_manifests() -> list[Path]:
    return [ROOT / ".cursor-plugin" / "plugin.json", ROOT / ".claude-plugin" / "plugin.json"]


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


def check_manifest_parity() -> list[str]:
    """Ensure Cursor and Claude plugin.json share name/description/keywords."""
    errors: list[str] = []
    plugins = _plugin_manifests()
    if not all(p.is_file() for p in plugins):
        return errors
    left, right = (_load_json(p) for p in plugins)
    for key in ("name", "description", "keywords", "license", "homepage", "repository"):
        if left.get(key) != right.get(key):
            errors.append(f"plugin.json field `{key}` differs between Cursor and Claude manifests")
    for path in plugins:
        data = _load_json(path)
        logo = data.get("logo")
        if logo:
            logo_path = ROOT / str(logo)
            if not logo_path.is_file():
                errors.append(f"{path.relative_to(ROOT)} logo missing: {logo}")
    cursor = _load_json(ROOT / ".cursor-plugin" / "plugin.json")
    claude = _load_json(ROOT / ".claude-plugin" / "plugin.json")
    if cursor.get("hooks") != "./hooks/hooks.json":
        errors.append("Cursor plugin.json hooks must be ./hooks/hooks.json")
    if claude.get("hooks") != "./hooks/claude-hooks.json":
        errors.append("Claude plugin.json hooks must be ./hooks/claude-hooks.json")
    if not (ROOT / "hooks" / "hooks.json").is_file():
        errors.append("missing hooks/hooks.json")
    if not (ROOT / "hooks" / "claude-hooks.json").is_file():
        errors.append("missing hooks/claude-hooks.json")
    return errors


def check_changelog_version() -> list[str]:
    errors: list[str] = []
    changelog = ROOT / "CHANGELOG.md"
    if not changelog.is_file():
        return ["missing CHANGELOG.md"]
    text = changelog.read_text(encoding="utf-8")
    match = CHANGELOG_VERSION_RE.search(text)
    if not match:
        return ["CHANGELOG.md missing `## [X.Y.Z]` heading"]
    changelog_version = match.group(1)
    try:
        manifest_version = _manifest_version(MANIFESTS[0])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    if changelog_version != manifest_version:
        errors.append(
            f"CHANGELOG top version {changelog_version} != manifest version {manifest_version}"
        )
    return errors


def _check_archipy_reference_text(text: str) -> list[str]:
    errors: list[str] = []
    version = ARCHIPY_REFERENCE_VERSION_RE.search(text)
    if not version:
        errors.append("archipy-docs/reference.md missing `Verified against archipy X.Y.x` version")
    elif int(version.group(1)) < 5:
        errors.append("archipy-docs/reference.md must target ArchiPy 5.x or newer")
    for removed in ARCHIPY_5_REMOVED_GUIDANCE:
        if removed in text:
            errors.append(f"archipy-docs/reference.md contains removed ArchiPy 5.x guidance: {removed}")
    for required in ARCHIPY_5_REQUIRED_GUIDANCE:
        if required not in text:
            errors.append(f"archipy-docs/reference.md missing ArchiPy 5.x guidance: {required}")
    return errors


def check_archipy_reference() -> list[str]:
    reference = ROOT / "skills" / "archipy-docs" / "reference.md"
    if not reference.is_file():
        return ["missing skills/archipy-docs/reference.md"]
    return _check_archipy_reference_text(reference.read_text(encoding="utf-8"))


def check_agents_commands() -> list[str]:
    errors: list[str] = []
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    commands_dir = ROOT / "commands"
    mentioned = sorted({m.group(1) for m in AGENTS_COMMAND_RE.finditer(agents) if m.group(1).startswith("/")})
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
        if not SKILL_NAME_RE.fullmatch(name):
            errors.append(f"{skill_dir.name}/SKILL.md has invalid skill name `{name}`")
        desc = FRONTMATTER_DESC_RE.search(text)
        description = desc.group(1).strip() if desc else ""
        if len(description) < 20:
            errors.append(f"{skill_dir.name}/SKILL.md missing or trivial description")
        elif len(description) > 1024:
            errors.append(f"{skill_dir.name}/SKILL.md description exceeds 1024 characters")
        if len(text.splitlines()) > 500:
            errors.append(f"{skill_dir.name}/SKILL.md exceeds 500 lines; move details to reference files")
        for reference in REFERENCE_FILE_RE.findall(text):
            if not (skill_dir / reference).is_file():
                errors.append(f"{skill_dir.name}/SKILL.md references missing `{reference}`")
        if name.startswith("scaffold-") or name == "redis-search":
            if "## Before writing files" not in text:
                errors.append(f"{skill_dir.name}/SKILL.md missing `## Before writing files` workflow")
            if "## Verify" not in text:
                errors.append(f"{skill_dir.name}/SKILL.md missing `## Verify` feedback loop")
    return errors


def check_rules() -> list[str]:
    errors: list[str] = []
    rules_root = ROOT / "rules"
    if not rules_root.is_dir():
        return ["missing rules/"]
    rule_files = sorted(rules_root.glob("*.mdc"))
    if not rule_files:
        errors.append("no rules/*.mdc files")
    missing_required = sorted(REQUIRED_APP_RULES - {rule.name for rule in rule_files})
    if missing_required:
        errors.append(f"missing required app rules: {', '.join(missing_required)}")
    for rule in rule_files:
        text = rule.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if not text.startswith("---\n") or len(parts) < 3:
            errors.append(f"{rule.name} missing valid frontmatter")
            continue
        frontmatter = parts[1]
        if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
            errors.append(f"{rule.name} missing frontmatter description")
        always_apply = re.search(r"^alwaysApply:\s*(true|false)\s*$", frontmatter, re.MULTILINE)
        if not always_apply:
            errors.append(f"{rule.name} missing boolean frontmatter `alwaysApply`")
        elif always_apply.group(1) == "false" and not re.search(r"^globs:\s*\S", frontmatter, re.MULTILINE):
            errors.append(f"{rule.name} requires frontmatter globs when alwaysApply is false")
    return errors


def check_command_skill_refs() -> list[str]:
    errors: list[str] = []
    skills_on_disk = {
        p.name for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    }
    for command in sorted((ROOT / "commands").glob("*.md")):
        text = command.read_text(encoding="utf-8")
        refs = COMMAND_SKILL_RE.findall(text) + DOCS_SKILL_RE.findall(text)
        if not refs:
            errors.append(f"commands/{command.name} has no Follow/Use **skill** reference")
            continue
        for skill in refs:
            if skill not in skills_on_disk:
                errors.append(f"commands/{command.name} references missing skill `{skill}`")
        if command.stem.startswith("scaffold-") or command.stem == "redis-search":
            if "in full" not in text or "Inspect the workspace" not in text:
                errors.append(
                    f"commands/{command.name} must read its skill in full and inspect the workspace"
                )
    return errors


def check_readme_catalog() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skills_on_disk = sorted(
        p.name for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )
    commands_on_disk = sorted(p.stem for p in (ROOT / "commands").glob("*.md"))
    rules_on_disk = sorted(p.name for p in (ROOT / "rules").glob("*.mdc"))

    skills_header = README_SKILLS_HEADER_RE.search(readme)
    commands_header = README_COMMANDS_HEADER_RE.search(readme)
    rules_header = README_RULES_HEADER_RE.search(readme)
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
    if not rules_header:
        errors.append("README.md missing `### Rules (N)` header")
    elif int(rules_header.group(1)) != len(rules_on_disk):
        errors.append(f"README Rules count {rules_header.group(1)} != disk {len(rules_on_disk)}")

    skills_section = ""
    if skills_header and commands_header:
        skills_section = readme[skills_header.end(): commands_header.start()]
    readme_skills = README_SKILL_ROW_RE.findall(skills_section)
    missing = sorted(set(skills_on_disk) - set(readme_skills))
    extra = sorted(set(readme_skills) - set(skills_on_disk))
    if missing:
        errors.append(f"README skills table missing: {', '.join(missing)}")
    if extra:
        errors.append(f"README skills table unknown: {', '.join(extra)}")

    rules_section = ""
    if rules_header and skills_header:
        rules_section = readme[rules_header.end(): skills_header.start()]
    readme_rules = README_RULE_ROW_RE.findall(rules_section)
    missing_rules = sorted(set(rules_on_disk) - set(readme_rules))
    extra_rules = sorted(set(readme_rules) - set(rules_on_disk))
    if missing_rules:
        errors.append(f"README rules table missing: {', '.join(missing_rules)}")
    if extra_rules:
        errors.append(f"README rules table unknown: {', '.join(extra_rules)}")

    for stem in commands_on_disk:
        if f"`/{stem}`" not in readme:
            errors.append(f"README.md missing command `/{stem}`")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_versions())
    errors.extend(check_manifest_parity())
    errors.extend(check_changelog_version())
    errors.extend(check_archipy_reference())
    errors.extend(check_agents_commands())
    errors.extend(check_skills())
    errors.extend(check_rules())
    errors.extend(check_command_skill_refs())
    errors.extend(check_readme_catalog())
    if errors:
        for error in errors:
            _fail(error)
        return 1
    version = _manifest_version(MANIFESTS[0])
    skill_count = len(
        [p for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
    )
    command_count = len(list((ROOT / "commands").glob("*.md")))
    rule_count = len(list((ROOT / "rules").glob("*.mdc")))
    print(f"OK: version={version} skills={skill_count} commands={command_count} rules={rule_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
