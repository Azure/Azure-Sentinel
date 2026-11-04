"""Migration and qualification evidence projection, HTML dashboards, and reviewer exports."""
from __future__ import annotations

from typing import Any

_LAZY_EXPORTS = (
    "ALLOWED_DECISION_SCOPES",
    "DECISION_MANIFEST_SCHEMA_VERSION",
    "DEFAULT_DECISION_MANIFEST_FILENAME",
    "build_sanitized_decision_manifest",
    "sanitize_decision_text",
    "verify_sanitized_decision_manifest",
    "write_sanitized_decision_manifest",
)


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        from solution_manager.reporting import decision_manifest

        return getattr(decision_manifest, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals().keys(), *_LAZY_EXPORTS})





