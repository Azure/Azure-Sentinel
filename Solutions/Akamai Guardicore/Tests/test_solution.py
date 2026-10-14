#!/usr/bin/env python3
"""Structural / regression tests for the Akamai Guardicore Sentinel solution.

These are self-contained (stdlib ``unittest`` only, no pip deps) and are meant
to guard the defects fixed in v3.0.1 plus the general packaging invariants of a
CCF (Codeless Connector Framework) solution. Run from anywhere:

    python3 -m unittest discover -s "Solutions/Akamai Guardicore/Tests" -v
    # or
    python3 "Solutions/Akamai Guardicore/Tests/test_solution.py"
"""

import json
import re
import unittest
import zipfile
from pathlib import Path

SOLUTION_DIR = Path(__file__).resolve().parents[1]

CCP_DIR = SOLUTION_DIR / "Data Connectors" / "AkamaiGuardicoreLogs_ccp"
MAIN_TEMPLATE = SOLUTION_DIR / "Package" / "mainTemplate.json"
CREATE_UI = SOLUTION_DIR / "Package" / "createUiDefinition.json"
TABLES = CCP_DIR / "AkamaiGuardicore_Tables.json"
POLLING = CCP_DIR / "AkamaiGuardicore_PollingConfig.json"
CONNECTOR_DEF = CCP_DIR / "AkamaiGuardicore_ConnectorDefinition.json"
SOLUTION_MANIFEST = SOLUTION_DIR / "Data" / "Solution_AkamaiGuardicore.json"
RELEASE_NOTES = SOLUTION_DIR / "ReleaseNotes.md"

EXPECTED_SOLUTION_VERSION = "3.0.1"
FIXED_CONTENT_SCHEMA_VERSION = "3.0.0"  # intentionally NOT bumped with the solution
EXPECTED_TABLES = {
    "GuardicoreAgents_CL",
    "GuardicoreAssets_CL",
    "GuardicoreApplications_CL",
    "GuardicorePolicyRules_CL",
}
BARE_TABLE_RE = re.compile(r"^Guardicore[A-Za-z]+_CL$")

# Per-poller paging expectations, keyed by a unique fragment of each poller's
# apiEndpoint: (offsetParaName, pageSizeParaName, pageSize).

EXPECTED_PAGING = {
    "/api/v3.0/agents": ("offset", "limit", 1000),
    "/api/v3.0/assets": ("offset", "limit", 1000),
    "/api/v3.0/workflow/projects": ("offset", "limit", 1000),
    "/api/v3.0/visibility/policy/rules": ("offset", "limit", 1000),
}
# Paging param names that must never appear as a literal version-branching ARM
# expression again (the removed dropdown era).
FORBIDDEN_PAGING_TOKENS = ("centraVersion", "if(equals")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def walk_dicts(obj):
    """Yield every dict nested anywhere inside a parsed JSON structure."""
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_dicts(item)


def collect_values(obj, key):
    """All values stored under `key` anywhere in the structure."""
    return [d[key] for d in walk_dicts(obj) if key in d]


def find_pollers(main_template):
    """Each RestApiPoller carries a `paging` and a `request` block."""
    return [d for d in walk_dicts(main_template) if "paging" in d and "request" in d]


def endpoint_of(poller):
    return poller["request"].get("apiEndpoint", "")


def paging_of(poller):
    """(offsetParaName, pageSizeParaName, pageSize) for a poller's paging block."""
    paging = poller["paging"]
    return (
        paging.get("offsetParaName"),
        paging.get("pageSizeParaName"),
        paging.get("pageSize"),
    )


def expected_paging_for(poller):
    """Look up (endpoint_fragment, expected_triple) by the poller's endpoint; the
    fragment is None when the endpoint is not one we recognise."""
    endpoint = endpoint_of(poller)
    for fragment, expected in EXPECTED_PAGING.items():
        if fragment in endpoint:
            return fragment, expected
    return None, None


class TestFilesExist(unittest.TestCase):
    def test_expected_files_present(self):
        for path in (
            MAIN_TEMPLATE, CREATE_UI, TABLES, POLLING, CONNECTOR_DEF,
            SOLUTION_MANIFEST, RELEASE_NOTES,
        ):
            self.assertTrue(path.exists(), f"missing expected file: {path}")


class TestJsonIsValid(unittest.TestCase):
    def test_all_solution_json_parses(self):
        failures = []
        for path in SOLUTION_DIR.rglob("*.json"):
            try:
                load_json(path)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                failures.append(f"{path.relative_to(SOLUTION_DIR)}: {exc}")
        self.assertEqual([], failures, "invalid JSON files found")


class TestNoWorkspaceNamePlaceholder(unittest.TestCase):
    """Regression: v3.0.0 shipped CCF table names as ``{{workspaceName}}/Guardicore*_CL``.

    The packaging tool never substitutes ``{{workspaceName}}`` on a table ``name``,
    so the literal token leaked into the deployed resource and table creation 404'd.
    """

    def test_ccp_connector_sources_have_no_placeholder(self):
        offenders = []
        for path in CCP_DIR.rglob("*.json"):
            if "{{workspaceName}}" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(SOLUTION_DIR)))
        self.assertEqual([], offenders, "{{workspaceName}} leaked into CCF connector files")

    def test_main_template_has_no_placeholder(self):
        self.assertNotIn("{{workspaceName}}", MAIN_TEMPLATE.read_text(encoding="utf-8"))


class TestTableNamesAreBare(unittest.TestCase):
    """Regression: CCF ``workspaces/tables`` resources must use bare ``_CL`` names."""

    def test_source_tables_are_bare(self):
        tables = load_json(TABLES)
        names = [t["name"] for t in tables]
        self.assertEqual(len(names), 4, "expected exactly 4 table resources")
        self.assertEqual(set(names), EXPECTED_TABLES)
        for table in tables:
            self.assertRegex(table["name"], BARE_TABLE_RE)
            # the inner schema name must match the bare outer name
            self.assertEqual(table["name"], table["properties"]["schema"]["name"])

    def test_ccf_tables_bare_in_main_template(self):
        # Only the four CCF connector tables must be bare. The playbook-created
        # tables (e.g. GuardicoreProcessedIncidents_CL) legitimately use the
        # plain-ARM concat(parameters('WorkspaceName'), ...) form and are allowed.
        main = load_json(MAIN_TEMPLATE)
        table_names = [
            d["name"]
            for d in walk_dicts(main)
            if isinstance(d.get("type"), str)
            and d["type"].lower().endswith("workspaces/tables")
            and isinstance(d.get("name"), str)
        ]
        self.assertTrue(table_names, "no workspaces/tables resources found in mainTemplate")
        for expected in EXPECTED_TABLES:
            self.assertIn(
                expected, table_names,
                f"CCF table {expected} is not present as a bare resource name",
            )
        # No table resource may carry an unresolved {{...}} packaging placeholder.
        for name in table_names:
            self.assertNotIn(
                "{{", name,
                f"table resource name contains an unresolved placeholder: {name!r}",
            )


class TestPaging(unittest.TestCase):
    """Each poller pages correctly for its own endpoint."""

    def test_each_poller_has_expected_paging(self):
        pollers = find_pollers(load_json(MAIN_TEMPLATE))
        self.assertEqual(len(pollers), 4, "expected exactly 4 RestApiPollers")
        seen = set()
        for poller in pollers:
            fragment, expected = expected_paging_for(poller)
            self.assertIsNotNone(
                expected, f"unrecognised poller endpoint: {endpoint_of(poller)!r}")
            self.assertEqual(poller["paging"].get("pagingType"), "Offset")
            self.assertEqual(
                paging_of(poller), expected,
                f"paging mismatch for {fragment}: got {paging_of(poller)}, want {expected}")
            seen.add(fragment)
        self.assertEqual(
            seen, set(EXPECTED_PAGING),
            "not every expected endpoint was present exactly once")


class TestVersionConsistency(unittest.TestCase):
    def test_solution_version_fields(self):
        main = load_json(MAIN_TEMPLATE)
        variables = main.get("variables", {})
        self.assertEqual(variables.get("_solutionVersion"), EXPECTED_SOLUTION_VERSION)
        self.assertEqual(variables.get("dataConnectorCCPVersion"), EXPECTED_SOLUTION_VERSION)

    def test_content_schema_version_is_fixed(self):
        # contentSchemaVersion is a FIXED schema version and must NOT track the
        # solution version bump.
        main = load_json(MAIN_TEMPLATE)
        values = set(collect_values(main, "contentSchemaVersion"))
        self.assertTrue(values, "no contentSchemaVersion found")
        self.assertEqual(
            values, {FIXED_CONTENT_SCHEMA_VERSION},
            f"contentSchemaVersion must stay {FIXED_CONTENT_SCHEMA_VERSION}; found {values}",
        )

    def test_solution_manifest_version(self):
        manifest = load_json(SOLUTION_MANIFEST)
        self.assertEqual(manifest.get("Version"), EXPECTED_SOLUTION_VERSION)

    def test_release_notes_has_current_version_row(self):
        notes = RELEASE_NOTES.read_text(encoding="utf-8")
        self.assertRegex(
            notes, rf"\|\s*{re.escape(EXPECTED_SOLUTION_VERSION)}\s*\|",
            "ReleaseNotes.md is missing a row for the current version",
        )


class TestPackageZipParity(unittest.TestCase):
    """The published ``<version>.zip`` must byte-match the loose Package files."""

    def test_zip_matches_loose_files(self):
        zip_path = SOLUTION_DIR / "Package" / f"{EXPECTED_SOLUTION_VERSION}.zip"
        self.assertTrue(zip_path.exists(), f"missing package zip: {zip_path.name}")
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
            self.assertEqual(
                names, {"mainTemplate.json", "createUiDefinition.json"},
                "zip must contain exactly mainTemplate.json + createUiDefinition.json",
            )
            for name in names:
                zipped = zf.read(name)
                loose = (SOLUTION_DIR / "Package" / name).read_bytes()
                self.assertEqual(
                    zipped, loose,
                    f"{name} inside {zip_path.name} is stale vs the loose file",
                )

    def test_no_stale_version_zips(self):
        zips = {p.name for p in (SOLUTION_DIR / "Package").glob("*.zip")}
        self.assertEqual(
            zips, {f"{EXPECTED_SOLUTION_VERSION}.zip"},
            f"unexpected package zips present: {zips}",
        )


class TestSourcePackageConsistency(unittest.TestCase):
    """The CCF source files must carry the same single-version, per-endpoint paging
    the packaged mainTemplate deploys, so re-running the packaging tool reproduces
    the working template."""

    def test_connector_definition_has_no_dropdown(self):
        dropdowns = [
            d for d in walk_dicts(load_json(CONNECTOR_DEF))
            if d.get("type") == "Dropdown"
        ]
        self.assertEqual(
            [], dropdowns,
            "the version dropdown must be removed from the source connector definition")

    def test_source_paging_matches_package(self):
        pollers = find_pollers(load_json(POLLING))
        self.assertEqual(len(pollers), 4, "expected exactly 4 pollers in the source polling config")
        for poller in pollers:
            fragment, expected = expected_paging_for(poller)
            self.assertIsNotNone(
                expected, f"unrecognised source poller endpoint: {endpoint_of(poller)!r}")
            self.assertEqual(
                paging_of(poller), expected,
                f"source paging mismatch for {fragment}: got {paging_of(poller)}, want {expected}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
