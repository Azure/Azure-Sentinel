"""Live lab deployment, runtime query validation, DCR readiness, and alert parity qualification."""
from __future__ import annotations

from typing import Any

_LAZY_EXPORTS = (
    "DEFAULT_LAB_TARGET",
    "PIPELINE_STATE_FILENAME",
    "PREFLIGHT_PACKET_FILENAME",
    "QUALIFICATION_STAGES",
    "QualificationOrchestrator",
    "assess_qualification_readiness",
    "audit_private_config_and_support_export",
    "evaluate_qualification_promotion_gate",
    "generate_mock_data",
    "plan_qualification_pipeline",
    "run_qualification_pipeline",
)


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        from solution_manager.qualification import orchestrator

        return getattr(orchestrator, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals().keys(), *_LAZY_EXPORTS})






