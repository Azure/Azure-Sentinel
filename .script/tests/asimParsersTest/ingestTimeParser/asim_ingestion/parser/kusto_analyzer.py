"""Trusted bridge to the Microsoft Kusto.Language parser."""

from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Any


ANALYZER_RESULT_VERSION = 3
_BUILD_LOCK = threading.Lock()
_PROJECT_DIRECTORY = Path(__file__).resolve().parents[2] / "kusto_analyzer"
_PROJECT_PATH = _PROJECT_DIRECTORY / "kusto_analyzer.csproj"
_DEFAULT_DLL_PATH = (
    _PROJECT_DIRECTORY
    / "bin"
    / "Release"
    / "net8.0"
    / "AsimKustoAnalyzer.dll"
)


class KustoAnalyzerError(RuntimeError):
    """Raised when the trusted Kusto analyzer cannot produce a result."""


def _dotnet_path() -> str:
    executable = shutil.which("dotnet")
    if executable is None:
        raise KustoAnalyzerError(
            "The dotnet executable is required for static KQL validation."
        )
    return executable


def _analyzer_dll_path() -> Path:
    configured = os.getenv("ASIM_KUSTO_ANALYZER_DLL")
    return (
        Path(configured).expanduser().resolve()
        if configured
        else _DEFAULT_DLL_PATH
    )


def _run_build_command(arguments: list[str], stage: str) -> None:
    try:
        process = subprocess.run(
            arguments,
            cwd=_PROJECT_DIRECTORY,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise KustoAnalyzerError(
            f"Kusto analyzer {stage} timed out."
        ) from exc
    except OSError as exc:
        raise KustoAnalyzerError(
            f"Kusto analyzer {stage} could not start: {exc}"
        ) from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()
        raise KustoAnalyzerError(
            f"Kusto analyzer {stage} failed: {detail[:2000]}"
        )


def ensure_kusto_analyzer() -> Path:
    """Build the pinned helper once when a prebuilt DLL is unavailable."""
    dll_path = _analyzer_dll_path()
    if dll_path.is_file():
        return dll_path
    if os.getenv("ASIM_KUSTO_ANALYZER_DLL"):
        raise KustoAnalyzerError(
            f"Configured Kusto analyzer DLL does not exist: {dll_path}"
        )

    with _BUILD_LOCK:
        if dll_path.is_file():
            return dll_path
        dotnet = _dotnet_path()
        _run_build_command(
            [
                dotnet,
                "restore",
                str(_PROJECT_PATH),
                "--locked-mode",
                "--nologo",
            ],
            "restore",
        )
        _run_build_command(
            [
                dotnet,
                "build",
                str(_PROJECT_PATH),
                "--configuration",
                "Release",
                "--no-restore",
                "--nologo",
                "--verbosity",
                "quiet",
            ],
            "build",
        )
    if not dll_path.is_file():
        raise KustoAnalyzerError(
            f"Kusto analyzer build produced no DLL at {dll_path}."
        )
    return dll_path


def _validate_location(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and all(
            isinstance(value.get(key), int)
            for key in ("start", "length", "line", "column")
        )
        and all(
            isinstance(value.get(key), str)
            for key in ("text", "normalizedText")
        )
    )


def _validate_syntax_fact(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("type"), str)
        and isinstance(value.get("kind"), str)
        and (
            value.get("name") is None
            or isinstance(value.get("name"), str)
        )
        and (
            value.get("ownerOperator") is None
            or isinstance(value.get("ownerOperator"), str)
        )
        and _validate_location(value.get("location"))
    )


def _validate_assignment_fact(value: Any) -> bool:
    is_string_literal = (
        value.get("isStringLiteral")
        if isinstance(value, dict)
        else None
    )
    string_value = value.get("stringValue") if isinstance(value, dict) else None
    return (
        isinstance(value, dict)
        and all(
            isinstance(value.get(key), str)
            for key in ("name", "expressionType", "expressionKind")
        )
        and isinstance(is_string_literal, bool)
        and (
            isinstance(string_value, str)
            if is_string_literal
            else string_value is None
        )
        and (
            value.get("ownerOperator") is None
            or isinstance(value.get("ownerOperator"), str)
        )
        and _validate_location(value.get("location"))
    )


def _validate_source_reference(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("name"), str)
        and isinstance(value.get("context"), str)
        and _validate_location(value.get("location"))
    )


def _validate_source_pipeline(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    is_valid = value.get("isValid")
    failure = value.get("failure")
    source_location = value.get("sourceLocation")
    if (
        not isinstance(is_valid, bool)
        or not isinstance(value.get("statementCount"), int)
        or any(
            value.get(key) is not None
            and not isinstance(value.get(key), str)
            for key in (
                "failure",
                "statementType",
                "rootType",
                "rootText",
            )
        )
    ):
        return False
    if is_valid:
        return (
            failure is None
            and value.get("statementCount") == 1
            and value.get("statementType") == "ExpressionStatement"
            and value.get("rootType") == "NameReference"
            and value.get("rootText") == "source"
            and _validate_location(source_location)
        )
    return isinstance(failure, str) and source_location is None


def _validate_result_contract(result: Any) -> dict[str, Any]:
    if (
        not isinstance(result, dict)
        or result.get("version") != ANALYZER_RESULT_VERSION
    ):
        raise KustoAnalyzerError(
            "Kusto analyzer returned an unsupported result contract."
        )
    diagnostics = result.get("diagnostics")
    statements = result.get("statements")
    if (
        not isinstance(diagnostics, list)
        or not all(
            isinstance(item, dict)
            and all(
                isinstance(item.get(key), str)
                for key in ("code", "severity", "message")
            )
            and all(
                isinstance(item.get(key), int)
                for key in ("start", "length", "line", "column")
            )
            for item in diagnostics
        )
        or not isinstance(statements, list)
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("type"), str)
            and isinstance(item.get("hasPipe"), bool)
            and (
                item.get("name") is None
                or isinstance(item.get("name"), str)
            )
            and (
                item.get("expressionRootType") is None
                or isinstance(item.get("expressionRootType"), str)
            )
            and (
                item.get("expressionRootText") is None
                or isinstance(item.get("expressionRootText"), str)
            )
            and _validate_location(item.get("location"))
            for item in statements
        )
    ):
        raise KustoAnalyzerError(
            "Kusto analyzer returned an invalid result contract."
        )
    for key in ("operators", "functions", "constructs"):
        facts = result.get(key)
        if (
            not isinstance(facts, list)
            or not all(_validate_syntax_fact(item) for item in facts)
        ):
            raise KustoAnalyzerError(
                "Kusto analyzer returned an invalid result contract."
            )
    assignments = result.get("assignments")
    source_references = result.get("sourceReferences")
    source_pipeline = result.get("sourcePipeline")
    if (
        not isinstance(assignments, list)
        or not all(
            _validate_assignment_fact(item)
            for item in assignments
        )
        or not isinstance(source_references, list)
        or not all(
            _validate_source_reference(item)
            for item in source_references
        )
        or not _validate_source_pipeline(source_pipeline)
    ):
        raise KustoAnalyzerError(
            "Kusto analyzer returned an invalid result contract."
        )
    pipeline = result.get("pipeline")
    if pipeline is not None and (
        not isinstance(pipeline, dict)
        or (
            pipeline.get("rootType") is not None
            and not isinstance(pipeline.get("rootType"), str)
        )
        or (
            pipeline.get("rootKind") is not None
            and not isinstance(pipeline.get("rootKind"), str)
        )
        or (
            pipeline.get("rootText") is not None
            and not isinstance(pipeline.get("rootText"), str)
        )
        or not isinstance(pipeline.get("operators"), list)
        or not all(
            _validate_syntax_fact(item)
            for item in pipeline["operators"]
        )
    ):
        raise KustoAnalyzerError(
            "Kusto analyzer returned an invalid result contract."
        )
    return result


@lru_cache(maxsize=256)
def analyze_kql(query: str) -> dict[str, Any]:
    """Parse one query and return syntax diagnostics and AST facts."""
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    dll_path = ensure_kusto_analyzer()
    try:
        process = subprocess.run(
            [_dotnet_path(), str(dll_path)],
            input=json.dumps({"query": query}, separators=(",", ":")),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise KustoAnalyzerError(
            "Kusto analyzer execution timed out."
        ) from exc
    except OSError as exc:
        raise KustoAnalyzerError(
            f"Kusto analyzer execution could not start: {exc}"
        ) from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()
        raise KustoAnalyzerError(
            f"Kusto analyzer execution failed: {detail[:2000]}"
        )
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise KustoAnalyzerError(
            "Kusto analyzer returned invalid JSON."
        ) from exc
    return _validate_result_contract(result)
