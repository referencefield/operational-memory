#!/usr/bin/env python3
"""Regression self-tests for tools/validate_protocol.py.

These tests exercise the validator as a black box against temporary copies of
this repository. They intentionally cover a small number of high-value
invariants rather than duplicating the validator implementation.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValidatorRegressionTests(unittest.TestCase):
    def make_copy(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        target = Path(temp_dir.name) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        return target

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "tools/validate_protocol.py"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_fails_with(self, result: subprocess.CompletedProcess[str], text: str) -> None:
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(text, output)
        self.assertIn("RESULT: FAIL", output)

    def test_current_repository_passes(self) -> None:
        root = self.make_copy()
        result = self.run_validator(root)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("RESULT: PASS", output)

    def test_documented_bootloader_drift_fails(self) -> None:
        root = self.make_copy()
        setup_path = root / "SETUP.md"
        text = setup_path.read_text(encoding="utf-8")
        needle = "<!-- BOOTLOADER-DOC-START -->\n> Operational Memory:"
        replacement = "<!-- BOOTLOADER-DOC-START -->\n> Altered Operational Memory:"
        self.assertIn(needle, text)
        setup_path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")

        result = self.run_validator(root)
        self.assert_fails_with(result, "documented bootloader does not match")

    def test_missing_main_push_trigger_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "      - main\n"
        self.assertIn(needle, text)
        workflow_path.write_text(text.replace(needle, "", 1), encoding="utf-8")

        result = self.run_validator(root)
        self.assert_fails_with(result, "push trigger must include canonical main")

    def test_supported_plan_manifest_drift_fails(self) -> None:
        root = self.make_copy()
        manifest_path = root / "PROTOCOL.yaml"
        text = manifest_path.read_text(encoding="utf-8")
        needle = "minimum_supported_chatgpt_plan: plus"
        self.assertIn(needle, text)
        manifest_path.write_text(
            text.replace(needle, "minimum_supported_chatgpt_plan: free", 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "compatibility.minimum_supported_chatgpt_plan must be 'plus'",
        )

    def test_absolute_manifest_path_fails(self) -> None:
        root = self.make_copy()
        outside = root.parent / "outside-current.md"
        outside.write_text("outside\n", encoding="utf-8")

        manifest_path = root / "PROTOCOL.yaml"
        text = manifest_path.read_text(encoding="utf-8")
        needle = "  current: CURRENT.md"
        self.assertIn(needle, text)
        manifest_path.write_text(
            text.replace(needle, f"  current: {outside}", 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "PROTOCOL.yaml global.current must be repository-relative",
        )

    def test_parent_traversal_manifest_path_fails(self) -> None:
        root = self.make_copy()
        outside = root.parent / "outside-current.md"
        outside.write_text("outside\n", encoding="utf-8")

        manifest_path = root / "PROTOCOL.yaml"
        text = manifest_path.read_text(encoding="utf-8")
        needle = "  current: CURRENT.md"
        self.assertIn(needle, text)
        manifest_path.write_text(
            text.replace(needle, "  current: ../outside-current.md", 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "PROTOCOL.yaml global.current must not contain parent traversal",
        )

    def test_symlink_escape_manifest_path_fails(self) -> None:
        root = self.make_copy()
        outside = root.parent / "outside-current.md"
        outside.write_text("outside\n", encoding="utf-8")
        link = root / "ESCAPE-CURRENT.md"
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

        manifest_path = root / "PROTOCOL.yaml"
        text = manifest_path.read_text(encoding="utf-8")
        needle = "  current: CURRENT.md"
        self.assertIn(needle, text)
        manifest_path.write_text(
            text.replace(needle, "  current: ESCAPE-CURRENT.md", 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "PROTOCOL.yaml global.current resolves outside repository",
        )

    def test_trigger_only_workflow_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        workflow_path.write_text(
            """name: Trigger-only validation

on:
  pull_request:
  push:
    branches:
      - main
  workflow_dispatch:
""",
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(result, "must define at least one validation job")

    def test_missing_workflow_contents_read_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "permissions:\n  contents: read\n\n"
        self.assertIn(needle, text)
        workflow_path.write_text(text.replace(needle, "", 1), encoding="utf-8")

        result = self.run_validator(root)
        self.assert_fails_with(result, "must declare top-level permissions.contents: read")

    def test_missing_workflow_checkout_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "        uses: actions/checkout@v7\n"
        self.assertIn(needle, text)
        workflow_path.write_text(text.replace(needle, "", 1), encoding="utf-8")

        result = self.run_validator(root)
        self.assert_fails_with(result, "validation job must check out the repository")

    def test_missing_pinned_validator_dependency_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = '        run: python -m pip install "PyYAML==6.0.2"\n'
        self.assertIn(needle, text)
        workflow_path.write_text(
            text.replace(needle, "        run: python -m pip install PyYAML\n", 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(result, "validation job must install pinned PyYAML==6.0.2")

    def test_missing_regression_test_step_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "        run: python tools/test_validate_protocol.py\n"
        self.assertIn(needle, text)
        workflow_path.write_text(
            text.replace(needle, '        run: python -c "print(1)"\n', 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(result, "validation job must run tools/test_validate_protocol.py")

    def test_missing_structural_validator_step_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "        run: python tools/validate_protocol.py\n"
        self.assertIn(needle, text)
        workflow_path.write_text(
            text.replace(needle, '        run: python -c "print(2)"\n', 1),
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(result, "validation job must run tools/validate_protocol.py")

    def test_missing_manual_dispatch_trigger_fails(self) -> None:
        root = self.make_copy()
        workflow_path = root / ".github" / "workflows" / "protocol-validation.yml"
        text = workflow_path.read_text(encoding="utf-8")
        needle = "  workflow_dispatch:\n"
        self.assertIn(needle, text)
        workflow_path.write_text(text.replace(needle, "", 1), encoding="utf-8")

        result = self.run_validator(root)
        self.assert_fails_with(result, "must run on workflow_dispatch")

    def test_active_current_decision_reference_passes(self) -> None:
        root = self.make_copy()
        current_path = root / "CURRENT.md"
        current_path.write_text(
            current_path.read_text(encoding="utf-8")
            + "\n## Explicit decision reference test\n\nCurrent authority: D-101.\n",
            encoding="utf-8",
        )

        decisions_path = root / "DECISIONS.md"
        decisions_path.write_text(
            decisions_path.read_text(encoding="utf-8")
            + """
### D-101 — Active reference test

- **Status:** active
- **Date:** 2026-09-18
- **Decision:** Use the active synthetic option.
- **Why / evidence:** Regression fixture.
- **Supersedes:** none.
- **Superseded by:** none.
""",
            encoding="utf-8",
        )

        result = self.run_validator(root)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("RESULT: PASS", output)

    def test_missing_current_decision_reference_fails(self) -> None:
        root = self.make_copy()
        current_path = root / "CURRENT.md"
        current_path.write_text(
            current_path.read_text(encoding="utf-8")
            + "\n## Explicit decision reference test\n\nCurrent authority: D-998.\n",
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "CURRENT.md references missing active decision D-998 in DECISIONS.md",
        )

    def test_superseded_current_decision_reference_fails(self) -> None:
        root = self.make_copy()
        current_path = root / "CURRENT.md"
        current_path.write_text(
            current_path.read_text(encoding="utf-8")
            + "\n## Explicit decision reference test\n\nCurrent authority: D-201.\n",
            encoding="utf-8",
        )

        decisions_path = root / "DECISIONS.md"
        decisions_path.write_text(
            decisions_path.read_text(encoding="utf-8")
            + """
### D-201 — Superseded reference test

- **Status:** superseded
- **Date:** 2026-09-18
- **Decision:** Use the old synthetic option.
- **Why / evidence:** Regression fixture.
- **Supersedes:** none.
- **Superseded by:** D-202.

### D-202 — Active replacement test

- **Status:** active
- **Date:** 2026-09-18
- **Decision:** Use the replacement synthetic option.
- **Why / evidence:** Regression fixture.
- **Supersedes:** D-201.
- **Superseded by:** none.
""",
            encoding="utf-8",
        )

        result = self.run_validator(root)
        self.assert_fails_with(
            result,
            "CURRENT.md references non-active decision D-201 in DECISIONS.md",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
