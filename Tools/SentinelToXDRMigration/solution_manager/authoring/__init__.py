"""Offline content authoring, schema validation, and dependency contracts for detections and workbooks."""
from __future__ import annotations

from solution_manager.authoring.validator import (
    validate_kql_query_static,
    validate_xdr_artifacts_kql,
    validate_xdr_detection_kql,
    validate_xdr_workbook_kql,
)

__all__ = [
    "validate_kql_query_static",
    "validate_xdr_artifacts_kql",
    "validate_xdr_detection_kql",
    "validate_xdr_workbook_kql",
]

