from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

STATE_FILE_NAME = "workflow-state.json"
SCHEMA_VERSION = "1.1.0"
WORKFLOW_PROFILES = ("authoring", "qualification")
STAGES = (
    "discovery",
    "conversion",
    "validation",
    "packaging",
    "deployment",
    "mockIngestion",
    "alertParity",
    "report",
)
QUALIFICATION_DEPENDENCIES = {
    "discovery": (),
    "conversion": ("discovery",),
    "validation": ("conversion",),
    "packaging": ("validation",),
    "deployment": ("packaging",),
    "mockIngestion": ("deployment",),
    "alertParity": ("mockIngestion",),
    "report": ("alertParity",),
}
AUTHORING_DEPENDENCIES = {
    "discovery": (),
    "conversion": ("discovery",),
    "validation": ("conversion",),
    "packaging": ("validation",),
    "report": ("packaging",),
}
AUTHORING_OPTIONAL_STAGES = {"deployment", "mockIngestion", "alertParity"}
TERMINAL_STATUSES = {"passed", "failed", "blocked"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _paths(solution: str | Path) -> tuple[Path, Path]:
    root = Path(solution).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")
    output = root / "XDR Detections"
    return root, output / STATE_FILE_NAME


def _schema() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "schema" / "workflow-state.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(state: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(_schema()).iter_errors(state),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid workflow state: {details}")


def _write(path: Path, state: dict[str, Any]) -> None:
    state["updatedAt"] = _utc_now()
    _validate(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load(solution: str | Path) -> tuple[Path, dict[str, Any]]:
    _, path = _paths(solution)
    if not path.is_file():
        raise ValueError(
            f"workflow state does not exist: {path}; run workflow-init first"
        )
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(state, dict):
        raise ValueError(f"workflow state must be a JSON object: {path}")
    _validate(state)
    return path, state


def _stage_result(name: str, *, required: bool = True) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pending" if required else "notRequired",
        "attempts": 0,
        "startedAt": None,
        "completedAt": None,
        "message": None if required else "not required for the authoring workflow",
        "artifacts": {},
        "evidence": [],
    }


def initialize_workflow(
    solution: str | Path,
    *,
    workspace_resource_id: str | None = None,
    version_bump: str | None = None,
    workflow_profile: str = "authoring",
) -> dict[str, Any]:
    root, path = _paths(solution)
    if version_bump not in (None, "none", "patch", "minor", "major"):
        raise ValueError("version bump must be none, patch, minor, or major")
    if workflow_profile not in WORKFLOW_PROFILES:
        raise ValueError("workflow profile must be authoring or qualification")
    requested_context = {
        "workspaceResourceId": workspace_resource_id,
        "versionBump": version_bump,
        "workflowProfile": workflow_profile,
    }
    if path.exists():
        _, state = _load(root)
        context = state["context"]
        for key, value in requested_context.items():
            if value is not None and context.get(key) not in (None, value):
                raise ValueError(
                    f"workflow already uses {key}={context.get(key)!r}, "
                    f"not {value!r}"
                )
            if value is not None and context.get(key) is None:
                context[key] = value
        _write(path, state)
        return {
            **state,
            "statePath": str(path),
            "resumed": True,
            "next": _next_stage_name(state),
        }

    now = _utc_now()
    state = {
        "schemaVersion": SCHEMA_VERSION,
        "solution": str(root),
        "workflowStatus": "inProgress",
        "createdAt": now,
        "updatedAt": now,
        "context": requested_context,
        "stages": {
            name: _stage_result(
                name,
                required=not (
                    workflow_profile == "authoring"
                    and name in AUTHORING_OPTIONAL_STAGES
                ),
            )
            for name in STAGES
        },
    }
    _write(path, state)
    return {
        **state,
        "statePath": str(path),
        "resumed": False,
        "next": _next_stage_name(state),
    }


def workflow_status(solution: str | Path) -> dict[str, Any]:
    path, state = _load(solution)
    return {**state, "statePath": str(path), "next": _next_stage_name(state)}


def _dependencies(state: dict[str, Any], stage: str) -> tuple[str, ...]:
    if state["context"]["workflowProfile"] == "authoring":
        return AUTHORING_DEPENDENCIES.get(stage, ())
    return QUALIFICATION_DEPENDENCIES[stage]


def _next_stage_name(state: dict[str, Any]) -> str | None:
    running = [
        name for name in STAGES if state["stages"][name]["status"] == "running"
    ]
    if running:
        return running[0]
    for name in STAGES:
        stage = state["stages"][name]
        if stage["status"] in {"passed", "notRequired"}:
            continue
        if all(
            state["stages"][dependency]["status"] == "passed"
            for dependency in _dependencies(state, name)
        ):
            return name
    return None


def next_workflow_stage(solution: str | Path) -> dict[str, Any]:
    path, state = _load(solution)
    name = _next_stage_name(state)
    blocked_by = []
    if name is None and state["workflowStatus"] != "completed":
        for candidate in STAGES:
            if state["stages"][candidate]["status"] in {"passed", "notRequired"}:
                continue
            blocked_by.extend(
                dependency
                for dependency in _dependencies(state, candidate)
                if state["stages"][dependency]["status"] != "passed"
            )
            if blocked_by:
                break
    return {
        "solution": state["solution"],
        "statePath": str(path),
        "workflowStatus": state["workflowStatus"],
        "next": name,
        "blockedBy": blocked_by,
    }


def start_workflow_stage(solution: str | Path, stage: str) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"unknown workflow stage: {stage}")
    path, state = _load(solution)
    current = state["stages"][stage]
    if current["status"] == "notRequired":
        raise ValueError(
            f"workflow stage is not required for "
            f"{state['context']['workflowProfile']} profile: {stage}"
        )
    if current["status"] == "passed":
        raise ValueError(f"workflow stage already passed: {stage}")
    if current["status"] == "running":
        return {**current, "statePath": str(path), "resumed": True}

    blocked_by = [
        dependency
        for dependency in _dependencies(state, stage)
        if state["stages"][dependency]["status"] != "passed"
    ]
    if blocked_by:
        raise ValueError(
            f"workflow stage {stage} is blocked by: {', '.join(blocked_by)}"
        )

    current.update(
        {
            "status": "running",
            "attempts": current["attempts"] + 1,
            "startedAt": _utc_now(),
            "completedAt": None,
            "message": None,
            "artifacts": {},
            "evidence": [],
        }
    )
    state["workflowStatus"] = "inProgress"
    _write(path, state)
    return {**current, "statePath": str(path), "resumed": False}


def complete_workflow_stage(
    solution: str | Path,
    stage: str,
    *,
    status: str,
    message: str | None = None,
    artifacts: dict[str, str] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"unknown workflow stage: {stage}")
    if status not in TERMINAL_STATUSES:
        raise ValueError("stage status must be passed, failed, or blocked")
    if status in {"failed", "blocked"} and not str(message or "").strip():
        raise ValueError(f"{status} workflow stages require a message")

    path, state = _load(solution)
    current = state["stages"][stage]
    if current["status"] != "running":
        raise ValueError(f"workflow stage is not running: {stage}")
    current.update(
        {
            "status": status,
            "completedAt": _utc_now(),
            "message": message,
            "artifacts": artifacts or {},
            "evidence": evidence or [],
        }
    )
    if status == "failed":
        state["workflowStatus"] = "failed"
    elif status == "blocked":
        state["workflowStatus"] = "blocked"
    elif stage == "report":
        state["workflowStatus"] = "completed"
    else:
        state["workflowStatus"] = "inProgress"
    _write(path, state)
    return {
        **current,
        "statePath": str(path),
        "workflowStatus": state["workflowStatus"],
        "next": _next_stage_name(state),
    }
