from __future__ import annotations

from pathlib import Path
from typing import Any

from solution_manager.qualification.pr_check_runner import (
    _extract_xdr_detection_fields,
)
from tests.test_pr_qualification_engine import (
    test_ddos_solution_nested_xdr_detections_and_sample_data,
)


def test_extract_xdr_detection_fields_supports_properties_nested_schema() -> None:
    """Verify _extract_xdr_detection_fields extracts fields from convert-solution properties-nested YAML."""
    nested_doc: dict[str, Any] = {
        "apiVersion": "2026-03-01",
        "kind": "CustomDetection",
        "contentProvenance": {
            "source": {
                "kind": "AnalyticsRule",
                "id": "6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
                "path": "Solutions/Azure DDoS Protection/Analytic Rules/AttackSourcesPPSThreshold.yaml",
                "querySha256": "cbabeb0916d52c15d6d9354534022ab1735fb22815d2336a3c616141a035c0a1",
                "schedule": {
                    "queryFrequency": "1h",
                    "queryPeriod": "1h",
                },
            },
            "conversion": {
                "reviewScope": {
                    "sourceDocumentSha256": "f053df233548466466d06f811b69dd718254d114d52bc28dc75290b660bf1fb1",
                }
            },
        },
        "properties": {
            "id": "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0",
            "displayName": "Attack Source Surpassed Traffic Threshold (PPS)",
            "queryCondition": {
                "queryText": "AzureDiagnostics | where Category == 'DDoSMitigationReports' | extend ReportId = reportId_s",
            },
            "schedule": {
                "frequency": "PT1H",
                "period": "PT1H",
            },
            "detectionAction": {
                "alertTemplate": {
                    "severity": "medium",
                    "tactics": [
                        {
                            "tactic": "Impact",
                            "techniques": [
                                {"technique": "T1498"},
                            ],
                        }
                    ],
                    "impactedAssets": [
                        {
                            "@odata.type": "#microsoft.graph.security.impactedDeviceAsset",
                            "identifier": "deviceName",
                            "inputColumnName": "Resource",
                        }
                    ],
                    "entityMappings": {
                        "ips": [
                            {
                                "id": "ip1",
                                "addressColumn": "sourcePublicIpAddress_s",
                            }
                        ]
                    },
                    "customDetails": {
                        "ReportId": "ReportId",
                    },
                }
            },
        },
    }

    extracted = _extract_xdr_detection_fields(nested_doc)
    assert extracted["id"] == "xdr-6e76fd9d-8104-41eb-bad3-26054a3ad5f0"
    assert "AzureDiagnostics" in extracted["query"]
    assert extracted["severity"] == "medium"
    assert extracted["tactics"] == ["Impact"]
    assert extracted["techniques"] == ["T1498"]
    assert extracted["frequency"] == "PT1H"
    assert isinstance(extracted["entities"], list) and len(extracted["entities"]) == 1
    assert extracted["customDetails"] == {"ReportId": "ReportId"}
    assert extracted["sourceRuleId"] == "6e76fd9d-8104-41eb-bad3-26054a3ad5f0"
    assert extracted["sourceRulePath"].endswith("AttackSourcesPPSThreshold.yaml")
    assert extracted["sourceRuleSha256"] == "cbabeb0916d52c15d6d9354534022ab1735fb22815d2336a3c616141a035c0a1"
    assert extracted["sourceKind"] == "Scheduled"


def test_azure_ddos_protection_target_checks_pass(tmp_path: Path) -> None:
    """Verify VAL-AR-01, E2E-V02, E2E-V03, MIG-V01, MIG-V02, and MIG-V03 return PASS on Solutions/Azure DDoS Protection."""
    test_ddos_solution_nested_xdr_detections_and_sample_data(tmp_path)
