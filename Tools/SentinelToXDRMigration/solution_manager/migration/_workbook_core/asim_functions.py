"""Deterministic rewrite of Sentinel ASIM unifying-parser function calls
(`_Im_<Schema>(...)`) into their AH-native `ASim<Schema>Logs` table equivalent.

Why this exists: `_Im_WebSession`, `_Im_NetworkSession`, `_Im_Dns`, etc. are
Sentinel workspace-scoped saved-query functions (union + normalize several
vendor parsers under one ASIM schema, with convenience named parameters like
`starttime=`, `url_has_any=`). Advanced Hunting has no workspace-function
namespace, so any call to one of these fails at runtime with something like
"Operator source expression should be table or column" - AH can't resolve the
identifier, and doesn't support the named-parameter call syntax at all.

The fix: the unified SecOps AH surface ships the equivalent data pre-normalized
directly in a native `ASim<Schema>Logs` table (confirmed live via
tenant_resolved_tables.json - see data/mapping_catalog.json's
`asimFunctionRewrites._source` for the evidence trail). Swap the function call
for the table, and inline whatever named parameters we have a verified,
semantics-preserving `| where` translation for (see
`asimFunctionRewrites.paramRewrites` in the catalog).

Conservative by design: a call is only auto-rewritten when EVERY named
parameter it uses has a known translation. If any parameter is unrecognized,
the call is left untouched and flagged for manual review instead of guessing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import mapping_catalog


def _split_top_level_args(argtext: str) -> List[str]:
    """Split a call's argument text on top-level commas (respecting nested
    parens/brackets and string literals)."""
    parts: List[str] = []
    depth, start, i, n = 0, 0, 0, len(argtext)
    in_str: Optional[str] = None
    while i < n:
        c = argtext[i]
        if in_str:
            if c == "\\" and in_str == '"' and not (i > 0 and argtext[i - 1] == "@"):
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"'):
            in_str = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(argtext[start:i])
            start = i + 1
        i += 1
    tail = argtext[start:]
    if tail.strip():
        parts.append(tail)
    return parts


def _find_call(kql: str, func_name: str, pos: int) -> Optional[Tuple[int, int, str]]:
    """If `func_name` at `pos` is followed (allowing whitespace) by a balanced
    `(...)`, return (call_start, call_end, argtext). Else None (bare reference)."""
    j = pos + len(func_name)
    while j < len(kql) and kql[j] in " \t\r\n":
        j += 1
    if j >= len(kql) or kql[j] != "(":
        return None
    depth, k, n = 1, j + 1, len(kql)
    in_str: Optional[str] = None
    while k < n and depth > 0:
        c = kql[k]
        if in_str:
            if c == "\\" and in_str == '"' and not (k > 0 and kql[k - 1] == "@"):
                k += 2
                continue
            if c == in_str:
                in_str = None
        elif c in ("'", '"'):
            in_str = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        k += 1
    return pos, k, kql[j + 1:k - 1]


def _comment_mask(text: str) -> List[bool]:
    """[ASIM-FIX 2026-08-02] Per-character `True` if that position is inside a
    `//...` KQL comment (from `//` to end of line), string-literal-aware so a `//` inside a
    quoted string isn't mistaken for a comment start."""
    mask = [False] * len(text)
    in_str: Optional[str] = None
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\" and in_str == '"' and not (i > 0 and text[i - 1] == "@"):
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"'):
            in_str = c
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = i
            while j < n and text[j] != "\n":
                mask[j] = True
                j += 1
            i = j
            continue
        i += 1
    return mask


def rewrite_im_calls(kql: str, catalog: Optional[dict] = None) -> dict:
    """Rewrite every `_Im_<Schema>(...)` / bare `_Im_<Schema>` reference in
    `kql` that this catalog knows how to translate.

    Returns: {"convertedKql": str, "diff": [...], "flags": [...]}.
    """
    cat = catalog or mapping_catalog.load_mapping_catalog()
    asim = cat.get("asimFunctionRewrites", {})
    functions: Dict[str, dict] = asim.get("functions", {})
    param_rewrites: Dict[str, dict] = asim.get("paramRewrites", {})

    if not functions:
        return {"convertedKql": kql, "diff": [], "flags": []}

    names = sorted(functions, key=len, reverse=True)
    pat = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b")

    diff: List[dict] = []
    flags: List[dict] = []
    out = kql
    # Process rightmost-first so earlier offsets stay valid as we splice.
    # Skip matches inside `//` comments - dead/inert text (e.g. an author's
    # commented-out "if you enable _Im_Dns, uncomment this" suggestion) is not
    # a live call and must not be rewritten or flagged for manual review.
    comment_mask = _comment_mask(out)
    matches = [m for m in pat.finditer(out) if not comment_mask[m.start()]]
    for m in reversed(matches):
        func = m.group(1)
        ah_table = functions[func]["ahTable"]
        call = _find_call(out, func, m.start())
        if call is None:
            # Bare reference (no parens) - safe straight rename, no params to lose.
            out = out[:m.start()] + ah_table + out[m.end():]
            diff.append({"kind": "asim-function-rewrite", "before": func,
                         "after": ah_table, "count": 1, "source": "deterministic",
                         "func": func, "ahTable": ah_table,
                         "reason": "ASIM unifying-parser function call replaced by "
                                   "its AH-native normalized table (no params to translate)."})
            continue

        start, end, argtext = call
        args = _split_top_level_args(argtext)
        clauses: List[str] = []
        unknown: List[str] = []
        for a in args:
            a = a.strip()
            if not a or "=" not in a:
                unknown.append(a)
                continue
            key, value = a.split("=", 1)
            key, value = key.strip(), value.strip()
            spec = param_rewrites.get(key)
            if spec is None:
                unknown.append(a)
                continue
            if spec.get("drop"):
                continue
            clauses.append(spec["template"].format(value=value))

        if unknown:
            # Don't guess - leave this call exactly as-is, flag for manual review.
            flags.append({"kind": "asim-function-unrewritten", "name": func,
                          "reason": f"Call to {func}(...) uses parameter(s) "
                                    f"{unknown} with no verified AH translation; "
                                    f"left unchanged. Manual review required "
                                    f"(equivalent table is {ah_table})."})
            continue

        replacement = ah_table
        if clauses:
            replacement += "\n    | where " + "\n    | where ".join(clauses)
        out = out[:start] + replacement + out[end:]
        diff.append({"kind": "asim-function-rewrite", "before": f"{func}({argtext})",
                     "after": replacement, "count": 1, "source": "deterministic",
                     "func": func, "ahTable": ah_table,
                     "reason": f"ASIM unifying-parser function call replaced by "
                               f"{ah_table} with its named parameters inlined as "
                               f"where clauses."})

    return {"convertedKql": out, "diff": diff, "flags": flags}


def flag_im_calls(kql: str, catalog: Optional[dict] = None) -> List[dict]:
    """[ASIM-FIX-TAG 2026-08-03] Detection-only counterpart to `rewrite_im_calls`,
    used while `rewrite.ASIM_REWRITE_ENABLED = False`. Every live `_Im_<Schema>(...)`
    / bare `_Im_<Schema>` reference is left completely untouched in the KQL and
    flagged for manual review - same flag shape (`asim-function-unrewritten`) the
    rewriter already produces for calls with an untranslatable parameter, so the
    existing needs-review gate in rewrite.py handles this path identically without
    any gate changes. Does not rewrite anything and returns no `diff`.

    [ASIM-FIX-TAG 2026-08-03b] Each flag also carries `func`, `ahTable`, and a
    `translatable` bool distinguishing two risk levels, so callers (batch_xdr.py)
    can decide whether a passing live validation may be trusted:
    - `translatable=True`: every named parameter used (if any) has a verified
      catalog translation - i.e. this call WOULD have been safely auto-rewritten
      had the rewrite been enabled. The only remaining unknown is whether AH has
      this Sentinel-workspace function at all on a generic tenant, not whether
      the data it returns (if it resolves) is correct.
    - `translatable=False`: uses a parameter with NO verified translation - the
      exact 2026-08-02 finding scenario (`_Im_FileEvent` silently binding to
      Blob-storage-log-shaped columns). A passing live bind/run must NOT be
      trusted here regardless of outcome.
    """
    cat = catalog or mapping_catalog.load_mapping_catalog()
    asim = cat.get("asimFunctionRewrites", {})
    functions: Dict[str, dict] = asim.get("functions", {})
    param_rewrites: Dict[str, dict] = asim.get("paramRewrites", {})
    if not functions:
        return []

    names = sorted(functions, key=len, reverse=True)
    pat = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b")
    comment_mask = _comment_mask(kql)

    flags: List[dict] = []
    seen: set = set()
    for m in pat.finditer(kql):
        if comment_mask[m.start()]:
            continue
        func = m.group(1)
        if func in seen:
            continue
        seen.add(func)
        ah_table = functions[func]["ahTable"]

        translatable = True
        call = _find_call(kql, func, m.start())
        if call is not None:
            _, _, argtext = call
            for a in _split_top_level_args(argtext):
                a = a.strip()
                if not a:
                    continue
                if "=" not in a or a.split("=", 1)[0].strip() not in param_rewrites:
                    translatable = False
                    break

        reason = (f"ASIM rewrite currently disabled (AH does not yet natively "
                  f"support unifying parsers for generic tenants); {func}(...) "
                  f"left unchanged. Manual review required (equivalent table "
                  f"would be {ah_table}).") if translatable else (
                  f"Call to {func}(...) uses a parameter with no verified AH "
                  f"translation; ASIM rewrite disabled, so it is left unchanged "
                  f"and must not be trusted even if it appears to bind/run "
                  f"(equivalent table would be {ah_table}).")
        flags.append({"kind": "asim-function-unrewritten", "name": func,
                      "func": func, "ahTable": ah_table, "translatable": translatable,
                      "reason": reason})
    return flags
