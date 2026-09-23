"""Tests for scripts/check_catalog.py and scripts/scaffold_hygiene.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import check_catalog

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class CatalogTests(unittest.TestCase):
    def test_check_catalog_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_catalog.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: version=", result.stdout)

    def test_scaffold_skill_requires_verification_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = root / "skills" / "scaffold-example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: scaffold-example\n"
                "description: Scaffold an example component when requested by the user.\n"
                "---\n"
                "# Example\n"
                "## Before writing files\n"
                "Inspect the repository.\n",
                encoding="utf-8",
            )

            with mock.patch.object(check_catalog, "ROOT", root):
                errors = check_catalog.check_skills()

        self.assertIn(
            "scaffold-example/SKILL.md missing `## Verify` feedback loop",
            errors,
        )

    def _write_skill(self, root: Path, name: str, body: str, frontmatter: str = "") -> None:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Example skill used by catalog tests for validation.\n{frontmatter}---\n{body}",
            encoding="utf-8",
        )

    def _skill_errors(self, root: Path) -> list[str]:
        with mock.patch.object(check_catalog, "ROOT", root):
            return check_catalog.check_skills()

    def test_scaffold_skill_requires_do_not_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self._write_skill(root, "scaffold-example", "## Before writing files\nInspect.\n## Verify\nRun checks.\n")
            errors = self._skill_errors(root)
        self.assertIn("scaffold-example/SKILL.md missing `## Do not` constraints", errors)
        self.assertIn("scaffold-example/SKILL.md `## Verify` must end with a report step", errors)

    def test_complete_scaffold_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self._write_skill(
                root,
                "scaffold-example",
                "## Before writing files\nInspect.\n## Do not\n- Overwrite.\n## Verify\n1. Report files.\n",
            )
            self.assertEqual(self._skill_errors(root), [])

    def test_docs_skill_must_disable_model_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self._write_skill(root, "docs-example", "Docs.\n")
            self._write_skill(root, "other", "Other.\n", "disable-model-invocation: true\n")
            errors = self._skill_errors(root)
        self.assertIn("docs-example/SKILL.md must set `disable-model-invocation: true`", errors)
        self.assertIn("other/SKILL.md must stay model-invocable", errors)

    def test_skill_relative_paths_must_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "rules").mkdir()
            (root / "rules" / "real.mdc").write_text("x", encoding="utf-8")
            self._write_skill(
                root,
                "example",
                "Read `../../rules/real.mdc`, `${CLAUDE_SKILL_DIR}/../../rules/gone.mdc`, and `../...`.\n",
            )
            errors = self._skill_errors(root)
        self.assertEqual(errors, ["example/SKILL.md references missing `../../rules/gone.mdc`"])

    def test_agents_commands_must_be_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "skills" / "scaffold-real").mkdir(parents=True)
            (root / "skills" / "scaffold-real" / "SKILL.md").write_text("x", encoding="utf-8")
            (root / "AGENTS.md").write_text("Use `/scaffold-real` or `/scaffold-gone`.\n", encoding="utf-8")
            with mock.patch.object(check_catalog, "ROOT", root):
                errors = check_catalog.check_agents_commands()
        self.assertEqual(errors, ["AGENTS.md advertises `/scaffold-gone` but missing skills/scaffold-gone/SKILL.md"])

    def test_skill_reference_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = root / "skills" / "example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: example\n"
                "description: Read an example template when handling example requests.\n"
                "---\n"
                "# Example\n"
                "Use `reference/missing.py`.\n",
                encoding="utf-8",
            )

            with mock.patch.object(check_catalog, "ROOT", root):
                errors = check_catalog.check_skills()

        self.assertIn(
            "example/SKILL.md references missing `reference/missing.py`",
            errors,
        )

    def test_archipy_reference_rejects_pre_5_guidance(self) -> None:
        errors = check_catalog._check_archipy_reference_text(
            "Verified against `archipy` 4.17.x.\n"
            "Use `TracingUtils` and `capture_span`.\n",
        )

        self.assertIn(
            "archipy-docs/reference.md must target ArchiPy 5.x or newer",
            errors,
        )
        self.assertIn(
            "archipy-docs/reference.md contains removed ArchiPy 5.x guidance: `TracingUtils`",
            errors,
        )


class HygieneTests(unittest.TestCase):
    def test_session_start(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), "sessionStart"],
            cwd=ROOT,
            input="{}",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn("additional_context", payload)
        self.assertIn("repositories/{domain}/adapters", payload["additional_context"])

    def test_allows_repo_adapters(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), "postToolUse"],
            cwd=ROOT,
            input=json.dumps({"tool_input": {"path": "repositories/user/adapters/user_db_adapter.py"}}),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(result.stdout, {"", "{}"})

    def test_warns_non_repo_adapters(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), "postToolUse"],
            cwd=ROOT,
            input=json.dumps({"tool_input": {"path": "adapters/redis_adapter.py"}}),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn("additional_context", payload)
        self.assertIn("repositories/{domain}/adapters", payload["additional_context"])
        self.assertNotIn("# Architecture for ArchiPy Apps", payload["additional_context"])

    def _run_claude(self, event: str, payload: dict[str, object]) -> dict[str, object]:
        env = os.environ.copy()
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), event],
            cwd=ROOT,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def _archipy_app(self) -> str:
        app = tempfile.TemporaryDirectory()
        self.addCleanup(app.cleanup)
        Path(app.name, "pyproject.toml").write_text(
            '[project]\nname = "demo"\ndependencies = ["archipy[postgres]>=5.4"]\n',
            encoding="utf-8",
        )
        return app.name

    def _claude_context(self, payload: dict[str, object], event: str) -> str:
        output = payload["hookSpecificOutput"]
        assert isinstance(output, dict)
        self.assertEqual(output["hookEventName"], event)
        self.assertNotIn("additional_context", payload)
        return str(output["additionalContext"])

    def test_claude_session_start_injects_architecture_rule(self) -> None:
        payload = self._run_claude("SessionStart", {"cwd": self._archipy_app()})
        context = self._claude_context(payload, "SessionStart")
        self.assertIn("# ArchiPy App Rules Index", context)
        self.assertIn("# Architecture for ArchiPy Apps", context)
        self.assertIn("# Contributing to ArchiPy Apps", context)
        self.assertIn("# Python Code Style for ArchiPy Apps", context)
        self.assertIn("# Security for ArchiPy Apps", context)
        self.assertIn("# Tooling for ArchiPy Apps", context)
        self.assertIn("services → logics", context)

    def test_claude_session_start_skips_non_archipy_project(self) -> None:
        with tempfile.TemporaryDirectory() as other:
            Path(other, "pyproject.toml").write_text('[project]\nname = "archipy-plugin"\n', encoding="utf-8")
            self.assertEqual(self._run_claude("SessionStart", {"cwd": other}), {})

    def test_claude_post_tool_use_injects_glob_rule(self) -> None:
        payload = self._run_claude(
            "PostToolUse",
            {"cwd": self._archipy_app(), "tool_input": {"file_path": "logics/user/user_logic.py"}},
        )
        context = self._claude_context(payload, "PostToolUse")
        self.assertIn("Unit of Work", context)
        self.assertIn("# Strict Typing for ArchiPy Apps", context)

    def test_claude_post_tool_use_injects_rule_once_per_session(self) -> None:
        session_id = f"test-{os.getpid()}-{id(self)}"
        state = Path(tempfile.gettempdir()) / f"archipy-plugin-rules-{session_id}.json"
        self.addCleanup(state.unlink, missing_ok=True)
        app = self._archipy_app()
        edit = {"cwd": app, "session_id": session_id, "tool_input": {"file_path": "logics/user/user_logic.py"}}
        first = self._run_claude("PostToolUse", edit)
        self.assertIn("Unit of Work", self._claude_context(first, "PostToolUse"))
        self.assertEqual(self._run_claude("PostToolUse", edit), {})
        warning = self._run_claude(
            "PostToolUse",
            {"cwd": app, "session_id": session_id, "tool_input": {"file_path": "adapters/redis_adapter.py"}},
        )
        self.assertIn("repositories/{domain}/adapters", self._claude_context(warning, "PostToolUse"))

    def test_claude_session_start_resets_rule_dedupe(self) -> None:
        session_id = f"test-reset-{os.getpid()}-{id(self)}"
        state = Path(tempfile.gettempdir()) / f"archipy-plugin-rules-{session_id}.json"
        self.addCleanup(state.unlink, missing_ok=True)
        app = self._archipy_app()
        edit = {"cwd": app, "session_id": session_id, "tool_input": {"file_path": "logics/user/user_logic.py"}}
        self._run_claude("PostToolUse", edit)
        self.assertEqual(self._run_claude("PostToolUse", edit), {})
        self._run_claude("SessionStart", {"cwd": app, "session_id": session_id, "source": "compact"})
        self.assertIn("Unit of Work", self._claude_context(self._run_claude("PostToolUse", edit), "PostToolUse"))

    def test_claude_post_tool_use_dedupes_subagents_separately(self) -> None:
        session_id = f"test-agent-{os.getpid()}-{id(self)}"
        tmp = Path(tempfile.gettempdir())
        for suffix in ("", "-sub1"):
            self.addCleanup((tmp / f"archipy-plugin-rules-{session_id}{suffix}.json").unlink, missing_ok=True)
        app = self._archipy_app()
        edit = {"cwd": app, "session_id": session_id, "tool_input": {"file_path": "logics/user/user_logic.py"}}
        self._run_claude("PostToolUse", {**edit, "agent_id": "sub1"})
        self.assertIn("Unit of Work", self._claude_context(self._run_claude("PostToolUse", edit), "PostToolUse"))

    def test_claude_post_tool_use_absolute_paths(self) -> None:
        app = self._archipy_app()
        logic = self._run_claude("PostToolUse", {"cwd": app, "tool_input": {"file_path": f"{app}/logics/user/user_logic.py"}})
        self.assertIn("Unit of Work", self._claude_context(logic, "PostToolUse"))
        adapter = self._run_claude("PostToolUse", {"cwd": app, "tool_input": {"file_path": f"{app}/adapters/redis_adapter.py"}})
        self.assertIn("repositories/{domain}/adapters", self._claude_context(adapter, "PostToolUse"))
        nested = self._run_claude(
            "PostToolUse", {"cwd": app, "tool_input": {"file_path": f"{app}/repositories/user/adapters/user_db_adapter.py"}}
        )
        self.assertNotIn("is under adapters/ but not", self._claude_context(nested, "PostToolUse"))

if __name__ == "__main__":
    unittest.main()
