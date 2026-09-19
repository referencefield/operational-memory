#!/usr/bin/env python3
"""Advisory structural validator for Operational Memory.

This intentionally checks only machine-verifiable repository invariants.
Semantic questions remain part of the ChatGPT health check described in OPERATIONS.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required to run tools/validate_protocol.py")
    print("Install with: python -m pip install pyyaml")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
ROOT_RESOLVED = ROOT.resolve()
ERRORS: list[str] = []
WARNINGS: list[str] = []
LEGACY_REPOSITORY_SLUG = "chatgpt" + "-operational-memory"
LEGACY_PROJECT_NAME = "ChatGPT" + " Operational Memory"
REMOVED_END_SESSION_TERMS = (
    "close" + "out",
    "close " + "out operational memory",
    "closing " + "out an important session",
)
AMBIGUOUS_SUPPORT_TERMS = (
    "paid chatgpt " + "plan",
    "paid chatgpt " + "account",
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py"}


def error(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def confined_path(path: str, role: str, base: Path = ROOT) -> Path | None:
    raw = str(path).strip()
    if not raw:
        error(f"missing {role}")
        return None

    posix = PurePosixPath(raw)
    windows = PureWindowsPath(raw)
    if posix.is_absolute() or windows.is_absolute():
        error(f"{role} must be repository-relative: {raw}")
        return None
    if ".." in posix.parts or ".." in windows.parts:
        error(f"{role} must not contain parent traversal: {raw}")
        return None

    base_resolved = base.resolve(strict=False)
    if not base_resolved.is_relative_to(ROOT_RESOLVED):
        error(f"{role} base resolves outside repository: {base}")
        return None

    target = (base_resolved / raw).resolve(strict=False)
    if not target.is_relative_to(ROOT_RESOLVED):
        error(f"{role} resolves outside repository: {raw}")
        return None
    return target


def require_file(path: str, role: str = "required file", base: Path = ROOT) -> Path:
    target = confined_path(path, role, base)
    if target is None:
        return ROOT / "__INVALID_PATH__"
    if not target.is_file():
        error(f"missing {role}: {path}")
    return target


def require_directory(path: str, role: str = "required directory", base: Path = ROOT) -> Path:
    target = confined_path(path, role, base)
    if target is None:
        return ROOT / "__INVALID_DIRECTORY__"
    if not target.is_dir():
        error(f"missing {role}: {path}")
    return target


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def text_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(ROOT_RESOLVED):
            error(
                f"repository path resolves outside repository: {path.relative_to(ROOT)}"
            )
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def ids_in(text: str, prefix: str) -> list[str]:
    return re.findall(rf"^###\s+({re.escape(prefix)}-\d+)\b", text, re.MULTILINE)


def check_unique_ids(path: Path, prefix: str) -> set[str]:
    text = read_text(path)
    ids = ids_in(text, prefix)
    seen: set[str] = set()
    for item in ids:
        if item in seen:
            error(f"duplicate {item} in {path.relative_to(ROOT)}")
        seen.add(item)
    return seen


def referenced_ids(value: str, prefix: str) -> Iterable[str]:
    if value.strip().lower() in {"none", "none.", "n/a", ""}:
        return []
    return re.findall(rf"\b{re.escape(prefix)}-\d+\b", value)


def field_value(block: str, label: str) -> str:
    match = re.search(
        rf"^- \*\*{re.escape(label)}:\*\*\s*([^\n]+)",
        block,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def entry_blocks(text: str, prefix: str) -> dict[str, str]:
    matches = list(
        re.finditer(rf"^###\s+({re.escape(prefix)}-\d+)\b", text, re.MULTILINE)
    )
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[match.start():end]
    return blocks


def is_example_block(block: str) -> bool:
    first_line = block.splitlines()[0].lower() if block.splitlines() else ""
    return "example only" in first_line


def check_references(path: Path, prefix: str) -> None:
    text = read_text(path)
    known = set(ids_in(text, prefix))
    for label in ("Supersedes", "Superseded by"):
        pattern = rf"^- \*\*{re.escape(label)}:\*\*\s*(.+)$"
        for match in re.finditer(pattern, text, re.MULTILINE):
            for ref in referenced_ids(match.group(1), prefix):
                if ref not in known:
                    error(
                        f"{path.relative_to(ROOT)} references missing {ref} in {label}"
                    )


def check_lifecycle_consistency(path: Path, prefix: str) -> None:
    records = entry_blocks(read_text(path), prefix)
    for item_id, block in records.items():
        if is_example_block(block):
            continue

        status = field_value(block, "Status").lower()
        supersedes = set(referenced_ids(field_value(block, "Supersedes"), prefix))
        superseded_by = set(
            referenced_ids(field_value(block, "Superseded by"), prefix)
        )

        if status.startswith("active") and superseded_by:
            error(
                f"{path.relative_to(ROOT)} {item_id} is active but has Superseded by"
            )
        if status == "superseded" and not superseded_by:
            error(
                f"{path.relative_to(ROOT)} {item_id} is superseded but has no Superseded by ID"
            )

        for prior_id in supersedes:
            prior_block = records.get(prior_id)
            if prior_block is None or is_example_block(prior_block):
                continue
            reciprocal = set(
                referenced_ids(field_value(prior_block, "Superseded by"), prefix)
            )
            if item_id not in reciprocal:
                error(
                    f"{path.relative_to(ROOT)} {item_id} supersedes {prior_id}, "
                    f"but {prior_id} does not reciprocally name {item_id} in Superseded by"
                )

        for later_id in superseded_by:
            later_block = records.get(later_id)
            if later_block is None or is_example_block(later_block):
                continue
            reciprocal = set(
                referenced_ids(field_value(later_block, "Supersedes"), prefix)
            )
            if item_id not in reciprocal:
                error(
                    f"{path.relative_to(ROOT)} {item_id} is superseded by {later_id}, "
                    f"but {later_id} does not reciprocally name {item_id} in Supersedes"
                )


def active_count(path: Path, prefix: str) -> int:
    count = 0
    for block in entry_blocks(read_text(path), prefix).values():
        if is_example_block(block):
            continue
        status = field_value(block, "Status").lower()
        if status.startswith("active"):
            count += 1
    return count


def budget_bytes(path: str, limit: int, label: str) -> None:
    target = confined_path(path, f"soft budget path for {label}")
    if target is None:
        return
    if target.is_file() and target.stat().st_size > limit:
        warn(f"soft budget crossed: {label} is {target.stat().st_size} bytes > {limit}")


def check_legacy_project_naming() -> None:
    forbidden = (
        "referencefield/" + LEGACY_REPOSITORY_SLUG,
        "template_name=" + LEGACY_REPOSITORY_SLUG,
        LEGACY_PROJECT_NAME,
    )
    for path in text_files():
        text = read_text(path)
        for term in forbidden:
            if term in text:
                error(
                    f"legacy project/repository naming remains in {path.relative_to(ROOT)}"
                )
                break


def check_removed_or_ambiguous_product_wording() -> None:
    for path in text_files():
        text = read_text(path).lower()
        if any(term in text for term in REMOVED_END_SESSION_TERMS):
            error(
                f"removed end-of-session workflow wording remains in {path.relative_to(ROOT)}"
            )
        if any(term in text for term in AMBIGUOUS_SUPPORT_TERMS):
            error(
                f"ambiguous ChatGPT support-plan wording remains in {path.relative_to(ROOT)}"
            )


def check_manifest_path_confinement(manifest: dict) -> None:
    template_source = manifest.get("template_source", {}) or {}
    compatibility = manifest.get("compatibility", {}) or {}
    activation = manifest.get("activation", {}) or {}
    collaboration = manifest.get("collaboration", {}) or {}
    validation = manifest.get("validation", {}) or {}
    projects_cfg = manifest.get("projects", {}) or {}

    scalar_paths = (
        ("front_door", manifest.get("front_door")),
        ("template_source.manifest", template_source.get("manifest")),
        ("compatibility.codex_bootloader", compatibility.get("codex_bootloader")),
        ("activation.diagnostic_file", activation.get("diagnostic_file")),
        ("collaboration.companion", collaboration.get("companion")),
        ("validation.script", validation.get("script")),
        ("validation.workflow", validation.get("workflow")),
    )
    for key, value in scalar_paths:
        if value is not None:
            confined_path(str(value), f"PROTOCOL.yaml {key}")

    for key, value in (manifest.get("human_docs", {}) or {}).items():
        confined_path(str(value), f"PROTOCOL.yaml human_docs.{key}")

    for key, value in (manifest.get("global", {}) or {}).items():
        confined_path(str(value), f"PROTOCOL.yaml global.{key}")

    projects_root_rel = projects_cfg.get("root")
    template_rel = projects_cfg.get("template")
    if projects_root_rel is not None:
        confined_path(str(projects_root_rel), "PROTOCOL.yaml projects.root")
    template_root = None
    if template_rel is not None:
        template_root = confined_path(
            str(template_rel),
            "PROTOCOL.yaml projects.template",
        )

    if template_root is not None:
        project_front_door = projects_cfg.get("front_door")
        if project_front_door is not None:
            confined_path(
                str(project_front_door),
                "PROTOCOL.yaml projects.front_door",
                template_root,
            )
        for index, filename in enumerate(projects_cfg.get("required_files", []) or []):
            confined_path(
                str(filename),
                f"PROTOCOL.yaml projects.required_files[{index}]",
                template_root,
            )


def check_validation_workflow(manifest: dict) -> None:
    validation = manifest.get("validation", {}) or {}
    workflow_rel = str(validation.get("workflow", "")).strip()
    if not workflow_rel:
        error("PROTOCOL.yaml validation.workflow is missing")
        return

    workflow_path = require_file(workflow_rel, "validation workflow")
    if validation.get("runs_on_pull_request") is not True:
        error("PROTOCOL.yaml validation.runs_on_pull_request must be true")
    if validation.get("runs_on_main_push") is not True:
        error("PROTOCOL.yaml validation.runs_on_main_push must be true")
    if validation.get("manual_dispatch_available") is not True:
        error("PROTOCOL.yaml validation.manual_dispatch_available must be true")
    if not workflow_path.is_file():
        return

    workflow_text = read_text(workflow_path)
    on_match = re.search(
        r"(?ms)^on:\s*\n(?P<body>.*?)(?=^[^\s#])",
        workflow_text,
    )
    trigger_block = on_match.group("body") if on_match else ""
    if not on_match:
        error(f"{workflow_rel} is missing a readable top-level on: trigger block")

    if not re.search(r"(?m)^  pull_request:\s*$", trigger_block):
        error(f"{workflow_rel} must run on pull_request")
    if not re.search(r"(?m)^  workflow_dispatch:\s*$", trigger_block):
        error(f"{workflow_rel} must run on workflow_dispatch")

    push_match = re.search(
        r"(?ms)^  push:\s*\n(?P<body>(?: {4,}.*\n?)*)",
        trigger_block,
    )
    if not push_match:
        error(f"{workflow_rel} must run on push to canonical main")
    else:
        push_block = push_match.group("body")
        if not re.search(r"(?m)^    branches:\s*$", push_block):
            error(f"{workflow_rel} push trigger must declare branches")
        if not re.search(r"(?m)^      - main\s*$", push_block):
            error(f"{workflow_rel} push trigger must include canonical main")

    try:
        workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader) or {}
    except Exception as exc:  # noqa: BLE001
        error(f"{workflow_rel} cannot be parsed: {exc}")
        return
    if not isinstance(workflow, dict):
        error(f"{workflow_rel} root must be a mapping")
        return

    permissions = workflow.get("permissions")
    if not isinstance(permissions, dict) or permissions.get("contents") != "read":
        error(f"{workflow_rel} must declare top-level permissions.contents: read")

    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        error(f"{workflow_rel} must define at least one validation job")
        return

    feature_seen = {
        "checkout": False,
        "pinned_dependency": False,
        "regression_tests": False,
        "structural_validator": False,
    }
    complete_job = False

    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue

        has_checkout = False
        has_pinned_dependency = False
        has_regression_tests = False
        has_structural_validator = False

        for step in steps:
            if not isinstance(step, dict):
                continue
            uses = str(step.get("uses", ""))
            run = str(step.get("run", ""))

            if uses.startswith("actions/checkout@"):
                has_checkout = True
            if re.search(
                r"(?i)python\s+-m\s+pip\s+install[^\n]*PyYAML==6\.0\.2",
                run,
            ):
                has_pinned_dependency = True
            if re.search(
                r"(?m)^\s*python\s+tools/test_validate_protocol\.py(?:\s|$)",
                run,
            ):
                has_regression_tests = True
            if re.search(
                r"(?m)^\s*python\s+tools/validate_protocol\.py(?:\s|$)",
                run,
            ):
                has_structural_validator = True

        feature_seen["checkout"] |= has_checkout
        feature_seen["pinned_dependency"] |= has_pinned_dependency
        feature_seen["regression_tests"] |= has_regression_tests
        feature_seen["structural_validator"] |= has_structural_validator

        if (
            has_checkout
            and has_pinned_dependency
            and has_regression_tests
            and has_structural_validator
        ):
            complete_job = True

    if not feature_seen["checkout"]:
        error(f"{workflow_rel} validation job must check out the repository")
    if not feature_seen["pinned_dependency"]:
        error(f"{workflow_rel} validation job must install pinned PyYAML==6.0.2")
    if not feature_seen["regression_tests"]:
        error(f"{workflow_rel} validation job must run tools/test_validate_protocol.py")
    if not feature_seen["structural_validator"]:
        error(f"{workflow_rel} validation job must run tools/validate_protocol.py")
    if all(feature_seen.values()) and not complete_job:
        error(f"{workflow_rel} required validation work must occur in one job")

def check_documented_bootloader(manifest: dict) -> None:
    bootloader = str(manifest.get("custom_instruction_template", "")).strip()
    if not bootloader:
        error("PROTOCOL.yaml custom_instruction_template is missing")
        return

    setup_rel = str((manifest.get("human_docs", {}) or {}).get("setup", "SETUP.md"))
    setup_path = require_file(setup_rel, "setup documentation")
    if not setup_path.is_file():
        return

    setup_text = read_text(setup_path)
    match = re.search(
        r"<!-- BOOTLOADER-DOC-START -->\s*\n>\s*(?P<text>[^\n]+)\n<!-- BOOTLOADER-DOC-END -->",
        setup_text,
    )
    if not match:
        error(f"{setup_rel} is missing the marked canonical bootloader documentation block")
        return

    documented = match.group("text").strip()
    if documented != bootloader:
        error(
            f"{setup_rel} documented bootloader does not match "
            "PROTOCOL.yaml custom_instruction_template"
        )


def load_manifest() -> dict:
    manifest_path = require_file("PROTOCOL.yaml", "protocol manifest")
    if not manifest_path.is_file():
        return {}
    try:
        data = yaml.safe_load(read_text(manifest_path)) or {}
    except Exception as exc:  # noqa: BLE001
        error(f"PROTOCOL.yaml cannot be parsed: {exc}")
        return {}
    if not isinstance(data, dict):
        error("PROTOCOL.yaml root must be a mapping")
        return {}
    return data


def registry_slugs(registry_path: Path) -> set[str]:
    text = read_text(registry_path)
    return set(
        re.findall(
            r"^###\s+([a-z0-9][a-z0-9-]*)\s+[—–-]\s+",
            text,
            re.MULTILINE,
        )
    )


def project_dirs(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    projects: set[str] = set()
    for item in root.iterdir():
        if item.name == "_TEMPLATE" or item.name.startswith("."):
            continue
        resolved = item.resolve(strict=False)
        if not resolved.is_relative_to(ROOT_RESOLVED):
            error(f"project directory resolves outside repository: {item.relative_to(ROOT)}")
            continue
        if item.is_dir():
            projects.add(item.name)
    return projects


def main() -> int:
    manifest = load_manifest()
    if not manifest:
        print_results()
        return 1

    check_manifest_path_confinement(manifest)
    check_legacy_project_naming()
    check_removed_or_ambiguous_product_wording()
    check_validation_workflow(manifest)
    check_documented_bootloader(manifest)

    version = str(manifest.get("protocol_version", "")).strip()
    if not version:
        error("PROTOCOL.yaml missing protocol_version")

    status = str(manifest.get("protocol_status", "")).strip()
    release_lifecycle = manifest.get("release_lifecycle", {}) or {}
    required_statuses = {"development", "acceptance_candidate", "released"}
    allowed_statuses = set(release_lifecycle.get("allowed_protocol_statuses", []))

    if status not in required_statuses:
        error("PROTOCOL.yaml protocol_status must be development, acceptance_candidate, or released")
    if allowed_statuses != required_statuses:
        error("PROTOCOL.yaml release_lifecycle.allowed_protocol_statuses must declare development, acceptance_candidate, and released")

    lifecycle_expected = {
        "development_status": "development",
        "acceptance_candidate_status": "acceptance_candidate",
        "released_status": "released",
        "initial_acceptance_entry_requires_explicit_user_authorization": True,
        "corrective_reentry_reuses_active_acceptance_authorization": True,
        "development_allows_substantive_changes": True,
        "development_validation_is_advisory": True,
        "development_has_frozen_candidate": False,
        "acceptance_transition_commit_is_first_freeze_eligible_candidate": True,
        "candidate_mutation_invalidates_gate": True,
        "corrective_change_requires_development_status": True,
        "release_requires_acceptance_gate_pass": True,
    }
    for key, expected in lifecycle_expected.items():
        if release_lifecycle.get(key) != expected:
            error(f"PROTOCOL.yaml release_lifecycle.{key} must be {expected!r}")

    if status in {"development", "acceptance_candidate"} and version != "unreleased":
        error("pre-release protocol_status requires protocol_version unreleased")
    if status == "released" and version == "unreleased":
        error("released protocol_status requires a real protocol_version")

    if manifest.get("canonical_branch") != "main":
        warn("canonical_branch is not main; confirm this is intentional")

    front_door = str(manifest.get("front_door", "START_HERE.md"))
    require_file(front_door, "front door")

    template_source = manifest.get("template_source", {}) or {}
    template_repository_id = template_source.get("repository_id")
    if not isinstance(template_repository_id, int) or template_repository_id <= 0:
        error("PROTOCOL.yaml template_source.repository_id must be a positive GitHub repository ID")
    if not str(template_source.get("repository", "")).strip():
        error("PROTOCOL.yaml template_source.repository is missing")
    if template_source.get("role") != "public_update_source_only":
        error("PROTOCOL.yaml template_source.role must be public_update_source_only")
    if template_source.get("owner_name_runtime_resolved") is not True:
        error("PROTOCOL.yaml template_source.owner_name_runtime_resolved must be true")
    if template_source.get("repository_name_part_of_protocol") is not False:
        error("PROTOCOL.yaml template_source.repository_name_part_of_protocol must be false")

    working_repository = manifest.get("working_repository", {}) or {}
    if working_repository.get("identity") != "github_repository_id":
        error("PROTOCOL.yaml working_repository.identity must be github_repository_id")
    if working_repository.get("rename_requires_bootloader_refresh") is not False:
        error("PROTOCOL.yaml working_repository.rename_requires_bootloader_refresh must be false")
    if working_repository.get("unresolved_repository_id_fails_closed") is not True:
        error("PROTOCOL.yaml working_repository.unresolved_repository_id_fails_closed must be true")

    global_map = manifest.get("global", {}) or {}
    for key in ("current", "decisions", "knowledge", "working_style", "projects"):
        path = global_map.get(key)
        if not path:
            error(f"PROTOCOL.yaml global.{key} is missing")
        else:
            require_file(str(path), f"global.{key}")

    for key, path in (manifest.get("human_docs", {}) or {}).items():
        require_file(str(path), f"human_docs.{key}")

    compatibility = manifest.get("compatibility", {}) or {}
    compatibility_expected = {
        "minimum_supported_chatgpt_plan": "plus",
        "free_chatgpt_plan_supported": False,
        "go_chatgpt_plan_supported": False,
        "higher_paid_plans_supported_when_required_github_capability_available": True,
        "required_chatgpt_plugin": "GitHub",
        "plugin_invocation": "@GitHub",
        "plugin_must_be_installed_or_selected": True,
        "plugin_must_be_authenticated": True,
        "plugin_must_be_authorized_for_exact_repository": True,
        "plugin_requires_repository_read_write_actions": True,
        "plan_alone_does_not_guarantee_plugin_capability": True,
    }
    for key, expected in compatibility_expected.items():
        if compatibility.get(key) != expected:
            error(f"PROTOCOL.yaml compatibility.{key} must be {expected!r}")

    activation = manifest.get("activation", {}) or {}
    blocked_priority = list(activation.get("blocked_priority_order", []))
    expected_priority_prefix = [
        "supported_chatgpt_plan",
        "github_plugin_installation_authentication",
    ]
    if blocked_priority[:2] != expected_priority_prefix:
        error(
            "PROTOCOL.yaml activation.blocked_priority_order must begin with "
            "supported_chatgpt_plan then github_plugin_installation_authentication"
        )

    codex_bootloader = compatibility.get("codex_bootloader")
    if not codex_bootloader:
        error("PROTOCOL.yaml compatibility.codex_bootloader is missing")
    else:
        require_file(str(codex_bootloader), "Codex bootloader")

    projects_cfg = manifest.get("projects", {}) or {}
    projects_root_rel = str(projects_cfg.get("root", "projects"))
    template_rel = str(projects_cfg.get("template", "projects/_TEMPLATE"))
    required_project_files = list(projects_cfg.get("required_files", []))

    projects_root = require_directory(projects_root_rel, "projects root")
    template_root = require_directory(template_rel, "project template")

    for filename in required_project_files:
        require_file(
            str(filename),
            f"project template required file {filename}",
            template_root,
        )

    registry_path = require_file(
        str(global_map.get("projects", "PROJECTS.md")),
        "project registry",
    )
    registered = registry_slugs(registry_path) if registry_path.is_file() else set()
    actual_projects = project_dirs(projects_root)

    for slug in sorted(registered - actual_projects):
        error(f"registered project directory missing: projects/{slug}")
    for slug in sorted(actual_projects - registered):
        error(f"project directory is not registered in PROJECTS.md: projects/{slug}")

    for slug in sorted(actual_projects):
        project_root = confined_path(slug, f"project directory projects/{slug}", projects_root)
        if project_root is None:
            continue
        for filename in required_project_files:
            require_file(
                str(filename),
                f"projects/{slug} required file {filename}",
                project_root,
            )

    decision_path = confined_path(
        str(global_map.get("decisions", "DECISIONS.md")),
        "PROTOCOL.yaml global.decisions",
    )
    knowledge_path = confined_path(
        str(global_map.get("knowledge", "KNOWLEDGE.md")),
        "PROTOCOL.yaml global.knowledge",
    )
    decision_paths = [decision_path] if decision_path is not None else []
    knowledge_paths = [knowledge_path] if knowledge_path is not None else []
    for slug in sorted(actual_projects):
        project_root = confined_path(slug, f"project directory projects/{slug}", projects_root)
        if project_root is None:
            continue
        project_decisions = confined_path(
            "DECISIONS.md",
            f"projects/{slug} decisions",
            project_root,
        )
        project_knowledge = confined_path(
            "KNOWLEDGE.md",
            f"projects/{slug} knowledge",
            project_root,
        )
        if project_decisions is not None:
            decision_paths.append(project_decisions)
        if project_knowledge is not None:
            knowledge_paths.append(project_knowledge)

    for path in decision_paths:
        if path.is_file():
            check_unique_ids(path, "D")
            check_references(path, "D")
            check_lifecycle_consistency(path, "D")
    for path in knowledge_paths:
        if path.is_file():
            check_unique_ids(path, "K")
            check_references(path, "K")
            check_lifecycle_consistency(path, "K")

    style_path = confined_path(
        str(global_map.get("working_style", "WORKING_STYLE.md")),
        "PROTOCOL.yaml global.working_style",
    )
    if style_path is not None and style_path.is_file():
        check_unique_ids(style_path, "WS")
        check_references(style_path, "WS")
        check_lifecycle_consistency(style_path, "WS")

    budgets = manifest.get("soft_budgets", {}) or {}
    budget_bytes(front_door, int(budgets.get("START_HERE.md_bytes", 10000)), "START_HERE.md")
    budget_bytes(
        str(global_map.get("current", "CURRENT.md")),
        int(budgets.get("CURRENT.md_bytes", 7000)),
        "global CURRENT.md",
    )

    project_front_door_limit = int(budgets.get("PROJECT.md_bytes", 9000))
    project_current_limit = int(budgets.get("project_CURRENT.md_bytes", 7000))
    for slug in sorted(actual_projects):
        budget_bytes(
            f"{projects_root_rel}/{slug}/PROJECT.md",
            project_front_door_limit,
            f"projects/{slug}/PROJECT.md",
        )
        budget_bytes(
            f"{projects_root_rel}/{slug}/CURRENT.md",
            project_current_limit,
            f"projects/{slug}/CURRENT.md",
        )

    decision_limit = int(budgets.get("active_decisions_per_scope", 30))
    for path in decision_paths:
        if path.is_file() and active_count(path, "D") > decision_limit:
            warn(
                f"soft budget crossed: {path.relative_to(ROOT)} has more than "
                f"{decision_limit} active decisions"
            )

    knowledge_limit = int(budgets.get("active_knowledge_per_scope", 40))
    for path in knowledge_paths:
        if path.is_file() and active_count(path, "K") > knowledge_limit:
            warn(
                f"soft budget crossed: {path.relative_to(ROOT)} has more than "
                f"{knowledge_limit} active knowledge entries"
            )

    style_limit = int(budgets.get("active_working_style_entries", 20))
    if style_path.is_file() and active_count(style_path, "WS") > style_limit:
        warn(
            f"soft budget crossed: WORKING_STYLE.md has more than {style_limit} active entries"
        )

    diagnostic_file = str((manifest.get("activation", {}) or {}).get("diagnostic_file", "SETUP-TEST.md"))
    setup_test = confined_path(diagnostic_file, "PROTOCOL.yaml activation.diagnostic_file")
    if setup_test is not None and setup_test.exists():
        warn(f"{diagnostic_file} still exists; remove it after setup validation")

    print_results(version)
    return 1 if ERRORS else 0


def print_results(version: str = "unknown") -> None:
    print(f"Operational-memory structural validation · protocol {version}")
    for message in WARNINGS:
        print(f"WARNING: {message}")
    for message in ERRORS:
        print(f"ERROR: {message}")
    if ERRORS:
        print(f"RESULT: FAIL ({len(ERRORS)} error(s), {len(WARNINGS)} warning(s))")
    elif WARNINGS:
        print(f"RESULT: PASS WITH WATCH SIGNALS ({len(WARNINGS)} warning(s))")
    else:
        print("RESULT: PASS")


if __name__ == "__main__":
    raise SystemExit(main())