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

    def test_scaffold_command_requires_inspect_first_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = root / "skills" / "scaffold-archipy-example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Example\n", encoding="utf-8")
            commands_dir = root / "commands"
            commands_dir.mkdir()
            (commands_dir / "scaffold-example.md").write_text(
                "Follow the **scaffold-archipy-example** skill.\n",
                encoding="utf-8",
            )

            with mock.patch.object(check_catalog, "ROOT", root):
                errors = check_catalog.check_command_skill_refs()

        self.assertIn(
            "commands/scaffold-example.md must read its skill in full and inspect the workspace",
            errors,
        )

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

    def test_claude_session_start_injects_architecture_rule(self) -> None:
        env = os.environ.copy()
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), "SessionStart"],
            cwd=ROOT,
            input="{}",
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["additional_context"]
        self.assertIn("# ArchiPy App Rules Index", context)
        self.assertIn("# Architecture for ArchiPy Apps", context)
        self.assertIn("# Contributing to ArchiPy Apps", context)
        self.assertIn("# Python Code Style for ArchiPy Apps", context)
        self.assertIn("# Security for ArchiPy Apps", context)
        self.assertIn("# Tooling for ArchiPy Apps", context)
        self.assertIn("services → logics", context)

    def test_claude_post_tool_use_injects_glob_rule(self) -> None:
        env = os.environ.copy()
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold_hygiene.py"), "PostToolUse"],
            cwd=ROOT,
            input=json.dumps({"tool_input": {"path": "logics/user/user_logic.py"}}),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("Unit of Work", payload["additional_context"])
        self.assertIn("# Strict Typing for ArchiPy Apps", payload["additional_context"])


if __name__ == "__main__":
    unittest.main()
