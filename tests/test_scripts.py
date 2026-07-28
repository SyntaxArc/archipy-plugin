"""Tests for scripts/check_catalog.py and scripts/scaffold_hygiene.py."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
