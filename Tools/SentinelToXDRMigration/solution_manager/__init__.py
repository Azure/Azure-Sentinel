"""Solution Manager for Microsoft Sentinel and Defender XDR content lifecycle."""
from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

__version__ = "0.1.0"

SUBPACKAGE_MODULES: dict[str, tuple[str, ...]] = {
    "core": (
        "artifacts",
        "budget",
        "content_paths",
        "coordinator",
        "onboarding",
        "preflight",
        "review_notifications",
        "target_config",
        "target_context",
        "workflow",
        "workflow_reminders",
    ),
    "authoring": (
        "authoring_contract",
        "columns",
        "dependencies",
        "native_workbooks",
        "workbook_dependencies",
        "workbook_functions",
        "workbook_publication",
        "workbook_updates",
        "workbook_validation",
    ),
    "migration": (
        "catalog",
        "converter",
        "mapping_evidence",
        "parser_bindings",
        "source_runtime_waiver",
        "workbook_workflow",
        "workbooks",
    ),
    "qualification": (
        "alert_parity",
        "analytic_deployment",
        "arm_acceptance",
        "arm_acceptance_support",
        "dcr_readiness",
        "delegated_app_registration",
        "deployment",
        "deployment_planning",
        "graph_auth",
        "graph_client_config",
        "graph_readiness",
        "logs_query",
        "mock_data",
        "orchestrator",
        "parity",
        "readiness_support",
        "runtime",
        "runtime_consent",
        "workbook_browser",
        "workbook_playwright",
        "workbook_preflight",
        "workbook_preflight_workflow",
        "workbook_qualification",
        "workbook_qualification_cli",
    ),
    "packaging": (
        "packaging",
        "packaging_selection",
        "release_notes",
    ),
    "reporting": (
        "decision_manifest",
        "evidence",
        "report",
        "report_dashboard",
        "report_review",
        "review_workflow",
        "runtime_report_references",
        "solution_report",
    ),
    "research": (),
}

MODULE_TO_SUBPACKAGE: dict[str, str] = {
    mod: subpkg
    for subpkg, modules in SUBPACKAGE_MODULES.items()
    for mod in modules
}

_PACKAGE_ROOT = Path(__file__).resolve().parent


def _canonical_and_aliases(fullname: str) -> tuple[str, list[str], str | None, Path, bool] | None:
    parts = fullname.split(".")
    if len(parts) < 2 or parts[0] not in ("solution_manager", "sentinel_xdr_migration"):
        return None

    # Top-level cli.py
    if parts[1:] == ["cli"]:
        canonical = "solution_manager.cli"
        aliases = ["solution_manager.cli", "sentinel_xdr_migration.cli"]
        return canonical, aliases, "cli", _PACKAGE_ROOT / "cli.py", False

    # Special case: "packaging" is both a subpackage directory and the module packaging.py.
    # Treating `solution_manager.packaging` as a package backed by `packaging/packaging.py`
    # (with `__path__` pointing to `packaging/`) satisfies both `from sentinel_xdr_migration.packaging import ...`
    # and `from solution_manager.packaging.packaging_selection import ...` with a single module instance.
    if parts[1:] in (["packaging"], ["packaging", "packaging"]):
        canonical = "solution_manager.packaging"
        aliases = [
            "solution_manager.packaging",
            "solution_manager.packaging.packaging",
            "sentinel_xdr_migration.packaging",
            "sentinel_xdr_migration.packaging.packaging",
        ]
        return canonical, aliases, "packaging", _PACKAGE_ROOT / "packaging" / "packaging.py", True

    # Subpackage itself (e.g. solution_manager.core or sentinel_xdr_migration.core)
    if len(parts) == 2 and parts[1] in SUBPACKAGE_MODULES:
        subpkg = parts[1]
        canonical = f"solution_manager.{subpkg}"
        aliases = [f"solution_manager.{subpkg}", f"sentinel_xdr_migration.{subpkg}"]
        return canonical, aliases, subpkg, _PACKAGE_ROOT / subpkg / "__init__.py", True

    # Flat module alias (e.g. sentinel_xdr_migration.workflow or solution_manager.workflow)
    if len(parts) == 2 and parts[1] in MODULE_TO_SUBPACKAGE:
        mod = parts[1]
        subpkg = MODULE_TO_SUBPACKAGE[mod]
        canonical = f"solution_manager.{subpkg}.{mod}"
        aliases = [
            canonical,
            f"solution_manager.{mod}",
            f"sentinel_xdr_migration.{subpkg}.{mod}",
            f"sentinel_xdr_migration.{mod}",
        ]
        return canonical, aliases, mod, _PACKAGE_ROOT / subpkg / f"{mod}.py", False

    # Nested subpackage module (e.g. solution_manager.core.workflow or sentinel_xdr_migration.core.workflow)
    if len(parts) == 3 and parts[1] in SUBPACKAGE_MODULES and parts[2] in SUBPACKAGE_MODULES[parts[1]]:
        subpkg, mod = parts[1], parts[2]
        canonical = f"solution_manager.{subpkg}.{mod}"
        aliases = [
            canonical,
            f"solution_manager.{mod}",
            f"sentinel_xdr_migration.{subpkg}.{mod}",
            f"sentinel_xdr_migration.{mod}",
        ]
        return canonical, aliases, mod, _PACKAGE_ROOT / subpkg / f"{mod}.py", False

    # _workbook_core package and submodules
    wb_tail: list[str] | None = None
    if parts[1] == "_workbook_core":
        wb_tail = parts[2:]
    elif len(parts) >= 3 and parts[1] == "migration" and parts[2] == "_workbook_core":
        wb_tail = parts[3:]
    if wb_tail is not None:
        wb_root = _PACKAGE_ROOT / "migration" / "_workbook_core"
        if not wb_tail:
            canonical = "solution_manager.migration._workbook_core"
            aliases = [
                canonical,
                "solution_manager._workbook_core",
                "sentinel_xdr_migration.migration._workbook_core",
                "sentinel_xdr_migration._workbook_core",
            ]
            return canonical, aliases, "_workbook_core", wb_root / "__init__.py", True
        if len(wb_tail) == 1:
            submod = wb_tail[0]
            sub_file = wb_root / f"{submod}.py"
            if sub_file.is_file():
                canonical = f"solution_manager.migration._workbook_core.{submod}"
                aliases = [
                    canonical,
                    f"solution_manager._workbook_core.{submod}",
                    f"sentinel_xdr_migration.migration._workbook_core.{submod}",
                    f"sentinel_xdr_migration._workbook_core.{submod}",
                ]
                return canonical, aliases, None, sub_file, False

    return None


def _bind_aliases(module: ModuleType, aliases: list[str], attr_name: str | None) -> None:
    for alias in aliases:
        sys.modules[alias] = module
    if attr_name:
        for root_name in ("solution_manager", "sentinel_xdr_migration"):
            root_mod = sys.modules.get(root_name)
            if root_mod is not None:
                setattr(root_mod, attr_name, module)
        if attr_name in MODULE_TO_SUBPACKAGE:
            subpkg = MODULE_TO_SUBPACKAGE[attr_name]
            for prefix in ("solution_manager", "sentinel_xdr_migration"):
                subpkg_mod = sys.modules.get(f"{prefix}.{subpkg}")
                if subpkg_mod is not None:
                    setattr(subpkg_mod, attr_name, module)


class _CanonicalLoader(importlib.abc.ExecutionLoader):
    def __init__(self, canonical: str, aliases: list[str], attr_name: str | None, origin: Path, is_pkg: bool) -> None:
        self._canonical = canonical
        self._aliases = aliases
        self._attr_name = attr_name
        self._origin = origin
        self._is_pkg = is_pkg
        self._source_loader = importlib.machinery.SourceFileLoader(canonical, str(origin))

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType | None:
        existing = sys.modules.get(self._canonical)
        if existing is not None:
            _bind_aliases(existing, self._aliases, self._attr_name)
            return existing
        return None

    def exec_module(self, module: ModuleType) -> None:
        if getattr(module, "_solution_manager_initialized", False):
            _bind_aliases(module, self._aliases, self._attr_name)
            return
        if self._is_pkg:
            module.__path__ = [str(self._origin.parent)]
        _bind_aliases(module, self._aliases, self._attr_name)
        try:
            self._source_loader.exec_module(module)
        except Exception:
            for alias in self._aliases:
                if sys.modules.get(alias) is module:
                    sys.modules.pop(alias, None)
            raise
        setattr(module, "_solution_manager_initialized", True)
        _bind_aliases(module, self._aliases, self._attr_name)

    def is_package(self, fullname: str) -> bool:
        return self._is_pkg

    def get_filename(self, fullname: str) -> str:
        return str(self._origin)

    def get_source(self, fullname: str) -> str | None:
        return self._source_loader.get_source(self._canonical)

    def get_code(self, fullname: str):
        return self._source_loader.get_code(self._canonical)

    def get_resource_reader(self, fullname: str):
        return self._source_loader.get_resource_reader(self._canonical)


class _AliasLoader(importlib.abc.ExecutionLoader):
    def __init__(self, canonical: str, aliases: list[str], attr_name: str | None, origin: Path, is_pkg: bool) -> None:
        self._canonical = canonical
        self._aliases = aliases
        self._attr_name = attr_name
        self._origin = origin
        self._is_pkg = is_pkg
        self._source_loader = importlib.machinery.SourceFileLoader(canonical, str(origin))

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        if self._canonical not in sys.modules and "." in self._canonical:
            parent_name = self._canonical.rsplit(".", 1)[0]
            if parent_name not in sys.modules:
                importlib.import_module(parent_name)
        mod = importlib.import_module(self._canonical)
        _bind_aliases(mod, self._aliases, self._attr_name)
        return mod

    def exec_module(self, module: ModuleType) -> None:
        _bind_aliases(module, self._aliases, self._attr_name)

    def is_package(self, fullname: str) -> bool:
        return self._is_pkg

    def get_filename(self, fullname: str) -> str:
        return str(self._origin)

    def get_source(self, fullname: str) -> str | None:
        return self._source_loader.get_source(self._canonical)

    def get_code(self, fullname: str):
        return self._source_loader.get_code(self._canonical)

    def get_resource_reader(self, fullname: str):
        return self._source_loader.get_resource_reader(self._canonical)


class _SolutionManagerFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: object = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        resolved = _canonical_and_aliases(fullname)
        if resolved is None:
            return None
        canonical, aliases, attr_name, origin, is_pkg = resolved
        if fullname == canonical:
            loader: importlib.abc.Loader = _CanonicalLoader(canonical, aliases, attr_name, origin, is_pkg)
        else:
            loader = _AliasLoader(canonical, aliases, attr_name, origin, is_pkg)
        spec = importlib.util.spec_from_file_location(
            fullname,
            origin,
            loader=loader,
            submodule_search_locations=[str(origin.parent)] if is_pkg else None,
        )
        return spec


def _install_finder() -> None:
    if not any(isinstance(f, _SolutionManagerFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _SolutionManagerFinder())


_install_finder()


def resolve_module_attribute(name: str) -> ModuleType:
    if name == "cli":
        return importlib.import_module("solution_manager.cli")
    if name in SUBPACKAGE_MODULES:
        return importlib.import_module(f"solution_manager.{name}")
    if name in MODULE_TO_SUBPACKAGE:
        subpkg = MODULE_TO_SUBPACKAGE[name]
        return importlib.import_module(f"solution_manager.{subpkg}.{name}")
    if name == "_workbook_core":
        return importlib.import_module("solution_manager.migration._workbook_core")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __getattr__(name: str) -> ModuleType:
    return resolve_module_attribute(name)
