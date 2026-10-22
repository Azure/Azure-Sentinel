# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the repository root.
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[3]
COMMON = ROOT / "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"


def literal(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class DefenderWorkbookPackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory(prefix="wb-packaging-", dir=Path.cwd())
        self.root = Path(self.scratch.name)
        self.solution = self.root / "Solutions" / "Sample"
        self.source = self.solution / "Workbooks" / "nested" / "source.json"
        self.source.parent.mkdir(parents=True)
        self.source.write_text(json.dumps({
            "version": "Notebook/1.0",
            "items": [
                {"type": 3, "content": {"query": "SourceTable | take 1"}},
                {"query": "scope"},
            ],
        }), encoding="utf-8")
        self.notebook = {
            "version": "Notebook/1.0",
            "items": [
                {"type": 3, "content": {"query": "DeviceEvents | take 1"}},
                {"type": 1, "content": {"json": "[parameters('authored-literal')]"}},
            ],
            "fallbackResourceIds": ["[[already-bracketed]", "literal"],
            "xdrMetadata": {
                "schemaVersion": "1.0.0",
                "contentId": str(uuid.uuid5(uuid.NAMESPACE_URL, "fixture/workbook/content")),
                "instanceId": str(uuid.uuid5(uuid.NAMESPACE_URL, "fixture/workbook/instance")),
                "version": "3.1.0",
                "displayName": "Synthetic workbook",
            },
            "contentProvenance": {
                "source": {
                    "path": "Workbooks/nested/source.json",
                    "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                    "originalMetadataVersion": "1.2.0",
                },
                "conversion": {
                    "tool": "sentinel-xdr-migration",
                    "version": "0.1.0",
                    "reviewRequired": False,
                    "queries": [{
                        "sourcePath": "/items/0/content/query",
                        "outputPath": "/items/0/content/query",
                        "sourceSha256": hashlib.sha256(b"SourceTable | take 1").hexdigest(),
                        "targetSha256": hashlib.sha256(b"DeviceEvents | take 1").hexdigest(),
                        "status": "converted",
                    }],
                },
                "requiredWorkloads": [{"workload": "mde", "dataTypes": ["DeviceEvents"]}],
                "requiredDataConnectors": [{"connectorId": "SyntheticConnector", "dataTypes": ["DeviceEvents"]}],
                "dependencyReviewRequired": False,
            },
        }
        self.reference = "XDR Workbooks/nested/workbook.json"
        self.target = self.solution / self.reference
        self.target.parent.mkdir(parents=True)
        self.write()
        self.data = {"Version": "3.2.7", "XDR Workbooks": [self.reference]}
        self.native = {
            "type": "Microsoft.Insights/workbooks", "name": "synthetic-native",
            "properties": {"serializedData": '{"version":"Notebook/1.0","items":[]}'},
            "condition": "[equals('native','native')]",
        }
        self.template = {
            "parameters": {},
            "variables": {"solutionId": "synthetic.publisher", "_solutionVersion": "3.2.7"},
            "resources": [{
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                "properties": {"contentKind": "Solution", "descriptionHtml": "", "icon": "", "dependencies": {
                    "criteria": [{"kind": "Workbook", "contentId": "native", "version": "1.0.0"}],
                }},
            }, copy.deepcopy(self.native)],
        }
        self.ui = {"parameters": {
            "outputs": {}, "steps": [], "config": {"basics": {
                "description": "{{SolutionDescription}}\n\n**Workbooks:** 1\n\n{{Logo}}",
            }},
        }}

    def tearDown(self) -> None:
        self.scratch.cleanup()

    def write(self) -> None:
        self.target.write_text(json.dumps(self.notebook), encoding="utf-8")

    def invoke(self, *, success: bool = True, package: bool = False, unchanged: bool = False,
               tracking_id: str | None = "pid-workbook-regression") -> dict:
        payload = self.root / "input.json"
        payload.write_text(json.dumps({
            "data": self.data, "template": self.template, "ui": self.ui,
        }), encoding="utf-8")
        emit = (
            f"$count=Add-XdrDefenderWorkbooksToSolution -SolutionName Sample -ContentToImport $inputData.data "
            f"-Template $template -RepositoryRoot {literal(self.root)}; "
            "Add-SolutionContentDeploymentParameters -Template $template -UiDefinition $ui; "
            "$global:baseCreateUiDefinition=$ui; Update-DefenderWorkbookDescriptionCount -Count $count; "
        )
        if package:
            metadata = self.solution / "SolutionMetadata.json"
            metadata.write_text(json.dumps({"trackingId": tracking_id}), encoding="utf-8")
            emit = (
                f"function git {{ $global:LASTEXITCODE=0; return {literal(self.root)} }}; "
                "$global:baseMainTemplate=$template; $global:baseCreateUiDefinition=$ui; "
                "$template | Add-Member -NotePropertyName metadata -NotePropertyValue "
                "([pscustomobject]@{author='';comments='{{SolutionName}}'}); "
                "$contentResourceDetails=[pscustomobject]@{apiVersion='3.0.0'}; "
                "GeneratePackage -solutionName Sample -contentToImport $inputData.data -IncludeXdrDetections $true "
                f"-SolutionMetadataPath {literal(metadata)} -SkipAttributionLookup; "
                "$count=@($template.resources | Where-Object {$_.properties.contentKind -eq 'DefenderWorkbook'}).Count; "
            )
        command = (
            "$ErrorActionPreference='Stop'; "
            f". {literal(COMMON)}; "
            f"$inputData=Get-Content -Raw -LiteralPath {literal(payload)} | ConvertFrom-Json; "
            "$template=$inputData.template; $ui=$inputData.ui; "
            "Register-SolutionResourceKind -Resources @($template.resources | Where-Object "
            "{$_.type -eq 'Microsoft.OperationalInsights/workspaces/savedSearches'}) -Kind Parser; "
            + (
                "$before=$template | ConvertTo-Json -Depth 100 -Compress; try {" + emit +
                "} catch {if (($template | ConvertTo-Json -Depth 100 -Compress) -cne $before) "
                "{throw 'TEMPLATE_MUTATED_BEFORE_FAILURE'}; throw}; "
                if unchanged else emit
            ) +
            "Write-Output '__RESULT__'; "
            "[pscustomobject]@{count=$count;template=$template;ui=$ui} | ConvertTo-Json -Depth 100 -Compress"
        )
        result = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True, text=True, check=False,
        )
        if not success:
            self.assertNotEqual(0, result.returncode, result.stdout)
            self.assertNotIn("__RESULT__", result.stdout)
            self.assertNotIn("TEMPLATE_MUTATED_BEFORE_FAILURE", result.stderr)
            normalized = " ".join(
                re.sub(r"\x1b\[[0-9;]*m", "", result.stderr).replace("|", " ").split()
            )
            return {"error": f"{result.stderr}\n{normalized}"}
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("__RESULT__", result.stdout)
        return json.loads(result.stdout.split("__RESULT__", 1)[1].strip())

    def add_function(
        self, alias: str = "ReviewedParser", *, folder: str = "Parsers",
        name: str = "[variables('parserObject1')._parserName1]",
    ) -> dict:
        path = self.solution / folder / f"{alias}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"FunctionName: {alias}\nFunctionAlias: {alias}\n"
            "FunctionParams:\n  - Name: limit\n    Type: int\n    Default: 1\n"
            "FunctionQuery: |\n  DeviceEvents | take limit\n", encoding="utf-8",
        )
        record = {
            "functionAlias": alias, "sourcePath": path.relative_to(self.solution).as_posix(),
            "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        self.notebook["contentProvenance"].setdefault("requiredWorkspaceFunctions", []).append(record)
        self.notebook["contentProvenance"]["conversion"]["queries"][0].setdefault(
            "workspaceFunctions", [],
        ).append(alias)
        self.data.setdefault("Parsers", []).append(record["sourcePath"])
        parser_match = re.fullmatch(
            r"\[variables\('(parserObject([1-9][0-9]*))'\)\.(_?parserName\2)\]",
            name,
        )
        if parser_match:
            obj_name, idx, name_prop = parser_match.groups()
            arm_leaf = "different-arm-name" if idx == "1" else f"{alias}-arm-name"
            self.template["variables"][obj_name] = {
                name_prop: f"[concat(parameters('workspace'),'/','{arm_leaf}')]",
                f"_parserId{idx}": (
                    "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', "
                    f"parameters('workspace'), '{arm_leaf}')]"
                ),
            }
        resource = {
            "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
            "name": name,
            "properties": {
                "functionAlias": alias, "query": "DeviceEvents | take limit\n",
                "functionParameters": "limit:int=1", "eTag": "*",
            },
        }
        self.template["resources"].append(resource)
        self.write()
        return resource

    def invoke_prerequisites(self, *, success: bool = True) -> str:
        self.write()
        payload = self.root / "prerequisites.json"
        payload.write_text(json.dumps({"data": self.data, "template": self.template}), encoding="utf-8")
        result = subprocess.run([
            "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
            "$ErrorActionPreference='Stop'; "
            f". {literal(COMMON)}; "
            f"$inputData=Get-Content -Raw -LiteralPath {literal(payload)} | ConvertFrom-Json; "
            f"$doc=Get-Content -Raw -LiteralPath {literal(self.target)} | ConvertFrom-Json; "
            "Get-DefenderWorkbookParserDependencies -Document $doc -ContentToImport $inputData.data "
            f"-Template $inputData.template -SolutionRoot {literal(self.solution)} -SolutionName Sample; "
            "Write-Output '__PREREQUISITES_PASSED__'",
        ], capture_output=True, text=True, check=False)
        self.assertEqual(success, result.returncode == 0, result.stderr)
        self.assertEqual(success, "__PREREQUISITES_PASSED__" in result.stdout)
        normalized = " ".join(
            re.sub(r"\x1b\[[0-9;]*m", "", result.stderr).replace("|", " ").split()
        )
        return f"{result.stderr}\n{normalized}"

    def scope_fixture(self) -> None:
        original = json.loads(self.source.read_bytes())
        original["items"][1] = {"content": {
            "resourceType": "microsoft.operationalinsights/workspaces",
            "parameters": [{
                "name": "Workspace", "type": 5, "queryType": 1,
                "query": "resources | where type =~ 'microsoft.operationalinsights/workspaces'",
            }],
        }}
        self.source.write_text(json.dumps(original), encoding="utf-8")
        provenance = self.notebook["contentProvenance"]
        provenance["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        provenance["conversion"]["queries"].append({
            "sourcePath": "/items/1/content/parameters/0/query",
            "sourceSha256": hashlib.sha256(original["items"][1]["content"]["parameters"][0]["query"].encode()).hexdigest(),
            "outputPath": None, "targetSha256": None, "status": "removed-scope-helper",
        })

    def test_prerequisite_scan_excludes_only_proven_removed_scope_helpers(self) -> None:
        self.scope_fixture()
        source_before = self.source.read_bytes()
        self.invoke_prerequisites()
        self.assertEqual(source_before, self.source.read_bytes())
        target_before = self.target.read_bytes()
        self.invoke_prerequisites()
        self.assertEqual(target_before, self.target.read_bytes())
        baseline = copy.deepcopy(self.notebook)
        for mutation in (
            "source-hash", "query-hash", "pointer", "status", "output",
            "retained-parameter", "retained-query", "retained-reference",
        ):
            with self.subTest(mutation=mutation):
                self.notebook = copy.deepcopy(baseline)
                provenance = self.notebook["contentProvenance"]
                query = provenance["conversion"]["queries"][-1]
                if mutation == "source-hash":
                    provenance["source"]["sha256"] = "0" * 64
                elif mutation == "query-hash":
                    query["sourceSha256"] = "0" * 64
                elif mutation == "pointer":
                    query["sourcePath"] = "/items/99/query"
                elif mutation == "status":
                    query["status"] = "blocked"
                elif mutation == "output":
                    query["outputPath"] = "/items/0/content/query"
                elif mutation == "retained-parameter":
                    self.notebook["items"].append({"content": {"parameters": [{"name": "Workspace", "type": 5}]}})
                elif mutation == "retained-query":
                    self.notebook["items"].append({"query": json.loads(source_before)["items"][1]["content"]["parameters"][0]["query"]})
                else:
                    self.notebook["items"].append({"content": {"json": "{Workspace}"}})
                self.invoke_prerequisites(success=False)

    def test_prerequisite_scope_proof_rejects_nonhelpers_and_live_dependencies(self) -> None:
        self.scope_fixture()
        baseline_source = json.loads(self.source.read_bytes())
        baseline = copy.deepcopy(self.notebook)
        for mutation in ("ordinary-query", "kql-parameter", "time-parameter", "live-text", "live-parameter", "duplicate-name"):
            with self.subTest(mutation=mutation):
                source = copy.deepcopy(baseline_source)
                self.notebook = copy.deepcopy(baseline)
                param = source["items"][1]["content"]["parameters"][0]
                if mutation == "ordinary-query":
                    source["items"][1] = {"query": param["query"]}
                    self.notebook["contentProvenance"]["conversion"]["queries"][-1]["sourcePath"] = "/items/1/query"
                elif mutation == "kql-parameter":
                    param["queryType"] = 0
                elif mutation == "time-parameter":
                    param["type"] = 4
                elif mutation == "live-text":
                    source["items"].append({"content": {"json": "{Workspace}"}})
                elif mutation == "live-parameter":
                    source["items"][1]["content"]["parameters"].append({
                        "name": "Filter", "type": 1, "value": "{Workspace}",
                    })
                else:
                    source["items"][1]["content"]["parameters"].append(copy.deepcopy(param))
                self.source.write_text(json.dumps(source), encoding="utf-8")
                self.notebook["contentProvenance"]["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
                self.invoke_prerequisites(success=False)

    def test_prerequisite_scope_dependency_closure_matches_python(self) -> None:
        from sentinel_xdr_migration._workbook_core import workbook
        self.scope_fixture()
        source = json.loads(self.source.read_bytes())
        params = source["items"][1]["content"]["parameters"]
        params[0]["query"] += " | where subscriptionId in ({Subscription})"
        params.append({"name": "Subscription", "type": 6, "value": "all"})
        params.append({
            "name": "ContextFree", "type": 1, "isHiddenWhenLocked": True,
            "queryType": 1, "query": "print context='{Workspace}'",
        })
        source["items"][0]["content"]["resourceContextFromParameter"] = "Workspace"
        _, removed, retained = workbook._scope_parameters(source)
        self.assertEqual({"Workspace", "Subscription", "ContextFree"}, removed)
        self.assertFalse(retained)
        self.source.write_text(json.dumps(source), encoding="utf-8")
        provenance = self.notebook["contentProvenance"]
        provenance["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        provenance["conversion"]["queries"][-1]["sourceSha256"] = hashlib.sha256(params[0]["query"].encode()).hexdigest()
        provenance["conversion"]["queries"].append({
            "sourcePath": "/items/1/content/parameters/2/query",
            "sourceSha256": hashlib.sha256(params[2]["query"].encode()).hexdigest(),
            "outputPath": None, "targetSha256": None, "status": "removed-scope-helper",
        })
        self.invoke_prerequisites()
        source["items"].append({"content": {"json": "{ContextFree}"}})
        _, removed, retained = workbook._scope_parameters(source)
        self.assertFalse(removed)
        self.assertEqual({"Workspace", "Subscription", "ContextFree"}, retained)
        self.source.write_text(json.dumps(source), encoding="utf-8")
        provenance["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.invoke_prerequisites(success=False)

    def test_prerequisite_scanner_matches_reviewed_python_query_contracts(self) -> None:
        from sentinel_xdr_migration._workbook_core import workbook
        queries = [
            "let gran = {Granularity}; EmailEvents | summarize count() by bin(Timestamp, gran)",
            "let gran = {Granularity}; EmailEvents | make-series count() on Timestamp step gran",
            "union withsource=Table (print value=1), (EmailEvents | take 1)",
            "union kind=outer withsource=Table (print value=1), (HiddenParser())",
            "union withsource=totable (print value=1), (MessageEvents | take 1)",
            "union withsource=Table (print value=1), table(Name)",
            "EmailPostDeliveryEvents | take 1",
            "MessagePostDeliveryEvents | take 1",
            "MessageUrlInfo | take 1",
            "FileMaliciousContentInfo | take 1",
            "datatable(label:string, value:long)['EmailEvents', 1] | extend doubled=value*2",
            "let gran = {Granularity}; DeviceEvents | take 1",
            "let gran = {Other}; EmailEvents | summarize count() by bin(Timestamp, gran)",
            "{Granularity}() | take 1",
            "{Granularity} | take 1",
            "table({Granularity}) | take 1",
            "totable(strcat('Email', 'Events')) | take 1",
            "resources | take 1",
            "['resources'] | take 1",
            "EmailEvents() | take 1",
            "HiddenParser() | take 1",
            "DeviceEvents | invoke HiddenParser()",
            "let Data = HiddenParser(); Data",
            "table('HiddenParser') | take 1",
            "table('EmailEvents') | take 1",
            "datatable(label:string)['constant'] | join (HiddenParser()) on label",
            "let gran = {Granularity}; EmailEvents | summarize count() by bin(Timestamp, gran); table(Name)",
            "union withsource=Other (table(Name)), HiddenParser",
            "range x from 0 to 10 step 1",
            "range x from 0 to 20 step 1",
            "range x from 0 to HiddenParser() step 1",
            "range x from 0 to toscalar(HiddenParser() | count) step 1",
            "range x from 0 to 10 step 1 | union HiddenParser",
            "union (range x from 0 to 10 step 1), (HiddenParser())",
            "range x from 0 to 10 step 1 | union EmailEvents",
            "let UsersLocation = externaldata(ip:string)[@\"https://example.invalid/geo.csv\"] with (format='csv'); UsersLocation | take 1",
            "let UsersLocation = externaldata(ip:string)['https://example.invalid/geo.csv']; UsersLocation | join (HiddenParser()) on ip // trailing https://comment",
            "let U = datatable(u:string)[\"http://a//b\"]; // real comment HiddenParser()\nU | take 1",
        ]
        payload = self.root / "scanner-queries.json"
        payload.write_text(json.dumps(queries), encoding="utf-8")
        result = subprocess.run([
            "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
            "$ErrorActionPreference='Stop'; "
            f". {literal(COMMON)}; "
            f"$queries=Get-Content -Raw -LiteralPath {literal(payload)} | ConvertFrom-Json; "
            "$rows=@(foreach ($q in $queries) { ,@(Get-DefenderWorkbookImplicitFunctions "
            "-Value ([pscustomobject]@{query=$q}) | Sort-Object -Unique) }); "
            "ConvertTo-Json -InputObject $rows -Depth 10 -Compress",
        ], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        actual = json.loads(result.stdout)
        for query, aliases in zip(queries, actual, strict=True):
            with self.subTest(query=query):
                self.assertEqual(sorted(workbook.opaque_functions(query)), sorted(aliases))

    def test_reviewed_literal_range_dropdowns_package_without_dependencies(self) -> None:
        from sentinel_xdr_migration import workbook_dependencies, workbooks
        from test_workbook_dependencies import decisions, review

        source = json.loads(self.source.read_bytes())
        source["items"] = [{"type": 9, "content": {"parameters": [
            {"name": f"Range{i}", "type": 2, "queryType": 0, "query": query}
            for i, query in enumerate((
                "range x from 0 to 10 step 1", "range x from 0 to 20 step 1",
            ))
        ]}}]
        self.source.write_text(json.dumps(source), encoding="utf-8")
        data = self.solution / "Data/Solution_Sample.json"
        data.parent.mkdir()
        data.write_text(json.dumps({"Version": "3.2.7"}), encoding="utf-8")
        plan = workbook_dependencies.plan_workbook_dependencies(self.solution)
        reviewed = decisions(plan)
        for row in reviewed["queries"]:
            row["tables"] = []
        reviewed["workbooks"][0]["requiredWorkloads"] = []
        receipt = review(self.solution, plan, reviewed)
        self.assertFalse(receipt["dependencyReviewRequired"])
        settings = json.loads((self.solution / "Logs/review-1/conversion-config.json").read_bytes())
        result = workbooks.convert_workbooks(
            self.solution, config=settings, report_directory=self.solution / "Logs/conversion")
        self.assertEqual(1, result["converted"])
        self.target = self.solution / "XDR Workbooks/nested/source.json"
        self.reference = self.target.relative_to(self.solution).as_posix()
        self.data["XDR Workbooks"] = [self.reference]
        self.notebook = json.loads(self.target.read_bytes())
        self.assertEqual(1, workbooks.validate_workbooks(self.solution)["valid"])
        emitted = self.invoke(package=True)
        self.assertEqual(1, emitted["count"])
        resources = [r for r in emitted["template"]["resources"]
                     if r.get("properties", {}).get("contentKind") == "DefenderWorkbook"]
        self.assertEqual(1, len(resources))
        install = next(r for r in emitted["template"]["resources"]
                       if r["type"] == "Microsoft.Resources/deployments")
        installed = install["properties"]["template"]["resources"]["workbook"]["properties"]["content"]
        self.assertEqual(
            ["range x from 0 to 10 step 1", "range x from 0 to 20 step 1"],
            [p["query"] for p in installed["items"][0]["content"]["parameters"]],
        )
        provenance = self.notebook["contentProvenance"]
        self.assertEqual([], provenance["requiredWorkloads"])
        self.assertEqual([], provenance["requiredDataConnectors"])
        self.assertEqual([], provenance.get("requiredWorkspaceFunctions", []))

    def test_prerequisite_scanner_preserves_known_saved_table_aliases(self) -> None:
        self.add_function("EmailEvents")
        self.notebook["items"][0]["content"]["query"] = "EmailEvents | take 1"
        query = self.notebook["contentProvenance"]["conversion"]["queries"][0]
        query["targetSha256"] = hashlib.sha256(b"EmailEvents | take 1").hexdigest()
        query["workspaceFunctions"] = []
        self.notebook["contentProvenance"]["requiredWorkspaceFunctions"] = []
        error = self.invoke_prerequisites(success=False)
        self.assertIn("unreviewed implicit workspace function 'EmailEvents'", error)

    def _set_single_query(self, text: str) -> None:
        self.notebook["items"][0]["content"]["query"] = text
        query = self.notebook["contentProvenance"]["conversion"]["queries"][0]
        query["targetSha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        query["workspaceFunctions"] = []
        self.notebook["contentProvenance"]["requiredWorkspaceFunctions"] = []

    def test_builtin_asim_unifying_parsers_need_no_declaration_or_saved_search(self) -> None:
        for name in ("_ASim_RegistryEvent", "_Im_NetworkSession"):
            with self.subTest(name=name):
                self._set_single_query(f"{name} | take 1")
                self.invoke_prerequisites(success=True)
                self.assertFalse([
                    r for r in self.template["resources"]
                    if r.get("type") == "Microsoft.OperationalInsights/workspaces/savedSearches"
                ])

    def test_other_unknown_implicit_functions_are_still_rejected(self) -> None:
        for name in ("_Foo_RegistryEvent", "_Im_Test", "ASim_RegistryEvent"):
            with self.subTest(name=name):
                self._set_single_query(f"{name} | take 1")
                error = self.invoke_prerequisites(success=False)
                self.assertIn(f"unreviewed implicit workspace function '{name}'", error)

    def test_required_parser_dependencies_use_emitted_names_and_preserve_provenance(self) -> None:
        self.add_function()
        self.add_function("SecondParser", folder="Workspace Functions", name="lab/arm-name-not-alias")
        source = self.source.read_bytes()
        authored = self.target.read_bytes()
        result = self.invoke()
        resources = result["template"]["resources"]
        install = next(r for r in resources if r["type"] == "Microsoft.Resources/deployments")
        self.assertEqual([
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), "
            + "'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]",
            "[variables('parserObject1')._parserId1]",
            "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', 'lab/arm-name-not-alias')]",
        ], install["dependsOn"])
        registration = next(r for r in resources if r["type"].endswith("/contentTemplates"))
        self.assertEqual(
            self.notebook["contentProvenance"]["requiredWorkspaceFunctions"],
            registration["properties"]["contentProvenance"]["requiredWorkspaceFunctions"],
        )
        installed = install["properties"]["template"]["resources"]["workbook"]["properties"]["content"]
        self.assertEqual({"packageId", "packageVersion", "contentId", "contentVersion"}, set(installed["contentProvenance"]))
        self.assertEqual(authored, self.target.read_bytes())
        self.assertEqual(source, self.source.read_bytes())
        self.assertIn("DeployParser", result["template"]["parameters"])
        self.assertTrue(result["template"]["parameters"]["DeployParser"]["defaultValue"])
        self.assertIn("DeployParser", result["ui"]["parameters"]["outputs"])
        for resource in resources:
            if resource["type"].endswith("/savedSearches"):
                self.assertEqual("[parameters('DeployParser')]", resource.get("condition"))
                self.assertEqual("*", resource["properties"]["eTag"])

    def test_syslog_two_parser_objects_emit_canonical_parser_ids_and_pass_python_verifier(self) -> None:
        from sentinel_xdr_migration import packaging

        for prop_prefix in ("parserName", "_parserName"):
            with self.subTest(prop_prefix=prop_prefix):
                self.tearDown()
                self.setUp()
                self.notebook["xdrMetadata"]["version"] = self.data["Version"]
                self.add_function(
                    "SyslogConnectorsOverallStatus",
                    name=f"[variables('parserObject1').{prop_prefix}1]",
                )
                self.add_function(
                    "SyslogConnectorsEventVolumebyDeviceProduct",
                    name=f"[variables('parserObject2').{prop_prefix}2]",
                )
                query = (
                    "union (SyslogConnectorsOverallStatus() | take 1), "
                    "(SyslogConnectorsEventVolumebyDeviceProduct() | take 1)"
                )
                self.notebook["items"][0]["content"]["query"] = query
                self.notebook["contentProvenance"]["conversion"]["queries"][0]["targetSha256"] = (
                    hashlib.sha256(query.encode("utf-8")).hexdigest()
                )
                self.write()
                (self.solution / "Data").mkdir(exist_ok=True)
                (self.solution / "Data/Solution_Sample.json").write_text(
                    json.dumps({"Name": "Sample", **self.data}), encoding="utf-8"
                )
                self.invoke(package=True)
                package_dir = self.solution / "Package"
                template = json.loads((package_dir / "mainTemplate.json").read_text(encoding="utf-8-sig"))
                install = next(r for r in template["resources"] if r["type"] == "Microsoft.Resources/deployments")
                self.assertEqual([
                    "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), "
                    + "'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]",
                    "[variables('parserObject1')._parserId1]",
                    "[variables('parserObject2')._parserId2]",
                ], install["dependsOn"])
                receipt = packaging._verify_workbook_package(
                    self.solution, [self.target], template, package_dir / "3.2.7.zip"
                )
                self.assertEqual(1, receipt["count"])
                tampered = copy.deepcopy(template)
                tampered_install = next(
                    r for r in tampered["resources"] if r["type"] == "Microsoft.Resources/deployments"
                )
                tampered_install["dependsOn"][1] = (
                    f"[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', "
                    f"variables('parserObject1').{prop_prefix}1)]"
                )
                with self.assertRaises(RuntimeError):
                    packaging._verify_workbook_package(
                        self.solution, [self.target], tampered, package_dir / "3.2.7.zip"
                    )
                missing_id = copy.deepcopy(template)
                missing_id["variables"]["parserObject2"].pop("_parserId2")
                with self.assertRaises(RuntimeError):
                    packaging._verify_workbook_package(
                        self.solution, [self.target], missing_id, package_dir / "3.2.7.zip"
                    )

    def test_function_dependency_ids_deduplicate_and_contract_references_work(self) -> None:
        self.add_function()
        self.add_function("SecondParser")
        query = self.notebook["contentProvenance"]["conversion"]["queries"][0]
        query["contract"] = {"workspaceFunctions": query.pop("workspaceFunctions")}
        self.write()
        result = self.invoke()
        install = next(r for r in result["template"]["resources"] if r["type"] == "Microsoft.Resources/deployments")
        self.assertEqual(2, len(install["dependsOn"]))

    def test_full_package_requires_parsers_and_linked_registrations_but_not_unrelated_parsers(self) -> None:
        self.add_function()
        metadata = {
            "type": "Microsoft.OperationalInsights/workspaces/providers/metadata",
            "name": "lab/Microsoft.SecurityInsights/required-parser",
            "properties": {
                "kind": "Parser", "contentId": "[variables('parserObject1').parserContentId1]",
            },
        }
        registration = {
            "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
            "name": "lab/Microsoft.SecurityInsights/required-registration",
            "properties": {
                "contentKind": "Parser", "contentId": "[variables('parserObject1').parserContentId1]",
            },
        }
        self.template["variables"]["parserObject1"]["parserContentId1"] = "ReviewedParser-Parser"
        self.template["resources"] += [
            metadata, registration, {
                "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
                "name": "lab/unrelated",
                "properties": {"functionAlias": "UnrelatedParser", "query": "DeviceEvents"},
            },
        ]
        original = self.target.read_bytes()
        self.invoke(package=True)
        package = json.loads((self.solution / "Package/mainTemplate.json").read_text(encoding="utf-8-sig"))
        self.assertIn("DeployParser", package["parameters"])
        self.assertTrue(package["parameters"]["DeployParser"]["defaultValue"])
        for resource in package["resources"][2:5]:
            self.assertEqual("[parameters('DeployParser')]", resource.get("condition"))
        self.assertEqual("[parameters('DeployParser')]", package["resources"][5]["condition"])
        installation = next(r for r in package["resources"] if r["type"] == "Microsoft.Resources/deployments")
        self.assertIn(
            "[variables('parserObject1')._parserId1]",
            installation["dependsOn"],
        )
        self.assertEqual(original, self.target.read_bytes())
        self.template["resources"][3]["condition"] = False
        self.invoke(success=False, unchanged=True)

    def test_invalid_parser_provenance_and_selections_fail_without_mutation(self) -> None:
        self.add_function()
        baseline = copy.deepcopy(self.notebook)
        data = copy.deepcopy(self.data)
        for mutation in (
            "missing", "empty", "null", "extra", "duplicate", "bad-alias", "bad-path",
            "uppercase-hash", "stale-hash", "not-selected", "duplicate-selection",
            "missing-yaml", "wrong-yaml-alias", "conflicting-yaml-alias",
        ):
            with self.subTest(mutation=mutation):
                self.notebook = copy.deepcopy(baseline)
                self.data = copy.deepcopy(data)
                provenance = self.notebook["contentProvenance"]
                record = provenance["requiredWorkspaceFunctions"][0]
                path = self.solution / record["sourcePath"]
                original = path.read_bytes()
                if mutation == "missing":
                    provenance.pop("requiredWorkspaceFunctions")
                elif mutation == "empty":
                    provenance["requiredWorkspaceFunctions"] = []
                elif mutation == "null":
                    provenance["requiredWorkspaceFunctions"] = None
                elif mutation == "extra":
                    record["unreviewed"] = True
                elif mutation == "duplicate":
                    provenance["requiredWorkspaceFunctions"].append(copy.deepcopy(record))
                elif mutation == "bad-alias":
                    record["functionAlias"] = "bad-alias"
                elif mutation == "bad-path":
                    record["sourcePath"] = "Parsers/../Parsers/ReviewedParser.yaml"
                elif mutation == "uppercase-hash":
                    record["sourceSha256"] = record["sourceSha256"].upper()
                elif mutation == "stale-hash":
                    record["sourceSha256"] = "0" * 64
                elif mutation == "not-selected":
                    self.data["Parsers"] = []
                elif mutation == "duplicate-selection":
                    self.data["Parsers"] *= 2
                elif mutation == "missing-yaml":
                    path.unlink()
                else:
                    path.write_bytes(
                        original.replace(b"ReviewedParser", b"OtherParser")
                        if mutation == "wrong-yaml-alias"
                        else original.replace(b"FunctionAlias: ReviewedParser", b"FunctionAlias: OtherParser")
                    )
                    record["sourceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.write()
                self.invoke(success=False, unchanged=True)
                path.write_bytes(original)

    def test_effective_yaml_alias_and_all_selection_fields(self) -> None:
        self.add_function()
        record = self.notebook["contentProvenance"]["requiredWorkspaceFunctions"][0]
        path = self.solution / record["sourcePath"]
        original = path.read_bytes()
        for field in ("Parsers", "Data Parsers", "Workspace Functions"):
            with self.subTest(field=field):
                for selection in ("Parsers", "Data Parsers", "Workspace Functions"):
                    self.data.pop(selection, None)
                self.data[field] = [record["sourcePath"]]
                path.write_bytes(original.replace(b"FunctionName: ReviewedParser", b"FunctionName: InternalParserName"))
                record["sourceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.write()
                self.assertEqual(1, self.invoke()["count"])
        path.write_bytes(original.replace(b"FunctionAlias: ReviewedParser\n", b""))
        record["sourceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write()
        self.assertEqual(1, self.invoke()["count"])

    def test_parser_resource_failures_are_atomic_across_workbooks(self) -> None:
        self.add_function()
        other = self.target.with_name("ordinary.json")
        ordinary = copy.deepcopy(self.notebook)
        ordinary["contentProvenance"].pop("requiredWorkspaceFunctions")
        ordinary["contentProvenance"]["conversion"]["queries"][0].pop("workspaceFunctions")
        for field in ("contentId", "instanceId"):
            ordinary["xdrMetadata"][field] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"ordinary/{field}"))
        other.write_text(json.dumps(ordinary), encoding="utf-8")
        self.data["XDR Workbooks"].insert(0, other.relative_to(self.solution).as_posix())
        template = copy.deepcopy(self.template)
        for mutation in (
            "missing", "duplicate", "conditional", "conditional-true", "copy",
            "wrong-alias", "wrong-query", "wrong-parameters", "stored-only", "nested-only",
            "bad-name",
        ):
            with self.subTest(mutation=mutation):
                self.template = copy.deepcopy(template)
                resource = self.template["resources"][-1]
                if mutation == "missing":
                    self.template["resources"].pop()
                elif mutation == "duplicate":
                    self.template["resources"].append(copy.deepcopy(resource))
                elif mutation in ("conditional", "conditional-true"):
                    resource["condition"] = True if mutation.endswith("true") else "[parameters('DeployParser')]"
                elif mutation == "copy":
                    resource["copy"] = {"name": "parserLoop", "count": 1}
                elif mutation == "wrong-alias":
                    resource["properties"]["functionAlias"] = "reviewedparser"
                elif mutation == "wrong-query":
                    resource["properties"]["query"] = "DeviceEvents | take 2"
                elif mutation == "wrong-parameters":
                    resource["properties"]["functionParameters"] = ""
                elif mutation == "bad-name":
                    resource["name"] = "alias-only"
                else:
                    self.template["resources"].pop()
                    self.template["resources"].append({
                        "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates"
                        if mutation == "stored-only" else "Microsoft.Resources/deployments",
                        "properties": {"mainTemplate" if mutation == "stored-only" else "template": {
                            "resources": [resource],
                        }},
                    })
                self.invoke(success=False, unchanged=True)

    def test_implicit_function_calls_cannot_omit_reviewed_prerequisites(self) -> None:
        source = self.source.read_bytes()
        baseline = copy.deepcopy(self.notebook)
        for query in (
            "HiddenParser() | take 1",
            "(HiddenParser()) | count",
            "SourceTable | invoke HiddenParser()",
            "DeviceEvents | join (HiddenParser()) on DeviceId",
            "DeviceEvents | lookup kind=leftouter (HiddenParser()) on DeviceId",
            "union DeviceEvents, (HiddenParser())",
            "let Data = HiddenParser(); Data",
            "let x = (HiddenParser()); x",
            "print toscalar(HiddenParser() | summarize count())",
            "print HiddenParser()",
            "print tostring(HiddenParser())",
            "DeviceEvents | extend x = HiddenParser()",
            "DeviceEvents | where DeviceName == HiddenParser()",
            "DeviceEvents | where DeviceName in (HiddenParser())",
            "print (HiddenParser())",
            "find in (HiddenParser()) where * has 'x'",
            "search in (HiddenParser()) 'x'",
            "find in (HiddenParser) where * has 'x'",
            "search in (HiddenParser) 'x'",
            "HiddenParser | count",
            "(HiddenParser) | count",
            "let x = HiddenParser; x",
            "let x = (HiddenParser); x",
            "let x = materialize(HiddenParser | take 1); x",
            "let x = materialize(HiddenParser); x",
            "DeviceEvents | where DeviceName in (HiddenParser | project DeviceName)",
            "DeviceEvents | where DeviceName in ((HiddenParser) | project DeviceName)",
            "DeviceEvents | where DeviceName in ( ( HiddenParser ) | project DeviceName)",
            "['HiddenParser']() | take 1",
            '["HiddenParser"]() | take 1',
            "[\n'HiddenParser'\n]() | take 1",
            "print ['HiddenParser']()",
            "['HiddenParser'] | take 10",
            "union ['HiddenParser']",
            "union kind=outer ['HiddenParser']",
            "union isfuzzy=true ['HiddenParser']",
            "DeviceEvents | invoke ['HiddenParser']()",
            "DeviceEvents | invoke ['HiddenParser']",
            "table('HiddenParser') | take 10",
            "table('HiddenParser', 'all') | take 10",
            "table('HiddenParser', 'hotcache') | take 10",
            "table('HiddenParser', 'default') | take 10",
            "totable('HiddenParser') | take 10",
            "totable('HiddenParser', 'all') | take 10",
            "table(strcat('Hidden', 'Parser')) | take 10",
            "totable(strcat('Hidden', 'Parser')) | take 10",
            "let local=(){HiddenParser()}; local()",
            "let local=(){HiddenParser}; local()",
            "let local=view(){HiddenParser}; local()",
            "view() { HiddenParser }",
            "DeviceEvents | partition by DeviceId { HiddenParser }",
            "DeviceEvents | fork (HiddenParser)",
            "DeviceEvents | fork (['HiddenParser'])",
            "DeviceEvents | where DeviceName has ['HiddenParser']()",
            "DeviceEvents | where DeviceName !has ['HiddenParser']()",
            "DeviceEvents | where DeviceName contains ['HiddenParser']()",
            "DeviceEvents | where DeviceName !contains ['HiddenParser']()",
            "DeviceEvents | where DeviceName startswith ['HiddenParser']()",
            "DeviceEvents | where DeviceName endswith ['HiddenParser']()",
            "DeviceEvents | where DeviceName has_cs ['HiddenParser']()",
            "DeviceEvents | where DeviceName has['HiddenParser']()",
            "DeviceEvents | where DeviceName !has['HiddenParser']()",
            "DeviceEvents | where DeviceName has['HiddenParser'] ()",
            "DeviceEvents | where DeviceName has['HiddenParser']\n()",
            "DeviceEvents | where DeviceName contains['HiddenParser']()",
            "DeviceEvents | where DeviceName !contains['HiddenParser']()",
            "DeviceEvents | where DeviceName startswith['HiddenParser']()",
            "DeviceEvents | where DeviceName endswith['HiddenParser']()",
            "DeviceEvents | where DeviceName has_cs['HiddenParser']()",
            "DeviceEvents | distinct ['HiddenParser']()",
            "DeviceEvents | distinct['HiddenParser']()",
            "DeviceEvents | mv-expand ['HiddenParser']()",
            "DeviceEvents | mv-expand['HiddenParser']()",
            "print['HiddenParser']()",
            "union['HiddenParser']",
            "union kind=outer['HiddenParser']",
            "union isfuzzy=true['HiddenParser']",
            "DeviceEvents | invoke['HiddenParser']()",
            "DeviceEvents | invoke['HiddenParser']",
            "print bag['HiddenParser']()",
            "DeviceEvents | join hint.strategy=broadcast (HiddenParser) on DeviceId",
            "DeviceEvents | join kind=inner hint.strategy=broadcast (HiddenParser) on DeviceId",
            "DeviceEvents | join hint.strategy=shuffle (['HiddenParser']) on DeviceId",
            "Evil_CL | take 1",
            "union Evil_CL",
            "table('Evil_CL') | take 1",
            "/* HiddenParser() */ | take 1",
            "{QueryParameter} | take 1",
            "{QueryParameter}() | take 1",
            "({QueryParameter} | project DeviceName)",
            "DeviceEvents | where DeviceName in ({QueryParameter} | project DeviceName)",
            "{Hidden Func}() | take 1",
            "({Hidden Func} | project DeviceName)",
            "table({QueryParameter}) | take 1",
        ):
            for side in ("source", "target"):
                with self.subTest(query=query, side=side):
                    self.notebook = copy.deepcopy(baseline)
                    self.source.write_bytes(source)
                    record = self.notebook["contentProvenance"]["conversion"]["queries"][0]
                    if side == "source":
                        document = json.loads(source)
                        document["items"][0]["content"]["query"] = query
                        self.source.write_text(json.dumps(document), encoding="utf-8")
                        self.notebook["contentProvenance"]["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
                        record["sourceSha256"] = hashlib.sha256(query.encode()).hexdigest()
                    else:
                        self.notebook["items"][0]["content"]["query"] = query
                        record["targetSha256"] = hashlib.sha256(query.encode()).hexdigest()
                    self.write()
                    self.invoke(success=False, unchanged=True)
        self.notebook = copy.deepcopy(baseline)
        self.source.write_bytes(source)
        wrapped = json.dumps({"__advancedHuntingSettings": True, "query": "HiddenParser()", "selectedWorkspaceIds": []})
        self.notebook["items"][0]["content"].update({"query": wrapped, "queryType": 18})
        self.notebook["contentProvenance"]["conversion"]["queries"][0]["targetSha256"] = hashlib.sha256(wrapped.encode()).hexdigest()
        self.write()
        self.invoke(success=False, unchanged=True)
        self.notebook = copy.deepcopy(baseline)
        self.source.write_bytes(source)
        self.add_function()
        self.notebook["items"][0]["content"]["query"] = "ReviewedParser() | take 1"
        self.notebook["contentProvenance"]["conversion"]["queries"][0]["targetSha256"] = hashlib.sha256(
            b"ReviewedParser() | take 1",
        ).hexdigest()
        self.write()
        self.assertEqual(1, self.invoke()["count"])

    def test_ordinary_workbooks_allow_absent_or_empty_functions_and_ignore_literals(self) -> None:
        for functions in (None, []):
            with self.subTest(functions=functions):
                if functions is not None:
                    self.notebook["contentProvenance"]["requiredWorkspaceFunctions"] = functions
                self.write()
                result = self.invoke()
                registration = result["template"]["resources"][-1]
                self.assertEqual([], registration["properties"]["contentProvenance"]["requiredWorkspaceFunctions"])
                self.assertEqual(1, len(result["template"]["resources"][-2]["dependsOn"]))
        for query in (
            "print text='HiddenParser()' // HiddenParser()\n",
            "print text=@'HiddenParser()' // /* HiddenParser() */\n",
            "let Local = () { DeviceEvents }; Local()",
            "let LocalTable = DeviceEvents; LocalTable | count",
            "DeviceEvents | where DeviceName in ({QueryParameter}) | take 1",
            "let Watchlist = _GetWatchlist('sample'); Watchlist",
            "_GetWatchlist('sample') | take 1",
            "let Window = ago(1h); DeviceEvents | where Timestamp > Window",
            "DeviceEvents | where (array_length(AdditionalFields) > 0)",
            "DeviceEvents | extend ['Activity Count'] = 1 | project ['Activity Count'], [\"ResolutionTime\"] = 2 | order by ['Activity Count'] desc",
            "DeviceEvents | extend v = todynamic(AdditionalFields)['nested'] | where isnotempty(['Activity Count'])",
            "DeviceEvents | where tostring(AdditionalFields['Leak']) != '' and isnotempty(AdditionalFields['Leak']['nested'])",
            "let LocalView = view() { DeviceEvents }; LocalView()",
            "table('DeviceEvents') | take 1",
            "table('DeviceEvents', 'all') | take 1",
            "totable('DeviceEvents') | take 1",
            "externaldata(Value:string)['https://example.invalid/reference.csv'] with (format='csv')",
        ):
            with self.subTest(query=query):
                self.notebook["items"][0]["content"]["query"] = query
                self.notebook["contentProvenance"]["conversion"]["queries"][0]["targetSha256"] = hashlib.sha256(query.encode()).hexdigest()
                self.write()
                self.assertEqual(1, self.invoke()["count"])

    def test_decoy_functions_cannot_satisfy_hint_flags_or_unsupported_table_indirection(self) -> None:
        source = self.source.read_bytes()
        decoys = ("hint", "broadcast", "__unsupported_table_indirection__", "__unsupported_escaped_call_context__")
        for idx, alias in enumerate(decoys, start=1):
            self.add_function(alias=alias, name=f"synthetic-parser-{idx}")
        baseline = copy.deepcopy(self.notebook)
        for query in (
            "DeviceEvents | join hint.strategy=broadcast (HiddenParser) on DeviceId",
            "DeviceEvents | join kind=inner hint.strategy=broadcast (HiddenParser) on DeviceId",
            "DeviceEvents | join hint.strategy=shuffle (['HiddenParser']) on DeviceId",
            "table(strcat('Hidden', 'Parser')) | take 1",
            "print bag['HiddenParser']()",
            "DeviceEvents | where isnotempty(todynamic(AdditionalFields)['HiddenParser']())",
        ):
            with self.subTest(query=query):
                self.notebook = copy.deepcopy(baseline)
                self.source.write_bytes(source)
                record = self.notebook["contentProvenance"]["conversion"]["queries"][0]
                self.notebook["items"][0]["content"]["query"] = query
                record["targetSha256"] = hashlib.sha256(query.encode()).hexdigest()
                self.write()
                self.invoke(success=False, unchanged=True)

    def test_watchlist_reference_data_cannot_be_a_telemetry_dependency(self) -> None:
        baseline = copy.deepcopy(self.notebook)
        for field in ("requiredWorkloads", "requiredDataConnectors"):
            for data_type in ("Watchlist", "watchlist"):
                with self.subTest(field=field, data_type=data_type):
                    self.notebook = copy.deepcopy(baseline)
                    self.notebook["contentProvenance"][field][0]["dataTypes"].append(data_type)
                    self.write()
                    self.invoke(success=False, unchanged=True)
        self.notebook = copy.deepcopy(baseline)
        query = "let Reference = _GetWatchlist('sample'); DeviceEvents | take 1"
        self.notebook["items"][0]["content"]["query"] = query
        provenance = self.notebook["contentProvenance"]["conversion"]["queries"][0]
        provenance["targetSha256"] = hashlib.sha256(query.encode()).hexdigest()
        provenance["referenceInputs"] = ["Watchlist"]
        self.write()
        self.assertEqual(1, self.invoke()["count"])

    def test_three_records_identity_registration_projection_and_source_preservation(self) -> None:
        authored = {self.source: self.source.read_bytes(), self.target: self.target.read_bytes()}
        for index in (1, 2):
            document = copy.deepcopy(self.notebook)
            for field in ("contentId", "instanceId"):
                document["xdrMetadata"][field] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"fixture/{index}/{field}"))
            path = self.target.with_name(f"workbook-{index}.json")
            path.write_text(json.dumps(document), encoding="utf-8")
            self.data["XDR Workbooks"].append(path.relative_to(self.solution).as_posix())
            authored[path] = path.read_bytes()
        result = self.invoke()
        self.assertEqual(3, result["count"])
        resources = result["template"]["resources"]
        installs = [r for r in resources if r["type"] == "Microsoft.Resources/deployments"]
        registrations = [r for r in resources if r["type"].endswith("/contentTemplates")]
        self.assertEqual(3, len(installs))
        self.assertEqual(3, len(registrations))
        self.assertEqual(3, len({r["name"] for r in installs}))
        criteria = resources[0]["properties"]["dependencies"]["criteria"]
        self.assertEqual(3, len([c for c in criteria if c["kind"] == "DefenderWorkbook"]))
        self.assertEqual("Workbook", criteria[0]["kind"])
        for installation, registration in zip(installs, registrations):
            inner = installation["properties"]["template"]
            stored = registration["properties"]["mainTemplate"]
            self.assertEqual(inner, stored)
            self.assertEqual("inner", installation["properties"]["expressionEvaluationOptions"]["scope"])
            self.assertEqual("2.0", inner["languageVersion"])
            self.assertEqual({"provider": "MicrosoftSecurity", "version": "1.0.0"}, inner["imports"]["MicrosoftSecurity"])
            self.assertEqual("Microsoft.Security/workbooks@2026-06-01-preview", inner["resources"]["workbook"]["type"])
            props = inner["resources"]["workbook"]["properties"]
            self.assertIsInstance(props["content"], dict)
            self.assertEqual("Notebook/1.0", props["content"]["version"])
            self.assertNotIn("xdrMetadata", props["content"])
            provenance = props["content"]["contentProvenance"]
            self.assertEqual({"packageId", "packageVersion", "contentId", "contentVersion"}, set(provenance))
            self.assertEqual("3.2.7", provenance["contentVersion"])
            self.assertNotEqual(props["id"], provenance["contentId"])
            for field in ("packageId", "packageVersion", "contentId"):
                self.assertEqual(provenance[field], registration["properties"][field])
            self.assertEqual(provenance["contentVersion"], registration["properties"]["version"])
            full = registration["properties"]["contentProvenance"]
            self.assertEqual(self.notebook["contentProvenance"]["requiredWorkloads"], full["requiredWorkloads"])
            self.assertEqual(self.notebook["contentProvenance"]["requiredDataConnectors"], full["requiredDataConnectors"])
            self.assertNotIn("source", full)
            self.assertNotIn("variables(", json.dumps(provenance))
            self.assertEqual("[parameters('DeployDefenderWorkbook')]", installation["condition"])
            self.assertEqual(installation["condition"], registration["condition"])
            self.assertEqual("DefenderWorkbook", registration["properties"]["contentKind"])
            self.assertEqual("2023-04-01-preview", registration["apiVersion"])
            self.assertIn(installation["name"], registration["dependsOn"][0])
        for path, original in authored.items():
            self.assertEqual(original, path.read_bytes())
        self.assertIn("**XDR Workbooks:** 3", result["ui"]["parameters"]["config"]["basics"]["description"])

    def test_flags_ui_test_parameter_defaults_and_native_route_are_independent(self) -> None:
        result = self.invoke()
        parameters = result["template"]["parameters"]
        self.assertTrue(parameters["DeployWorkbook"]["defaultValue"])
        self.assertFalse(parameters["DeployDefenderWorkbook"]["defaultValue"])
        self.assertNotIn("DeployCustomDetection", parameters)
        outputs = result["ui"]["parameters"]["outputs"]
        self.assertEqual("[steps('contentSelection').DeployDefenderWorkbook]", outputs["DeployDefenderWorkbook"])
        elements = result["ui"]["parameters"]["steps"][0]["elements"]
        self.assertFalse(next(e for e in elements if e["name"] == "DeployDefenderWorkbook")["defaultValue"])
        native = result["template"]["resources"][1]
        condition = native.pop("condition")
        original = copy.deepcopy(self.native)
        original.pop("condition")
        self.assertEqual(original, native)
        self.assertEqual("[and(parameters('DeployWorkbook'), equals('native','native'))]", condition)
        self.assertNotIn("DeployWorkbook", json.dumps(result["template"]["resources"][2:]))

    def test_generate_package_writes_independent_test_parameters_and_zip(self) -> None:
        original = self.target.read_bytes()
        result = self.invoke(package=True)
        package = self.solution / "Package"
        parameters = json.loads((package / "testParameters.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(result["template"]["parameters"], parameters)
        self.assertTrue(parameters["DeployWorkbook"]["defaultValue"])
        self.assertFalse(parameters["DeployDefenderWorkbook"]["defaultValue"])
        with zipfile.ZipFile(package / "3.2.7.zip") as archive:
            template = json.loads(archive.read("mainTemplate.json"))
            ui = json.loads(archive.read("createUiDefinition.json"))
        self.assertEqual(5, len(template["resources"]))
        marker = next(r for r in template["resources"] if r.get("name") == "pid-workbook-regression")
        self.assertNotIn("condition", marker)
        self.assertEqual([], marker["properties"]["template"]["resources"])
        self.assertEqual("[steps('contentSelection').DeployDefenderWorkbook]", ui["parameters"]["outputs"]["DeployDefenderWorkbook"])
        self.assertEqual(original, self.target.read_bytes())
        self.assertIn("**XDR Workbooks:** 1", ui["parameters"]["config"]["basics"]["description"])

    def test_workbook_only_missing_attribution_cannot_skip_lookup(self) -> None:
        result = self.invoke(package=True, success=False, tracking_id=None)
        self.assertIn("Required published lookup failed", result["error"])
        self.assertIn("catalog identity", result["error"])
        self.assertFalse((self.solution / "Package").exists())
        self.assertEqual({"trackingId": None},
                         json.loads((self.solution / "SolutionMetadata.json").read_text()))

    def test_empty_selection_never_scans_or_emits_flag(self) -> None:
        self.data["XDR Workbooks"] = []
        result = self.invoke()
        self.assertEqual(0, result["count"])
        self.assertNotIn("DeployDefenderWorkbook", result["template"]["parameters"])
        self.assertEqual(2, len(result["template"]["resources"]))

    def test_existing_files_require_selection_and_selection_must_be_array(self) -> None:
        for value in (None, "[]", {}, [7], [None]):
            with self.subTest(value=value):
                if value is None:
                    self.data.pop("XDR Workbooks", None)
                else:
                    self.data["XDR Workbooks"] = value
                self.invoke(success=False)

    def test_no_workbook_directory_does_not_add_selection(self) -> None:
        shutil.rmtree(self.solution / "XDR Workbooks")
        self.data.pop("XDR Workbooks")
        result = self.invoke()
        self.assertEqual(0, result["count"])
        self.assertNotIn("DeployDefenderWorkbook", result["template"]["parameters"])

    def test_version_bounds_and_package_boundary(self) -> None:
        for version in ("3.0.9", "4.0.0", "Notebook/1.0", "3.1", "03.1.0", "3.01.0"):
            with self.subTest(version=version):
                self.notebook["xdrMetadata"]["version"] = version
                self.write()
                self.invoke(success=False)
        self.notebook["xdrMetadata"]["version"] = "3.1.0"
        self.write()
        self.template["variables"]["_solutionVersion"] = "4.0.0"
        self.invoke(success=False)
        self.template["variables"]["_solutionVersion"] = "3.2.6"
        self.invoke(success=False)

    def test_source_passthrough_validates_all_dependencies_and_handles_empty_arrays(self) -> None:
        baseline = copy.deepcopy(self.notebook)
        cases = (
            ({}, True),
            ({"requiredWorkloads": [], "requiredDataConnectors": []}, True),
            ({"requiredDataConnectors": "[]"}, False),
            ({"requiredWorkloads": [
                {"workload": "mde", "dataTypes": ["DeviceEvents"]},
                {"workload": "unknown", "dataTypes": []},
            ]}, False),
        )
        for changes, success in cases:
            with self.subTest(changes=changes):
                self.notebook = copy.deepcopy(baseline)
                self.notebook["contentProvenance"].update(changes)
                self.write()
                result = subprocess.run([
                    "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
                    "$ErrorActionPreference='Stop'; "
                    f". {literal(COMMON)}; "
                    f"$doc=Get-Content -Raw -LiteralPath {literal(self.target)} | ConvertFrom-Json; "
                    "$source=Assert-DefenderWorkbookDocument -Document $doc "
                    f"-SolutionRoot {literal(self.solution)} -SolutionName Sample "
                    "-ContentPath 'fixture' -PassThruSource; "
                    "ConvertTo-Json -InputObject $source -Depth 100 -Compress",
                ], capture_output=True, text=True, check=False)
                self.assertEqual(success, result.returncode == 0, result.stderr)
                if success:
                    self.assertEqual(json.loads(self.source.read_bytes()), json.loads(result.stdout))

    def test_review_missing_arrays_unknown_workload_and_stale_source_block(self) -> None:
        baseline = copy.deepcopy(self.notebook)
        mutations = [
            ("conversion", "reviewRequired", True), ("conversion", "reviewRequired", None),
            ("conversion", "tool", ""), ("conversion", "version", None),
            (None, "dependencyReviewRequired", True), (None, "dependencyReviewRequired", None),
            (None, "requiredWorkloads", None), (None, "requiredDataConnectors", "[]"),
            (None, "requiredWorkloads", [{"workload": "unknown", "dataTypes": []}]),
            (None, "requiredDataConnectors", [{"connectorId": "Connector", "dataTypes": [7]}]),
            ("source", "sha256", "a" * 64), ("source", "path", "../outside.json"),
        ]
        for section, field, value in mutations:
            with self.subTest(field=field, value=value):
                self.notebook = copy.deepcopy(baseline)
                container = self.notebook["contentProvenance"]
                if section:
                    container = container[section]
                container[field] = value
                self.write()
                self.invoke(success=False)

    def test_selection_paths_duplicates_and_symlinks_fail_closed(self) -> None:
        for selection in (
            [self.reference, self.reference],
            [self.reference, f"Solutions/Sample/{self.reference}"],
            ["../outside.json"], ["Workbooks/nested/source.json"],
            ["/absolute.json"], ["XDR Workbooks/../Workbooks/nested/source.json"],
        ):
            with self.subTest(selection=selection):
                self.data["XDR Workbooks"] = selection
                self.invoke(success=False)
        link = self.target.with_name("link.json")
        link.symlink_to(self.target)
        self.data["XDR Workbooks"] = [link.relative_to(self.solution).as_posix()]
        self.invoke(success=False)
        link.unlink()
        source_link = self.source.with_name("link.json")
        source_link.symlink_to(self.source)
        self.notebook["contentProvenance"]["source"]["path"] = "Workbooks/nested/link.json"
        self.write()
        self.data["XDR Workbooks"] = [self.reference]
        self.invoke(success=False)

    def test_colliding_authored_identities_are_not_rewritten(self) -> None:
        self.notebook["xdrMetadata"]["instanceId"] = self.notebook["xdrMetadata"]["contentId"]
        self.write()
        self.invoke(success=False)
        self.notebook["xdrMetadata"]["instanceId"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "fixture/other"))
        self.write()
        other = self.target.with_name("other.json")
        other.write_bytes(self.target.read_bytes())
        self.data["XDR Workbooks"].append(other.relative_to(self.solution).as_posix())
        self.invoke(success=False)

    def test_arm_looking_strings_escape_only_deployment_copies(self) -> None:
        self.notebook["xdrMetadata"]["displayName"] = "[authored title]"
        self.notebook["items"].append({"type": 1, "content": {"json": ["[literal]", None, True, 42]}})
        self.write()
        original = self.target.read_bytes()
        result = self.invoke()
        installation = result["template"]["resources"][2]
        properties = installation["properties"]["template"]["resources"]["workbook"]["properties"]
        self.assertEqual("[[authored title]", properties["name"])
        self.assertEqual("[[parameters('authored-literal')]", properties["content"]["items"][1]["content"]["json"])
        self.assertEqual("[[[already-bracketed]", properties["content"]["fallbackResourceIds"][0])
        self.assertEqual(["[[literal]", None, True, 42], properties["content"]["items"][2]["content"]["json"])
        self.assertEqual(original, self.target.read_bytes())
        self.assertEqual("[[authored title]", result["template"]["resources"][3]["properties"]["displayName"])

    def test_query_current_hash_blockers_and_pruned_scope_record(self) -> None:
        baseline = copy.deepcopy(self.notebook)
        for mutation in ("stale", "blocked", "missing-pointer", "missing-array"):
            with self.subTest(mutation=mutation):
                self.notebook = copy.deepcopy(baseline)
                conversion = self.notebook["contentProvenance"]["conversion"]
                if mutation == "missing-array":
                    conversion.pop("queries")
                elif mutation == "stale":
                    self.notebook["items"][0]["content"]["query"] += " "
                elif mutation == "blocked":
                    conversion["queries"][0]["status"] = "needs-review"
                else:
                    conversion["queries"][0]["outputPath"] = "/items/99/query"
                self.write()
                self.invoke(success=False)
        self.notebook = copy.deepcopy(baseline)
        self.scope_fixture()
        self.write()
        self.assertEqual(1, self.invoke()["count"])

    def test_no_query_notebook_keeps_complete_layout(self) -> None:
        self.notebook["items"] = [{"type": 1, "name": "text-only", "content": {"json": "fixture text"}}]
        self.notebook["contentProvenance"]["conversion"]["queries"] = []
        self.notebook["contentProvenance"]["requiredWorkloads"] = []
        self.notebook["contentProvenance"]["requiredDataConnectors"] = []
        self.source.write_text(json.dumps({"version": "Notebook/1.0", "items": []}), encoding="utf-8")
        self.notebook["contentProvenance"]["source"]["sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.write()
        result = self.invoke()
        content = result["template"]["resources"][2]["properties"]["template"]["resources"]["workbook"]["properties"]["content"]
        self.assertEqual(self.notebook["items"], content["items"])

    def test_nested_notebook_layout_is_not_serialized_to_truncated_text(self) -> None:
        nested = {"leaf": "[literal]"}
        for _ in range(60):
            nested = {"child": nested}
        self.notebook["items"][1]["content"]["layout"] = nested
        self.write()
        result = self.invoke(package=True)
        packaged = json.loads((self.solution / "Package/mainTemplate.json").read_text(encoding="utf-8-sig"))
        content = packaged["resources"][2]["properties"]["template"]["resources"]["workbook"]["properties"]["content"]
        value = content["items"][1]["content"]["layout"]
        for _ in range(60):
            self.assertIsInstance(value, dict)
            value = value["child"]
        self.assertEqual({"leaf": "[[literal]"}, value)
        self.assertEqual(1, result["count"])
        for _ in range(30):
            nested = {"child": nested}
        self.notebook["items"][1]["content"]["layout"] = nested
        self.write()
        self.invoke(success=False)

    def test_v3_entrypoint_method_forwarding_preserves_legacy_default(self) -> None:
        toolkit = self.root / "Tools/Create-Azure-Sentinel-Solution"
        (toolkit / "V3").mkdir(parents=True)
        (toolkit / "common").mkdir()
        (toolkit / "common/createSolutionLocal.ps1").write_text(
            "param($SolutionDataFolderPath,$VersionMode,$VersionBump,$TargetVersion,"
            "$EntryPointName,$DefaultInputPath,$ToolkitRootPath,$IncludeXdrDetections,"
            "$EnforceV31Versions,[switch]$SkipAttributionLookup,"
            "[ValidateSet('arm-ttk','lab-deployment')]$ArmValidationMethod='arm-ttk')\n"
            "[pscustomobject]@{method=$ArmValidationMethod;entry=$EntryPointName;"
            "xdr=$IncludeXdrDetections} | ConvertTo-Json -Compress\n",
            encoding="utf-8",
        )
        for entry, method in (("createSolutionV3_1.ps1", None), ("createSolutionV3_1.ps1", "lab-deployment")):
            with self.subTest(entry=entry, method=method):
                destination = toolkit / "V3" / entry
                shutil.copy2(ROOT / "Tools/Create-Azure-Sentinel-Solution/V3" / entry, destination)
                arguments = ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
                             str(destination), "-SolutionDataFolderPath", "fixture"]
                if method:
                    arguments += ["-ArmValidationMethod", method]
                result = subprocess.run(arguments, capture_output=True, text=True, check=False)
                self.assertEqual(0, result.returncode, result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(method or "arm-ttk", record["method"])
                self.assertEqual(entry == "createSolutionV3_1.ps1", record["xdr"] is True)
        legacy = (ROOT / "Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1").read_text()
        self.assertIn('RunArmTtkOnPackage -solutionName $solutionName -isPipelineRun $false', legacy)


if __name__ == "__main__":
    unittest.main()
