from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[3]

SCAN_ROOTS = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "package.json",
    REPO_ROOT / "package-lock.json",
    REPO_ROOT / ".claude",
    REPO_ROOT / ".cursor",
    REPO_ROOT / ".windsurf",
    REPO_ROOT / ".github" / "agents",
    REPO_ROOT / ".github" / "skills",
    REPO_ROOT / ".script" / "local-validation",
    REPO_ROOT / "Tools" / "AzureMonitorLogsIngestion",
    REPO_ROOT / "Tools" / "Create-Azure-Sentinel-Solution",
    REPO_ROOT / "Tools" / "SentinelToXDRMigration",
    REPO_ROOT / "Tools" / "SolutionMigration",
]

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "ignored",
    ".venv",
    "venv",
    "Logs",
}

FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("personal handle or path (oferinbar/wiking/kingwil)", re.compile(r"\b(?:oferinbar|wiking|kingwil)\b", re.IGNORECASE)),
    ("Copilot session-state path", re.compile(r"\.copilot[\\/]+session-state", re.IGNORECASE)),
    ("internal ADO npm registry URL", re.compile(r"pkgs\.visualstudio\.com", re.IGNORECASE)),
    (
        "lab/environment GUID or workspace name",
        re.compile(
            r"\b(?:39768270-33ce-4b90-a1a6-e0caeb3ba0ab|42382e39-f157-46d1-a931-b8cfd779ece5|756386d8-e2d4-4f09-905a-74b24313721f|956386d8-e2d4-4f09-905a-74b24313721f|0e8e91c3-dec0-4634-a473-1254c3bce737|525a15fc-6f89-424c-bb5f-17a652e5c15d|OptimizeSentinelWorkspace|DefaultResourceGroup-EUS)\b",
            re.IGNORECASE,
        ),
    ),
]


def _iter_text_files() -> list[Path]:
    files: list[Path] = []
    this_file = Path(__file__).resolve()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for item in root.rglob("*"):
            if any(part in SKIP_DIR_NAMES for part in item.parts):
                continue
            if not item.is_file() or item.resolve() == this_file:
                continue
            files.append(item)
    return sorted(files)


def test_no_personal_or_lab_residue_in_toolkit_files() -> None:
    violations: list[str] = []
    for file_path in _iter_text_files():
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = file_path.relative_to(REPO_ROOT).as_posix()
        for label, pattern in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                violations.append(f"{rel}:{line_no}: {label} ({match.group(0)!r})")
    assert not violations, "Release hygiene violations detected:\n" + "\n".join(violations[:50])


def test_local_validator_does_not_interpolate_variables_in_exec_sync() -> None:
    for rel in (".script/local-validation/validate.ts", ".script/local-validation/validate.js"):
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        interpolated_exec_sync = re.findall(r"execSync\(\s*`[^`]*\$\{[^`]*`", text)
        assert not interpolated_exec_sync, (
            f"{rel} uses interpolated template strings in execSync (use execFileSync with argv arrays instead): "
            f"{interpolated_exec_sync}"
        )
