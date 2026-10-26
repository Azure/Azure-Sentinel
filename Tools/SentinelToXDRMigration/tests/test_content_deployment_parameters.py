from __future__ import annotations

import copy
import itertools
import json
import shutil
import unittest
import zipfile

import test_customer_usage_attribution as attribution
from sentinel_xdr_migration.packaging import _deployment_parameters


CONTRACT = json.loads(
    (attribution.PACKAGER / "common/contentDeploymentParameters.json").read_text()
)
FIVE = (
    "DeployAnalyticsRule", "DeployPlaybook", "DeployWorkbook",
    "DeployDataConnector", "DeployCustomDetection",
)
PREFIX = "Microsoft.OperationalInsights/workspaces/providers/"


class ContentDeploymentDescriptionTests(unittest.TestCase):
    def test_sentinel_content_descriptions_use_microsoft_branding(self):
        expected = {
            "DeployAnalyticsRule": (
                "Deploy the Microsoft Sentinel analytic rules carried by this solution "
                "(ContentKind AnalyticsRule and its AnalyticsRuleTemplate registration face)."
            ),
            "DeployWorkbook": (
                "Deploy the Microsoft Sentinel workbook content and its Content Hub registration "
                "carried by this solution (ContentKind Workbook and WorkbookTemplate)."
            ),
            "DeployHuntingQuery": "Deploy the Microsoft Sentinel hunting queries carried by this solution.",
            "DeployInvestigationQuery": (
                "Deploy the Microsoft Sentinel investigation queries carried by this solution."
            ),
            "DeployAutomationRule": "Deploy the Microsoft Sentinel automation rules carried by this solution.",
        }
        self.assertEqual(
            expected,
            {name: CONTRACT[name]["description"] for name in expected},
        )


def registration(kind, name):
    return {
        "type": PREFIX + "contentTemplates", "apiVersion": "2023-04-01-preview",
        "name": name, "dependsOn": ["package"],
        "properties": {"contentKind": kind, "mainTemplate": {
            "parameters": {"innerOnly": {"type": "bool", "defaultValue": True}},
            "variables": {"query": "print Test = 1"},
            "resources": [{"name": "inner", "type": "Synthetic/content",
                           "condition": "[parameters('innerOnly')]", "properties": {"id": name}}],
        }},
    }


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class ContentDeploymentTests(unittest.TestCase):
    setUp = attribution.AttributionTests.setUp
    run_ps = attribution.AttributionTests.run_ps
    prepare_integration = attribution.AttributionTests.prepare_integration
    package = attribution.AttributionTests.package
    write_metadata = attribution.AttributionTests.write_metadata

    def apply_contract(self, template):
        source = self.repository / "selection-input.json"
        source.write_text(json.dumps(template))
        result = self.run_ps(
            f". {attribution.ps_literal(attribution.PACKAGER / 'common/contentDeploymentParameters.ps1')}; "
            f"$template = Get-Content -Raw {attribution.ps_literal(source)} | ConvertFrom-Json; "
            "$ui = [pscustomobject]@{parameters=[pscustomobject]@{steps=@();outputs=[pscustomobject]@{}}}; "
            "Add-SolutionContentDeploymentParameters -Template $template -UiDefinition $ui; "
            "@{template=$template;ui=$ui} | ConvertTo-Json -Depth 100"
        )
        return result

    def test_five_parameter_matrix_preserves_every_resource_and_scope(self):
        families = {}
        for parameter in FIVE:
            for kind in CONTRACT[parameter]["kinds"]:
                families[kind] = parameter
        resources = [registration(kind, kind) for kind in families]
        for suffix in ("dataConnectors", "dataConnectorDefinitions"):
            resources.append({"type": PREFIX + suffix, "name": suffix, "properties": {}})
            families[suffix] = "DeployDataConnector"
        resources.append({
            "type": PREFIX + "metadata", "name": "connector-metadata",
            "dependsOn": ["dataConnectors"],
            "properties": {"kind": "DataConnector", "parentId": "dataConnectors"},
        })
        families["connector-metadata"] = "DeployDataConnector"
        install = {
            "name": "cd-install", "type": "Microsoft.Resources/deployments",
            "dependsOn": ["package"], "properties": {
                "mode": "Incremental", "expressionEvaluationOptions": {"scope": "inner"},
                "template": {"languageVersion": "2.0",
                             "imports": {"MicrosoftSecurity": {"provider": "MicrosoftSecurity", "version": "1.0.0"}},
                             "resources": {"detectionRule": {
                                 "import": "MicrosoftSecurity", "type": "Microsoft.Security/detectionRules@2025-06-01",
                                 "properties": {"id": "11111111-2222-3333-4444-555555555555",
                                                "status": "disabled", "queryCondition": {"queryText": "print Test=1"}},
                             }}},
            },
        }
        resources.append(install)
        families["cd-install"] = "DeployCustomDetection"
        package = {"name": "package", "type": PREFIX + "contentPackages",
                   "properties": {"contentKind": "Solution", "dependencies": {
                       "operator": "AND", "criteria": [{"kind": "AnalyticsRule", "contentId": "id"}],
                   }}}
        resources.append(package)
        original = {"parameters": {"workspace": {"type": "string"}},
                    "variables": {"sentinel": {"id": "untouched"}, "array": [1, 2]},
                    "resources": resources}
        result = self.apply_contract(original)
        self.assertEqual(0, result.returncode, result.stderr)
        output = json.loads(result.stdout)
        generated = output["template"]
        self.assertEqual(original["variables"], generated["variables"])
        self.assertEqual(set(FIVE), set(generated["parameters"]) - {"workspace"})
        self.assertEqual(
            {name: CONTRACT[name]["defaultValue"] for name in FIVE},
            _deployment_parameters(generated, output["ui"], generated["parameters"], has_xdr=True),
        )
        for before, after in zip(resources, generated["resources"], strict=True):
            body = copy.deepcopy(after)
            if before["name"] in families:
                self.assertEqual(f"[parameters('{families[before['name']]}')]", body.pop("condition"))
            self.assertEqual(before, body)

        # Exhaustive ARM boolean selection truth table, comparing resource identities,
        # not counts. Nested stored content is never evaluated in the outer scope.
        for flags in itertools.product((False, True), repeat=5):
            values = dict(zip(FIVE, flags, strict=True))
            expected = {"package"} | {name for name, family in families.items() if values[family]}
            actual = {
                resource["name"] for resource in generated["resources"]
                if "condition" not in resource or values[resource["condition"][13:-3]]
            }
            self.assertEqual(expected, actual, values)
            self.assertEqual(values["DeployAnalyticsRule"], "AnalyticsRule" in actual)
            self.assertEqual(values["DeployCustomDetection"], "cd-install" in actual)
            self.assertEqual("CustomDetection" in actual, "cd-install" in actual)

    def test_existing_conditions_and_child_scope_are_composed_not_replaced(self):
        resources = []
        for index, condition in enumerate((
            True, False, "[equals(parameters('existing'), 'a[b]')]",
        )):
            item = registration("Playbook", str(index))
            item["condition"] = condition
            item["resources"] = [{"name": "child", "type": "child",
                                  "condition": "[parameters('existing')]"}]
            resources.append(item)
        result = self.apply_contract({
            "parameters": {"existing": {"type": "bool", "defaultValue": True}},
            "variables": {}, "resources": resources,
        })
        self.assertEqual(0, result.returncode, result.stderr)
        generated = json.loads(result.stdout)["template"]["resources"]
        for before, after, expression in zip(
            resources, generated, ("true()", "false()", "equals(parameters('existing'), 'a[b]')"), strict=True,
        ):
            self.assertEqual(f"[and(parameters('DeployPlaybook'), {expression})]", after["condition"])
            self.assertEqual("[and(parameters('DeployPlaybook'), parameters('existing'))]",
                             after["resources"][0]["condition"])
            self.assertEqual(before["properties"], after["properties"])

    def test_vocabulary_subsets_and_unclassified_resources_fail_specifically(self):
        resources = [registration(kind, kind)
                     for entry in CONTRACT.values() for kind in entry["kinds"]]
        result = self.apply_contract({"parameters": {}, "variables": {}, "resources": resources})
        self.assertEqual(0, result.returncode, result.stderr)
        template = json.loads(result.stdout)["template"]
        self.assertEqual(set(CONTRACT), set(template["parameters"]))
        self.assertIs(False, template["parameters"]["DeployDefenderWorkbook"]["defaultValue"])
        workbook = next(
            resource for resource in template["resources"]
            if resource["name"] == "DefenderWorkbook"
        )
        self.assertEqual(
            "[parameters('DeployDefenderWorkbook')]", workbook["condition"]
        )
        for resource in (
            registration("FutureKind", "future-kind"),
            {"type": "Microsoft.Resources/deployments", "name": "unowned-deployment", "properties": {}},
        ):
            result = self.apply_contract({"parameters": {}, "resources": [resource]})
            self.assertNotEqual(0, result.returncode)
            self.assertIn(resource["name"], result.stderr)
            self.assertIn("Unclassified V3.1", result.stderr)

    def test_real_entry_points_defaults_registration_and_legacy_isolation(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        original = json.loads(self.data.read_text())
        for configured in (attribution.ABSENT, False, True):
            data = dict(original)
            if configured is not attribution.ABSENT:
                data["Include XDR Content Registration"] = configured
            self.data.write_text(json.dumps(data))
            for pipeline in (False, True):
                with self.subTest(configured=configured, pipeline=pipeline):
                    result = self.package(entry, pipeline)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn("live provider registration support remains unverified", result.stdout)
                    if configured is not attribution.ABSENT:
                        self.assertIn("deprecated and ignored", result.stdout)
                    package = self.solution / "Package"
                    template, ui, parameters = [
                        json.loads((package / name).read_text(encoding="utf-8-sig"))
                        for name in ("mainTemplate.json", "createUiDefinition.json", "testParameters.json")
                    ]
                    self.assertEqual(
                        {"DeployAnalyticsRule": True, "DeployCustomDetection": False},
                        _deployment_parameters(template, ui, parameters, has_xdr=True),
                    )
                    self.assertNotIn("E5Flavor", json.dumps(template))
                    self.assertNotIn("RegisterE5Content", json.dumps(template))
                    installed = next(r for r in template["resources"]
                                     if r["type"] == "Microsoft.Resources/deployments"
                                     and r["name"] != attribution.TRACKING_ID)
                    registered = next(r for r in template["resources"]
                                      if r.get("properties", {}).get("contentKind") == "CustomDetection")
                    self.assertEqual(installed["condition"], registered["condition"])
                    self.assertIn(f"[resourceId('Microsoft.Resources/deployments', '{installed['name']}')]",
                                  registered["dependsOn"])
                    self.assertFalse(any(registered["name"] in dep for dep in installed["dependsOn"]))
                    for body in (installed["properties"]["template"], registered["properties"]["mainTemplate"]):
                        self.assertEqual("2.0", body["languageVersion"])
                        self.assertEqual("1.0.0", body["imports"]["MicrosoftSecurity"]["version"])
                        self.assertEqual("disabled", body["resources"]["detectionRule"]["properties"]["status"])
                        self.assertNotIn("Deploy", json.dumps(body))
                    self.assertIn(attribution.AttributionTests.marker(attribution.TRACKING_ID), template["resources"])
                    with zipfile.ZipFile(package / "3.2.2.zip") as archive:
                        self.assertEqual(template, json.loads(archive.read("mainTemplate.json")))
                        self.assertEqual(ui, json.loads(archive.read("createUiDefinition.json")))
        original["XDR Detections"] = []
        self.data.write_text(json.dumps(original))
        for pipeline in (False, True):
            result = self.package(entry, pipeline)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
            self.assertIn("DeployAnalyticsRule", template["parameters"])
            self.assertNotIn("DeployCustomDetection", template["parameters"])
        legacy = entry.with_name("legacy.ps1")
        shutil.copyfile(attribution.PACKAGER / "V3/createSolutionV3.ps1", legacy)
        result = self.package(legacy, False, version_bump="patch")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
        self.assertFalse(set(CONTRACT) & template["parameters"].keys())
        self.assertTrue(all("condition" not in r for r in template["resources"]))

    def test_custom_detection_dependencies_use_registration_identity_and_version(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        data = json.loads(self.data.read_text())
        source_rule = json.loads(
            (self.solution / "Analytic Rules/Test.yaml").read_text().split("\n", 1)[1]
        )
        source_detection = json.loads(
            (self.solution / "XDR Detections/Test.yaml").read_text().split("\n", 1)[1]
        )
        identities = [
            ("11111111-2222-3333-4444-555555555555", "3.1.0", "Test"),
            ("22222222-2222-3333-4444-555555555555", "3.1.1", "Second"),
            ("33333333-2222-3333-4444-555555555555", "3.1.2", "Third"),
        ]
        analytic_paths = []
        detection_paths = []
        for content_id, version, stem in identities:
            rule = copy.deepcopy(source_rule)
            rule.update(id=content_id, name=f"{stem} rule")
            rule_path = self.solution / f"Analytic Rules/{stem}.yaml"
            rule_path.write_text("---\n" + json.dumps(rule))
            analytic_paths.append(str(rule_path.relative_to(self.solution)))

            detection = copy.deepcopy(source_detection)
            detection["version"] = version
            detection["contentProvenance"]["source"]["id"] = content_id
            detection["properties"]["id"] = content_id
            detection["properties"]["displayName"] = f"{stem} detection"
            detection_path = self.solution / f"XDR Detections/{stem}.yaml"
            detection_path.write_text("---\n" + json.dumps(detection))
            detection_paths.append(str(detection_path.relative_to(self.solution)))

        data["Analytic Rules"] = analytic_paths
        data["XDR Detections"] = []
        self.data.write_text(json.dumps(data))
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        sentinel_only = json.loads(
            (self.solution / "Package/mainTemplate.json").read_text(encoding="utf-8-sig")
        )
        package = next(
            resource for resource in sentinel_only["resources"]
            if resource["type"].endswith("/contentPackages")
        )
        sentinel_dependencies = package["properties"]["dependencies"]
        self.assertEqual("AND", sentinel_dependencies["operator"])
        self.assertFalse(any(
            criterion["kind"] == "CustomDetection"
            for criterion in sentinel_dependencies["criteria"]
        ))

        data["XDR Detections"] = detection_paths
        self.data.write_text(json.dumps(data))
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        hybrid = json.loads(
            (self.solution / "Package/mainTemplate.json").read_text(encoding="utf-8-sig")
        )
        package = next(
            resource for resource in hybrid["resources"]
            if resource["type"].endswith("/contentPackages")
        )
        dependencies = package["properties"]["dependencies"]
        registrations = [
            resource for resource in hybrid["resources"]
            if resource.get("properties", {}).get("contentKind") == "CustomDetection"
        ]
        custom_detection_criteria = [
            criterion for criterion in dependencies["criteria"]
            if criterion["kind"] == "CustomDetection"
        ]
        self.assertEqual("AND", dependencies["operator"])
        self.assertEqual(
            sentinel_dependencies["criteria"],
            dependencies["criteria"][:-len(custom_detection_criteria)],
        )
        self.assertEqual(3, len(custom_detection_criteria))
        self.assertEqual(
            [
                {
                    "kind": "CustomDetection",
                    "contentId": registration["properties"]["contentId"],
                    "version": registration["properties"]["version"],
                }
                for registration in registrations
            ],
            custom_detection_criteria,
        )
        self.assertEqual(
            [(f"xdr-{content_id}", version) for content_id, version, _ in identities],
            [(item["contentId"], item["version"]) for item in custom_detection_criteria],
        )

        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        regenerated = json.loads(
            (self.solution / "Package/mainTemplate.json").read_text(encoding="utf-8-sig")
        )
        regenerated_package = next(
            resource for resource in regenerated["resources"]
            if resource["type"].endswith("/contentPackages")
        )
        self.assertEqual(
            dependencies["criteria"],
            regenerated_package["properties"]["dependencies"]["criteria"],
        )

    def test_python_rejects_legacy_stale_or_unsupported_selections(self):
        template = {"parameters": {"DeployAnalyticsRule": {"type": "bool", "defaultValue": True}}}
        ui = {"parameters": {"outputs": {"DeployAnalyticsRule": "[steps('contentSelection').DeployAnalyticsRule]"},
                             "steps": [{"name": "contentSelection", "elements": [{
                                 "name": "DeployAnalyticsRule", "type": "Microsoft.Common.CheckBox", "defaultValue": True,
                             }]}]}}
        self.assertEqual({"DeployAnalyticsRule": True},
                         _deployment_parameters(template, ui, template["parameters"], has_xdr=False))
        with self.assertRaisesRegex(RuntimeError, "testParameters"):
            _deployment_parameters(template, ui, {}, has_xdr=False)
        with self.assertRaisesRegex(RuntimeError, "UI selections"):
            _deployment_parameters(template, {}, template["parameters"], has_xdr=False)
        template["parameters"]["E5Flavor"] = {"type": "bool", "defaultValue": False}
        with self.assertRaisesRegex(RuntimeError, "obsolete"):
            _deployment_parameters(template, ui, template["parameters"], has_xdr=False)

    def test_real_mixed_emitters_share_only_the_applicable_five_controls(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        data = json.loads(self.data.read_text())
        fixtures = {
            "Workbooks/Test.json": {"version": "Notebook/1.0", "items": [], "styleSettings": {}},
            "Workbooks/WorkbooksMetadata.json": [{
                "templateRelativePath": "Test.json", "workbookKey": "Test",
                "title": "Test", "description": "Test workbook", "version": "1.0.0",
                "dataTypesDependencies": [], "dataConnectorsDependencies": [],
            }],
            "Data Connectors/Test.json": {
                "id": "TestConnector", "title": "Test connector", "publisher": "Test",
                "descriptionMarkdown": "Test connector", "graphQueries": [], "dataTypes": [],
                "connectivityCriterias": [], "sampleQueries": [], "availability": {"isPreview": False},
                "permissions": {"resourceProvider": []}, "instructionSteps": [],
            },
        }
        for name, resource_type in (
            ("Workflow", "Microsoft.Logic/workflows"),
            ("Connector", "Microsoft.Web/customApis"),
            ("Function", "Microsoft.Web/sites"),
        ):
            fixtures[f"Playbooks/{name}/azuredeploy.json"] = {
                "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0",
                "metadata": {"title": name, "description": "Test"},
                "parameters": {
                    "FunctionAppName": {"type": "string", "defaultValue": "TestFunction"},
                    "ConnectorName": {"type": "string", "defaultValue": "TestConnector"},
                },
                "variables": {},
                "resources": [{
                    "type": resource_type,
                    "name": "[parameters('ConnectorName')]" if name == "Connector" else name,
                    "apiVersion": "2019-05-01",
                    "location": "[resourceGroup().location]", "tags": {"hidden-SentinelTemplateVersion": "1.0.0"},
                    "properties": {"definition": {"triggers": {}, "actions": {}}},
                }],
            }
        for relative, document in fixtures.items():
            path = self.solution / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(document))
        # The existing workbook emitter reads metadata relative to repositoryBasePath.
        # Supply that fixture too; this parameter-only change does not alter path resolution.
        workbook_metadata = self.repository / "Workbooks/WorkbooksMetadata.json"
        workbook_metadata.parent.mkdir()
        workbook_metadata.write_text(json.dumps(fixtures["Workbooks/WorkbooksMetadata.json"]))
        data.update({
            "Workbooks": ["Workbooks/Test.json"], "Data Connectors": ["Data Connectors/Test.json"],
            "Playbooks": [name for name in fixtures if name.startswith("Playbooks/")],
        })
        self.data.write_text(json.dumps(data))
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                result = self.package(entry, pipeline)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                package = self.solution / "Package"
                template, ui, parameters = [
                    json.loads((package / name).read_text(encoding="utf-8-sig"))
                    for name in ("mainTemplate.json", "createUiDefinition.json", "testParameters.json")
                ]
                self.assertEqual(
                    {name: CONTRACT[name]["defaultValue"] for name in FIVE},
                    _deployment_parameters(template, ui, parameters, has_xdr=True),
                )
                for resource in template["resources"]:
                    kind = resource.get("properties", {}).get("contentKind")
                    if kind in ("Playbook", "LogicAppsCustomConnector", "AzureFunction"):
                        self.assertEqual("[parameters('DeployPlaybook')]", resource["condition"])
                    if resource["type"] in (PREFIX + "dataConnectors", PREFIX + "metadata"):
                        self.assertEqual("[parameters('DeployDataConnector')]", resource["condition"])
                self.assertEqual(
                    {"Playbook", "LogicAppsCustomConnector", "AzureFunction"},
                    {r.get("properties", {}).get("contentKind") for r in template["resources"]
                     if r.get("condition") == "[parameters('DeployPlaybook')]"},
                )

    def test_first_authored_tactic_only_in_both_arm_copies_without_source_mutation(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        path = self.solution / "XDR Detections/Test.yaml"
        document = json.loads(path.read_text().removeprefix("---\n"))
        document["properties"]["detectionAction"]["alertTemplate"]["customDetails"] = {
            "AdditionalEvidence": "Test",
        }
        tactics = [
            {"tactic": "Execution", "techniques": [
                {"technique": "T1059", "subTechniques": ["T1059.003", "T1059.001"]},
                {"technique": "T1047"},
            ]},
            {"tactic": "Persistence", "techniques": [{"technique": "T1547", "subTechniques": ["T1547.001"]}]},
            {"tactic": "Discovery", "techniques": [{"technique": "T1082"}]},
        ]
        for authored in (tactics[:1], tactics[:2], tactics, list(reversed(tactics))):
            document["properties"]["detectionAction"]["alertTemplate"]["tactics"] = authored
            document["contentProvenance"]["originalTactics"] = copy.deepcopy(authored)
            path.write_text("---\n" + json.dumps(document))
            original = {p: p.read_bytes() for p in (
                path, self.solution / "Analytic Rules/Test.yaml", self.data, self.metadata,
            )}
            for pipeline in (False, True):
                with self.subTest(authored=authored, pipeline=pipeline):
                    result = self.package(entry, pipeline)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    if len(authored) > 1:
                        self.assertIn(f"first authored tactic '{authored[0]['tactic']}'", result.stdout)
                        self.assertIn("omitted tactics: " + ", ".join(t["tactic"] for t in authored[1:]),
                                      result.stdout)
                        self.assertIn("not a recommended classification", result.stdout)
                    else:
                        self.assertNotIn("V3.1 TACTIC SELECTION:", result.stdout)
                    template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                    bodies = []
                    for resource in template["resources"]:
                        if resource["type"] == "Microsoft.Resources/deployments" and resource.get("condition"):
                            bodies.append(resource["properties"]["template"])
                        elif resource.get("properties", {}).get("contentKind") == "CustomDetection":
                            bodies.append(resource["properties"]["mainTemplate"])
                    self.assertEqual(2, len(bodies))
                    expected = copy.deepcopy(document["properties"])
                    expected["id"] = (
                        "xdr-" + document["contentProvenance"]["source"]["id"]
                    )
                    expected["id"] = f"[if(true(), '{expected['id']}', '{expected['id']}')]"
                    expected["detectionAction"]["alertTemplate"]["tactics"] = [authored[0]]
                    expected["contentProvenance"] = {
                        "packageId": "testpublisher.test-sentinel",
                        "packageVersion": "3.2.2",
                        "contentId": "xdr-" + document["contentProvenance"]["source"]["id"],
                        "contentVersion": document["version"],
                    }
                    for body in bodies:
                        self.assertEqual(expected, body["resources"]["detectionRule"]["properties"])
                    self.assertEqual(original, {p: p.read_bytes() for p in original})

    def test_invalid_tactic_lists_are_rejected_before_any_payload_selection(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        path = self.solution / "XDR Detections/Test.yaml"
        document = json.loads(path.read_text().removeprefix("---\n"))
        for tactics in (None, [], "Execution", ["Execution"], [{"tactic": ""}],
                        [{"tactic": "Execution"}, {"tactic": "Persistence", "techniques": ["T1547"]}]):
            document["properties"]["detectionAction"]["alertTemplate"]["tactics"] = tactics
            path.write_text("---\n" + json.dumps(document))
            with self.subTest(tactics=tactics):
                result = self.package(entry, False)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("Custom Detection", result.stderr)
                self.assertFalse((self.solution / "Package/mainTemplate.json").exists())


if __name__ == "__main__":
    unittest.main()
