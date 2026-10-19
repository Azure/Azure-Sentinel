"""Live lab deployment, runtime query validation, DCR readiness, and alert parity qualification."""
from __future__ import annotations

from typing import Any

__all__ = [
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
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from solution_manager.qualification import orchestrator

        return getattr(orchestrator, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


