"""Backwards-compatibility shim for `solution_manager`.

All implementation modules live under `Tools/SentinelToXDRMigration/solution_manager/`
organized by Solution Manager capability (`core/`, `authoring/`, `migration/`,
`qualification/`, `packaging/`, `reporting/`, `research/`).
"""
from __future__ import annotations

from types import ModuleType

import solution_manager
from solution_manager import (
    MODULE_TO_SUBPACKAGE,
    SUBPACKAGE_MODULES,
    __version__,
    resolve_module_attribute,
)

__all__ = [
    "__version__",
    "SUBPACKAGE_MODULES",
    "MODULE_TO_SUBPACKAGE",
    *SUBPACKAGE_MODULES.keys(),
    *MODULE_TO_SUBPACKAGE.keys(),
    "cli",
]


def __getattr__(name: str) -> ModuleType:
    return resolve_module_attribute(name)

