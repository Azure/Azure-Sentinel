#!/usr/bin/env python3
import json
import os

azure_sentinel_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.join(azure_sentinel_dir, "Package")
connectors_dir = os.path.join(azure_sentinel_dir, "DataConnectors")
rules_dir = os.path.join(azure_sentinel_dir, "AnalyticRules")
workbooks_dir = os.path.join(azure_sentinel_dir, "Workbooks")
hunting_dir = os.path.join(azure_sentinel_dir, "HuntingQueries")
parsers_dir = os.path.join(azure_sentinel_dir, "Parsers")

for d in [azure_sentinel_dir, package_dir, connectors_dir, rules_dir, workbooks_dir, hunting_dir, parsers_dir]:
    os.makedirs(d, exist_ok=True)

# 1. createUiDefinition.json
create_ui_definition = {
  "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
  "handler": "Microsoft.Azure.CreateUIDef",
  "version": "0.1.2-preview",
  "parameters": {
    "config": {
      "isDefault": True,
      "errorMessage": {
        "selectRange": "Please choose a valid value from the allowed range."
      }
    },
    "basics": {
      "description": "Deploy the DentiSystems Threat Intelligence & Active Deception solution for Microsoft Sentinel. Ingest high-fidelity honeypot breach telemetry, GATE zero-trust gateway blocks, and real-time adversary indicators directly into your Log Analytics workspace.",
      "subscription": {
        "resourceProviders": [
          "Microsoft.OperationsManagement",
          "Microsoft.OperationalInsights",
          "Microsoft.SecurityInsights",
          "Microsoft.Insights"
        ]
      },
      "location": {
        "metadata": {
          "hidden": False
        }
      },
      "resourceGroup": {
        "metadata": {
          "hidden": False
        }
      },
      "workspace": {
        "name": "workspace",
        "type": "Microsoft.OperationalInsights.WorkspaceSelector",
        "label": "Log Analytics Workspace",
        "subLabel": {
          "preValidation": "Select the Log Analytics workspace with Microsoft Sentinel enabled.",
          "postValidation": "Selected workspace verified."
        },
        "toolTip": "Choose the Microsoft Sentinel onboarded workspace for this solution.",
        "visible": True,
        "options": {
          "filter": {
            "resourceType": "Microsoft.OperationalInsights/workspaces"
          }
        }
      }
    },
    "steps": [
      {
        "name": "dentiSystemsConfig",
        "label": "DentiSystems Setup",
        "subLabel": {
          "preValidation": "Configure your DentiSystems API endpoint and authentication token.",
          "postValidation": "Configuration valid."
        },
        "blurb": "Provide your DentiSystems tenant credentials to enable automated threat intelligence ingestion into Microsoft Sentinel.",
        "elements": [
          {
            "name": "apiEndpoint",
            "type": "Microsoft.Common.TextBox",
            "label": "DentiSystems API Endpoint URL",
            "defaultValue": "https://api.grid.denti.systems/api/attacks/recent?format=json",
            "toolTip": "Enter your DentiGrid Threat Intelligence API URL.",
            "required": True
          },
          {
            "name": "apiKey",
            "type": "Microsoft.Common.PasswordBox",
            "label": "DentiSystems API Bearer Token",
            "defaultValue": "",
            "toolTip": "Enter your secure DentiSystems API Bearer Token.",
            "required": True
          },
          {
            "name": "enableDataConnector",
            "type": "Microsoft.Common.CheckBox",
            "label": "Enable Codeless REST API Data Connector",
            "defaultValue": True,
            "toolTip": "Enables automatic scheduled polling of DentiGrid threat feeds directly into your Sentinel workspace."
          }
        ]
      },
      {
        "name": "securityContent",
        "label": "Security Content & Analytics",
        "subLabel": {
          "preValidation": "Select detection rules, workbooks, and hunting queries to deploy.",
          "postValidation": "Content selection valid."
        },
        "blurb": "Choose the pre-built Microsoft Sentinel security content artifacts you wish to deploy:",
        "elements": [
          {
            "name": "contentInfo",
            "type": "Microsoft.Common.TextBlock",
            "options": {
              "text": "Select the security artifacts you wish to deploy alongside the DentiSystems integration:"
            }
          },
          {
            "name": "enableAnalyticRules",
            "type": "Microsoft.Common.CheckBox",
            "label": "Deploy Pre-configured Sentinel Analytic Detection Rules (4 Rules)",
            "defaultValue": True,
            "toolTip": "Deploys MITRE ATT&CK-mapped Scheduled Alert Rules: High Severity Honeypot Breach, Volumetric Recon/Scan, GATE Zero-Trust Threat Intercept, and SCADA/BMS Protocol Tampering."
          },
          {
            "name": "enableWorkbooks",
            "type": "Microsoft.Common.CheckBox",
            "label": "Deploy DentiSystems Threat Intelligence & Deception Dashboard Workbook",
            "defaultValue": True,
            "toolTip": "Deploys an interactive multi-tab Azure Monitor/Sentinel Workbook with attack geolocations, protocol breakdowns, honeypot sensor status, and attacker IP analytics."
          },
          {
            "name": "enableHuntingQueries",
            "type": "Microsoft.Common.CheckBox",
            "label": "Deploy Threat Hunting Saved Searches & ASIM Parsers",
            "defaultValue": True,
            "toolTip": "Deploys Log Analytics Saved Searches and ASIM normalization parser functions for advanced threat hunting."
          }
        ]
      }
    ],
    "outputs": {
      "workspace": "[basics('workspace').name]",
      "workspaceLocation": "[basics('workspace').location]",
      "location": "[basics('workspace').location]",
      "dentiSystemsApiEndpoint": "[steps('dentiSystemsConfig').apiEndpoint]",
      "dentiSystemsApiKey": "[steps('dentiSystemsConfig').apiKey]",
      "enableDataConnector": "[steps('dentiSystemsConfig').enableDataConnector]",
      "enableAnalyticRules": "[steps('securityContent').enableAnalyticRules]",
      "enableWorkbooks": "[steps('securityContent').enableWorkbooks]",
      "enableHuntingQueries": "[steps('securityContent').enableHuntingQueries]"
    }
  }
}

# 2. Workbook serialized data definition
workbook_serialized = {
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# 🛡️ DentiSystems Threat Intelligence & Active Deception Dashboard\n### Real-time visibility into honeypot traps, adversary TTPs, and GATE zero-trust gateway telemetry."
      },
      "name": "text_header"
    },
    {
      "type": 9,
      "content": {
        "version": "KqlParameterItem/1.0",
        "parameters": [
          {
            "id": "TimeRange",
            "version": "KqlParameterItem/1.0",
            "name": "TimeRange",
            "type": 4,
            "isRequired": True,
            "value": {
              "durationMs": 86400000
            },
            "typeSettings": {
              "selectableValues": [
                { "durationMs": 3600000, "createdTime": "2026-08-23" },
                { "durationMs": 86400000, "createdTime": "2026-08-23" },
                { "durationMs": 604800000, "createdTime": "2026-08-23" },
                { "durationMs": 2592000000, "createdTime": "2026-08-23" }
              ]
            },
            "timeContext": {
              "durationMs": 86400000
            }
          },
          {
            "id": "MinSeverity",
            "version": "KqlParameterItem/1.0",
            "name": "MinSeverity",
            "type": 1,
            "description": "Filter by minimum severity score (1-10)",
            "value": "1",
            "timeContext": {
              "durationMs": 86400000
            }
          }
        ],
        "style": "pills",
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces"
      },
      "name": "parameters_filters"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated {TimeRange}\n| where toint(Severity_d) >= toint('{MinSeverity}') or toint(Severity_s) >= toint('{MinSeverity}')\n| summarize \n    TotalAttacks = count(),\n    CriticalBreaches = countif(toint(Severity_d) >= 8 or toint(Severity_s) >= 8),\n    UniqueAttackerIPs = dcount(SourceIP_s),\n    ActiveSensors = dcount(NodeID_s)",
        "size": 4,
        "title": "Threat Intelligence KPI Overview",
        "timeContext": {
          "durationMs": 86400000
        },
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces",
        "visualization": "tiles",
        "tileSettings": {
          "titleContent": {
            "columnMatch": "TotalAttacks",
            "formatter": 1
          },
          "leftContent": {
            "columnMatch": "TotalAttacks",
            "formatter": 12,
            "formatOptions": {
              "palette": "auto"
            }
          },
          "showBorder": True
        }
      },
      "name": "query_kpi_tiles"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated {TimeRange}\n| summarize ThreatCount = count() by bin(TimeGenerated, 1h), Protocol = tostring(Protocol_s)\n| render timechart",
        "size": 0,
        "title": "Threat Volume by Protocol Over Time",
        "timeContext": {
          "durationMs": 86400000
        },
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces",
        "visualization": "timechart"
      },
      "name": "query_timechart"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated {TimeRange}\n| summarize AttackCount = count(), UniquePorts = dcount(DestinationPort_d), Signatures = make_set(Signature_s, 5) by SourceIP_s, SourceCountry_s, SourceCity_s\n| sort by AttackCount desc\n| take 20",
        "size": 0,
        "title": "Top 20 Malicious Threat Actors (Attacker IPs)",
        "timeContext": {
          "durationMs": 86400000
        },
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces",
        "visualization": "table",
        "gridSettings": {
          "formatters": [
            {
              "columnMatch": "AttackCount",
              "formatter": 8,
              "formatOptions": {
                "palette": "red"
              }
            }
          ]
        }
      },
      "name": "query_top_attackers"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated {TimeRange}\n| where Platform_s =~ 'GATE' or isnotempty(URL_s)\n| project TimeGenerated, SourceIP_s, SourceCountry_s, Method_s, URL_s, Signature_s, NodeID_s\n| sort by TimeGenerated desc\n| take 50",
        "size": 0,
        "title": "GATE Zero-Trust Reverse Proxy & WAF Intercept Stream",
        "timeContext": {
          "durationMs": 86400000
        },
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces",
        "visualization": "table"
      },
      "name": "query_gate_stream"
    }
  ]
}

# 3. mainTemplate.json
main_template = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workspace": {
      "type": "string",
      "metadata": {
        "description": "The name of the Log Analytics Workspace where Microsoft Sentinel is enabled."
      }
    },
    "workspaceLocation": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "The geographic region of the Log Analytics Workspace."
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "Deployment location for solution resources."
      }
    },
    "dentiSystemsApiEndpoint": {
      "type": "string",
      "defaultValue": "https://api.grid.denti.systems/api/attacks/recent",
      "metadata": {
        "description": "DentiSystems Threat Intelligence API feed endpoint URL."
      }
    },
    "dentiSystemsApiKey": {
      "type": "securestring",
      "metadata": {
        "description": "Authentication Bearer Token for the DentiSystems Threat Intelligence API."
      }
    },
    "enableDataConnector": {
      "type": "bool",
      "defaultValue": True,
      "metadata": {
        "description": "Deploy the Microsoft Sentinel Codeless Data Connector (CCP) for scheduled API polling."
      }
    },
    "enableAnalyticRules": {
      "type": "bool",
      "defaultValue": True,
      "metadata": {
        "description": "Deploy pre-configured Microsoft Sentinel Scheduled Alert Rules for automated incident generation."
      }
    },
    "enableWorkbooks": {
      "type": "bool",
      "defaultValue": True,
      "metadata": {
        "description": "Deploy interactive Azure Monitor/Sentinel Workbook for visual threat analysis."
      }
    },
    "enableHuntingQueries": {
      "type": "bool",
      "defaultValue": True,
      "metadata": {
        "description": "Deploy ASIM parser functions and advanced threat hunting saved searches."
      }
    },
    "_artifactsLocation": {
      "type": "string",
      "defaultValue": "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/DentiSystems/Package/",
      "metadata": {
        "description": "The base URI where artifacts required by this template are located."
      }
    },
    "_artifactsLocationSasToken": {
      "type": "securestring",
      "defaultValue": "",
      "metadata": {
        "description": "The sasToken required to access _artifactsLocation."
      }
    }
  },
  "variables": {
    "solutionId": "DentiSystemsThreatIntelligence",
    "solutionVersion": "1.0.0",
    "solutionName": "DentiSystems Threat Intelligence & Active Deception",
    "solutionDescription": "Provides real-time active deception telemetry, honeypot breach intelligence, and zero-trust gateway threat analytics from DentiSystems into Microsoft Sentinel.",
    "solutionAuthor": "DentiSystems Inc.",
    "customTableName": "DENTIGRIDThreats_CL",
    "dataConnectorName": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/DentiSystemsCCPConnector')]",
    "ruleId_HighSeverity": "[guid(parameters('workspace'), 'DentiSystems_HighSeverityBreach_Rule')]",
    "ruleId_VolumetricRecon": "[guid(parameters('workspace'), 'DentiSystems_VolumetricRecon_Rule')]",
    "ruleId_GateThreat": "[guid(parameters('workspace'), 'DentiSystems_GATE_ThreatIntercept_Rule')]",
    "ruleId_ScadaTamper": "[guid(parameters('workspace'), 'DentiSystems_SCADA_Tamper_Rule')]",
    "workbookId": "[guid(parameters('workspace'), 'DentiSystems_Threat_Workbook')]",
    "parserSavedSearchId": "[guid(parameters('workspace'), 'DentiSystems_Threats_Parser')]",
    "huntingQueryId_Creds": "[guid(parameters('workspace'), 'DentiSystems_Hunting_Creds')]",
    "huntingQueryId_Exploit": "[guid(parameters('workspace'), 'DentiSystems_Hunting_Exploitation')]"
  },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/metadata",
      "apiVersion": "2022-01-01-preview",
      "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', variables('solutionId'))]",
      "properties": {
        "parentId": "[concat('/subscriptions/', subscription().subscriptionId, '/resourceGroups/', resourceGroup().name, '/providers/Microsoft.OperationalInsights/workspaces/', parameters('workspace'), '/providers/Microsoft.SecurityInsights/solutions/', variables('solutionId'))]",
        "contentId": "[variables('solutionId')]",
        "kind": "Solution",
        "version": "[variables('solutionVersion')]",
        "source": {
          "kind": "Solution",
          "name": "[variables('solutionName')]",
          "sourceId": "[variables('solutionId')]"
        },
        "author": {
          "name": "[variables('solutionAuthor')]",
          "email": "security@denti.systems"
        },
        "support": {
          "name": "DentiSystems Support",
          "email": "support@denti.systems",
          "link": "https://denti.systems/support",
          "tier": "Partner"
        },
        "categories": {
          "domains": [
            "Security - Threat Intelligence",
            "Security - Network",
            "Security - Deception & Honeypots"
          ],
          "verticals": [
            "Critical Infrastructure",
            "PropTech & Smart Buildings",
            "Enterprise Security"
          ]
        },
        "providers": [
          "DentiSystems Inc."
        ],
        "firstPublishDate": "2026-08-20",
        "lastPublishDate": "2026-08-23"
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/dataConnectors",
      "apiVersion": "2022-11-01-preview",
      "name": "[variables('dataConnectorName')]",
      "kind": "RestApiPoller",
      "condition": "[parameters('enableDataConnector')]",
      "properties": {
        "connectorDefinitionName": "DentiSystemsThreatIntelligence",
        "dataType": "DENTIGRIDThreats_CL",
        "response": {
          "eventsJsonPaths": [
            "$.attacks[*]"
          ]
        },
        "paging": {
          "pagingType": "None"
        },
        "request": {
          "apiEndpoint": "[parameters('dentiSystemsApiEndpoint')]",
          "httpMethod": "Get",
          "headers": {
            "Accept": "application/json",
            "User-Agent": "Azure-Sentinel-DentiSystems-CCP/1.0"
          },
          "queryParameters": {
            "limit": "100",
            "format": "json"
          },
          "auth": {
            "type": "APIKey",
            "apiKeyIdentifier": "Authorization",
            "apiKeyName": "Authorization",
            "apiKeyValue": "[concat('Bearer ', parameters('dentiSystemsApiKey'))]"
          }
        },
        "uiConfig": {
          "title": "DentiSystems Active Deception & Threat Intelligence",
          "publisher": "DentiSystems Inc.",
          "descriptionMarkdown": "The **DentiSystems Solution for Microsoft Sentinel** provides automated continuous ingestion of high-fidelity threat intelligence, honeypot breach indicators, and GATE zero-trust gateway blocks directly into your Log Analytics workspace.",
          "customImage": "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/DentiSystems/Package/assets/logo.png",
          "graphQueriesTableName": "DENTIGRIDThreats_CL",
          "graphQueries": [
            {
              "metricName": "Total Threat Events Ingested",
              "legend": "DentiSystems Telemetry",
              "baseQuery": "DENTIGRIDThreats_CL | summarize count() by bin(TimeGenerated, 1h)"
            }
          ],
          "sampleQueries": [
            {
              "description": "High Severity Threats in Last 24 Hours",
              "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(24h)\n| where toint(Severity_d) >= 7 or toint(Severity_s) >= 7\n| project TimeGenerated, SourceIP_s, SourceCountry_s, DestinationPort_d, Protocol_s, Signature_s, Severity_s, Platform_s"
            },
            {
              "description": "Top Attacker IPs targeted across DentiGrid Deception Mesh",
              "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(7d)\n| summarize AttackCount = count(), UniquePorts = dcount(DestinationPort_d), Signatures = make_set(Signature_s) by SourceIP_s, SourceCountry_s\n| sort by AttackCount desc"
            }
          ],
          "dataTypes": [
            {
              "name": "DENTIGRIDThreats_CL",
              "lastDataReceivedQuery": "DENTIGRIDThreats_CL | summarize Time = max(TimeGenerated)\n| where isnotempty(Time)"
            }
          ],
          "connectivityCriterias": [
            {
              "type": "IsConnectedQuery",
              "value": [
                "DENTIGRIDThreats_CL | summarize LastLog = max(TimeGenerated) | project IsConnected = LastLog > ago(3d)"
              ]
            }
          ],
          "availability": {
            "status": "1",
            "isPreview": False
          },
          "instructionSteps": [
            {
              "title": "1. Obtain DentiSystems API Token",
              "description": "Log into your **DentiGrid Admin Console**, navigate to **Settings > Integrations > SIEM & SOAR Pipelines**, and copy your dedicated Bearer API Token."
            },
            {
              "title": "2. Verify Real-time Ingestion",
              "description": "Once configured, Microsoft Sentinel will poll the DentiSystems Threat Intelligence feed at regular intervals. Events will populate the `DENTIGRIDThreats_CL` table and can be queried using KQL or viewed in the prebuilt Workbook."
            }
          ]
        }
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
      "apiVersion": "2022-11-01-preview",
      "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', variables('ruleId_HighSeverity'))]",
      "kind": "Scheduled",
      "condition": "[parameters('enableAnalyticRules')]",
      "properties": {
        "displayName": "DentiSystems - High Severity Honeypot Breach Detected",
        "description": "Identifies critical exploitation attempts, unauthorized shell breakouts, or high-severity attacks intercepted by DentiGrid active deception honeypot sensors.",
        "severity": "High",
        "enabled": True,
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where toint(Severity_d) >= 8 or toint(Severity_s) >= 8 or Signature_s has_any ('RCE', 'Exploit', 'Breakout', 'Rootkit', 'Unauthorized Access', 'Privilege Escalation')\n| extend IPCustomEntity = coalesce(SourceIP_s, tostring(column_ifexists('ip_s', '')))\n| extend HostCustomEntity = coalesce(NodeID_s, tostring(column_ifexists('node_id_s', '')))\n| extend ProtocolCustom = coalesce(Protocol_s, tostring(column_ifexists('protocol_s', '')))\n| extend PortCustom = coalesce(tostring(DestinationPort_d), tostring(column_ifexists('port_d', '')))\n| project TimeGenerated, IPCustomEntity, HostCustomEntity, ProtocolCustom, PortCustom, Signature_s, Severity_s, SourceCountry_s, SourceCity_s, URL_s, Platform_s",
        "queryFrequency": "PT1H",
        "queryPeriod": "PT1H",
        "triggerOperator": "GreaterThan",
        "triggerThreshold": 0,
        "suppressionDuration": "PT1H",
        "suppressionEnabled": False,
        "tactics": [
          "InitialAccess",
          "Execution",
          "LateralMovement"
        ],
        "techniques": [
          "T1190",
          "T1078",
          "T1021"
        ],
        "entityMappings": [
          {
            "entityType": "IP",
            "fieldMappings": [
              {
                "identifier": "Address",
                "columnName": "IPCustomEntity"
              }
            ]
          },
          {
            "entityType": "Host",
            "fieldMappings": [
              {
                "identifier": "HostName",
                "columnName": "HostCustomEntity"
              }
            ]
          }
        ],
        "incidentConfiguration": {
          "createIncident": True,
          "groupingConfiguration": {
            "enabled": True,
            "reopenClosedIncident": False,
            "lookbackDuration": "PT5H",
            "matchingMethod": "Selected",
            "groupByEntities": [
              "IP"
            ],
            "groupByAlertDetails": [],
            "groupByCustomDetails": []
          }
        }
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
      "apiVersion": "2022-11-01-preview",
      "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', variables('ruleId_VolumetricRecon'))]",
      "kind": "Scheduled",
      "condition": "[parameters('enableAnalyticRules')]",
      "properties": {
        "displayName": "DentiSystems - Volumetric Port Scanning & Reconnaissance",
        "description": "Detects automated adversary scanners probing multiple honeypot sensors or targeting multiple distinct network ports across the DentiGrid deception mesh.",
        "severity": "Medium",
        "enabled": True,
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| summarize DistinctPorts = dcount(DestinationPort_d), DistinctNodes = dcount(NodeID_s), TotalAttempts = count(), Signatures = make_set(Signature_s, 5) by SourceIP_s, SourceCountry_s, bin(TimeGenerated, 15m)\n| where DistinctPorts >= 5 or TotalAttempts >= 20\n| extend IPCustomEntity = SourceIP_s",
        "queryFrequency": "PT15M",
        "queryPeriod": "PT1H",
        "triggerOperator": "GreaterThan",
        "triggerThreshold": 0,
        "suppressionDuration": "PT1H",
        "suppressionEnabled": False,
        "tactics": [
          "Discovery",
          "Reconnaissance"
        ],
        "techniques": [
          "T1046",
          "T1595"
        ],
        "entityMappings": [
          {
            "entityType": "IP",
            "fieldMappings": [
              {
                "identifier": "Address",
                "columnName": "IPCustomEntity"
              }
            ]
          }
        ],
        "incidentConfiguration": {
          "createIncident": True,
          "groupingConfiguration": {
            "enabled": True,
            "reopenClosedIncident": False,
            "lookbackDuration": "PT5H",
            "matchingMethod": "Selected",
            "groupByEntities": [
              "IP"
            ],
            "groupByAlertDetails": [],
            "groupByCustomDetails": []
          }
        }
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
      "apiVersion": "2022-11-01-preview",
      "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', variables('ruleId_GateThreat'))]",
      "kind": "Scheduled",
      "condition": "[parameters('enableAnalyticRules')]",
      "properties": {
        "displayName": "DentiSystems - GATE Zero-Trust Threat & Injection Intercepted",
        "description": "Detects SQL injection, OS command injection, XSS, or prompt injection payloads intercepted and blocked by the DentiSystems GATE edge reverse proxy.",
        "severity": "High",
        "enabled": True,
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where Platform_s =~ 'GATE' or Signature_s has_any ('SQL Injection', 'Command Injection', 'XSS', 'Prompt Injection', 'Schema Violation', 'BMS Override')\n| extend IPCustomEntity = SourceIP_s\n| extend URLCustomEntity = URL_s\n| project TimeGenerated, IPCustomEntity, URLCustomEntity, Signature_s, Method_s, SourceCountry_s, NodeID_s",
        "queryFrequency": "PT1H",
        "queryPeriod": "PT1H",
        "triggerOperator": "GreaterThan",
        "triggerThreshold": 0,
        "suppressionDuration": "PT1H",
        "suppressionEnabled": False,
        "tactics": [
          "InitialAccess",
          "DefenseEvasion"
        ],
        "techniques": [
          "T1190",
          "T1059"
        ],
        "entityMappings": [
          {
            "entityType": "IP",
            "fieldMappings": [
              {
                "identifier": "Address",
                "columnName": "IPCustomEntity"
              }
            ]
          },
          {
            "entityType": "URL",
            "fieldMappings": [
              {
                "identifier": "Url",
                "columnName": "URLCustomEntity"
              }
            ]
          }
        ],
        "incidentConfiguration": {
          "createIncident": True,
          "groupingConfiguration": {
            "enabled": True,
            "reopenClosedIncident": False,
            "lookbackDuration": "PT5H",
            "matchingMethod": "Selected",
            "groupByEntities": [
              "IP"
            ],
            "groupByAlertDetails": [],
            "groupByCustomDetails": []
          }
        }
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
      "apiVersion": "2022-11-01-preview",
      "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/', variables('ruleId_ScadaTamper'))]",
      "kind": "Scheduled",
      "condition": "[parameters('enableAnalyticRules')]",
      "properties": {
        "displayName": "DentiSystems - Critical SCADA / BMS / IoT Protocol Tampering",
        "description": "Detects unauthorized connection attempts or command injections targeting Modbus, BACnet, S7comm, MQTT, or BMS/IoT industrial control protocols.",
        "severity": "High",
        "enabled": True,
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where Protocol_s in~ ('modbus', 'bacnet', 's7comm', 'dnp3', 'mqtt', 'coap') or DestinationPort_d in (502, 47808, 102, 20000, 1883, 5683)\n| extend IPCustomEntity = SourceIP_s\n| extend HostCustomEntity = NodeID_s\n| project TimeGenerated, IPCustomEntity, HostCustomEntity, Protocol_s, DestinationPort_d, Signature_s, Severity_s, SourceCountry_s",
        "queryFrequency": "PT1H",
        "queryPeriod": "PT1H",
        "triggerOperator": "GreaterThan",
        "triggerThreshold": 0,
        "suppressionDuration": "PT1H",
        "suppressionEnabled": False,
        "tactics": [
          "Impact",
          "InitialAccess"
        ],
        "techniques": [
          "T0855",
          "T0812"
        ],
        "entityMappings": [
          {
            "entityType": "IP",
            "fieldMappings": [
              {
                "identifier": "Address",
                "columnName": "IPCustomEntity"
              }
            ]
          },
          {
            "entityType": "Host",
            "fieldMappings": [
              {
                "identifier": "HostName",
                "columnName": "HostCustomEntity"
              }
            ]
          }
        ],
        "incidentConfiguration": {
          "createIncident": True,
          "groupingConfiguration": {
            "enabled": True,
            "reopenClosedIncident": False,
            "lookbackDuration": "PT5H",
            "matchingMethod": "Selected",
            "groupByEntities": [
              "IP"
            ],
            "groupByAlertDetails": [],
            "groupByCustomDetails": []
          }
        }
      }
    },
    {
      "type": "Microsoft.Insights/workbooks",
      "apiVersion": "2022-04-01",
      "name": "[variables('workbookId')]",
      "location": "[parameters('workspaceLocation')]",
      "kind": "shared",
      "condition": "[parameters('enableWorkbooks')]",
      "properties": {
        "displayName": "DentiSystems Threat Intelligence & Deception Dashboard",
        "category": "sentinel",
        "sourceId": "[concat('/subscriptions/', subscription().subscriptionId, '/resourceGroups/', resourceGroup().name, '/providers/Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]",
        "serializedData": json.dumps(workbook_serialized)
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-08-01",
      "name": "[concat(parameters('workspace'), '/DentiSystemsThreats')]",
      "location": "[parameters('workspaceLocation')]",
      "condition": "[parameters('enableHuntingQueries')]",
      "properties": {
        "category": "DentiSystems",
        "displayName": "DentiSystemsThreats (ASIM Normalized Function)",
        "functionAlias": "DentiSystemsThreats",
        "query": "DENTIGRIDThreats_CL\n| extend EventVendor = 'DentiSystems', EventProduct = 'DentiGrid', EventProductVersion = '1.0'\n| extend EventStartTime = TimeGenerated, EventEndTime = TimeGenerated\n| extend EventType = 'ThreatIntel', EventSeverity = tostring(coalesce(Severity_s, tostring(Severity_d), 'Medium'))\n| extend SrcIpAddr = coalesce(SourceIP_s, tostring(column_ifexists('ip_s', '')))\n| extend SrcGeoCountry = coalesce(SourceCountry_s, tostring(column_ifexists('country_s', '')))\n| extend SrcGeoCity = coalesce(SourceCity_s, tostring(column_ifexists('city_s', '')))\n| extend DstPortNumber = toint(coalesce(DestinationPort_d, toint(column_ifexists('port_d', 0))))\n| extend NetworkProtocol = coalesce(Protocol_s, tostring(column_ifexists('protocol_s', '')))\n| extend ThreatSignature = coalesce(Signature_s, tostring(column_ifexists('signature_s', '')))\n| extend TargetNodeId = coalesce(NodeID_s, tostring(column_ifexists('node_id_s', '')))\n| extend TargetUrl = coalesce(URL_s, tostring(column_ifexists('url_s', '')))\n| extend HttpMethod = coalesce(Method_s, tostring(column_ifexists('method_s', '')))\n| extend RawPayload = coalesce(Payload_s, tostring(column_ifexists('payload_s', '')))\n| extend IngestionPlatform = coalesce(Platform_s, 'DENTIGRID')",
        "version": 1
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-08-01",
      "name": "[concat(parameters('workspace'), '/DentiSystems_Hunting_SSHBruteforce')]",
      "location": "[parameters('workspaceLocation')]",
      "condition": "[parameters('enableHuntingQueries')]",
      "properties": {
        "category": "DentiSystems Hunting",
        "displayName": "DentiSystems - SSH Deception Brute Force Hunting",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(7d)\n| where Protocol_s =~ 'ssh' or DestinationPort_d == 22\n| summarize AttemptCount = count(), NodeCount = dcount(NodeID_s), FirstSeen = min(TimeGenerated), LastSeen = max(TimeGenerated) by SourceIP_s, SourceCountry_s\n| where AttemptCount > 10\n| sort by AttemptCount desc",
        "version": 1
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-08-01",
      "name": "[concat(parameters('workspace'), '/DentiSystems_Hunting_ZeroDayExploitation')]",
      "location": "[parameters('workspaceLocation')]",
      "condition": "[parameters('enableHuntingQueries')]",
      "properties": {
        "category": "DentiSystems Hunting",
        "displayName": "DentiSystems - Zero-Day & Web Shell Exploitation Hunting",
        "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(7d)\n| where Signature_s has_any ('log4j', 'spring4shell', 'cve-', 'webshell', 'cmd.exe', '/bin/sh', 'curl', 'wget')\n| project TimeGenerated, SourceIP_s, SourceCountry_s, DestinationPort_d, Protocol_s, Signature_s, Method_s, URL_s, NodeID_s\n| sort by TimeGenerated desc",
        "version": 1
      }
    }
  ]
}

# 4. SolutionMetadata.json
solution_metadata = {
  "name": "DentiSystems",
  "version": "1.0.0",
  "author": "DentiSystems Inc. <security@denti.systems>",
  "publisher": "DentiSystems Inc.",
  "firstPublishDate": "2026-08-20",
  "lastPublishDate": "2026-08-23",
  "categories": {
    "domains": [
      "Security - Threat Intelligence",
      "Security - Network & Edge",
      "Security - Deception & Honeypots"
    ],
    "verticals": [
      "Critical Infrastructure",
      "PropTech & Smart Buildings",
      "Enterprise Security"
    ]
  },
  "contentId": "dentisystems-threat-intelligence-solution",
  "description": "The DentiSystems Solution for Microsoft Sentinel provides automated ingestion of active deception telemetry, honeypot breach indicators, GATE zero-trust gateway blocks, and real-time adversary threat intelligence.",
  "support": {
    "tier": "Partner",
    "name": "DentiSystems Support Team",
    "email": "support@denti.systems",
    "url": "https://denti.systems/support"
  },
  "packageDetails": {
    "dataConnectors": 1,
    "analyticRules": 4,
    "workbooks": 1,
    "huntingQueries": 2,
    "parsers": 1
  }
}

# Individual Rule Definitions
rule1 = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "id": "DentiSystems_HighSeverityBreach",
  "name": "DentiSystems - High Severity Honeypot Breach Detected",
  "type": "Microsoft.SecurityInsights/alertRules",
  "kind": "Scheduled",
  "properties": {
    "displayName": "DentiSystems - High Severity Honeypot Breach Detected",
    "description": "Identifies critical exploitation attempts, unauthorized shell breakouts, or high-severity attacks intercepted by DentiGrid active deception honeypot sensors.",
    "severity": "High",
    "enabled": True,
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where toint(Severity_d) >= 8 or toint(Severity_s) >= 8 or Signature_s has_any ('RCE', 'Exploit', 'Breakout', 'Rootkit', 'Unauthorized Access', 'Privilege Escalation')\n| extend IPCustomEntity = coalesce(SourceIP_s, tostring(column_ifexists('ip_s', '')))\n| extend HostCustomEntity = coalesce(NodeID_s, tostring(column_ifexists('node_id_s', '')))\n| extend ProtocolCustom = coalesce(Protocol_s, tostring(column_ifexists('protocol_s', '')))\n| extend PortCustom = coalesce(tostring(DestinationPort_d), tostring(column_ifexists('port_d', '')))\n| project TimeGenerated, IPCustomEntity, HostCustomEntity, ProtocolCustom, PortCustom, Signature_s, Severity_s, SourceCountry_s, SourceCity_s, URL_s, Platform_s",
    "queryFrequency": "PT1H",
    "queryPeriod": "PT1H",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "tactics": ["InitialAccess", "Execution", "LateralMovement"],
    "techniques": ["T1190", "T1078", "T1021"]
  }
}

rule2 = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "id": "DentiSystems_VolumetricRecon",
  "name": "DentiSystems - Volumetric Port Scanning & Reconnaissance",
  "type": "Microsoft.SecurityInsights/alertRules",
  "kind": "Scheduled",
  "properties": {
    "displayName": "DentiSystems - Volumetric Port Scanning & Reconnaissance",
    "description": "Detects automated adversary scanners probing multiple honeypot sensors or targeting multiple distinct network ports across the DentiGrid deception mesh.",
    "severity": "Medium",
    "enabled": True,
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| summarize DistinctPorts = dcount(DestinationPort_d), DistinctNodes = dcount(NodeID_s), TotalAttempts = count(), Signatures = make_set(Signature_s, 5) by SourceIP_s, SourceCountry_s, bin(TimeGenerated, 15m)\n| where DistinctPorts >= 5 or TotalAttempts >= 20\n| extend IPCustomEntity = SourceIP_s",
    "queryFrequency": "PT15M",
    "queryPeriod": "PT1H",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "tactics": ["Discovery", "Reconnaissance"],
    "techniques": ["T1046", "T1595"]
  }
}

rule3 = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "id": "DentiSystems_GATE_ThreatIntercept",
  "name": "DentiSystems - GATE Zero-Trust Threat & Injection Intercepted",
  "type": "Microsoft.SecurityInsights/alertRules",
  "kind": "Scheduled",
  "properties": {
    "displayName": "DentiSystems - GATE Zero-Trust Threat & Injection Intercepted",
    "description": "Detects SQL injection, OS command injection, XSS, or prompt injection payloads intercepted and blocked by the DentiSystems GATE edge reverse proxy.",
    "severity": "High",
    "enabled": True,
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where Platform_s =~ 'GATE' or Signature_s has_any ('SQL Injection', 'Command Injection', 'XSS', 'Prompt Injection', 'Schema Violation', 'BMS Override')\n| extend IPCustomEntity = SourceIP_s\n| extend URLCustomEntity = URL_s\n| project TimeGenerated, IPCustomEntity, URLCustomEntity, Signature_s, Method_s, SourceCountry_s, NodeID_s",
    "queryFrequency": "PT1H",
    "queryPeriod": "PT1H",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "tactics": ["InitialAccess", "DefenseEvasion"],
    "techniques": ["T1190", "T1059"]
  }
}

rule4 = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "id": "DentiSystems_SCADA_Tamper",
  "name": "DentiSystems - Critical SCADA / BMS / IoT Protocol Tampering",
  "type": "Microsoft.SecurityInsights/alertRules",
  "kind": "Scheduled",
  "properties": {
    "displayName": "DentiSystems - Critical SCADA / BMS / IoT Protocol Tampering",
    "description": "Detects unauthorized connection attempts or command injections targeting Modbus, BACnet, S7comm, MQTT, or BMS/IoT industrial control protocols.",
    "severity": "High",
    "enabled": True,
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(1h)\n| where Protocol_s in~ ('modbus', 'bacnet', 's7comm', 'dnp3', 'mqtt', 'coap') or DestinationPort_d in (502, 47808, 102, 20000, 1883, 5683)\n| extend IPCustomEntity = SourceIP_s\n| extend HostCustomEntity = NodeID_s\n| project TimeGenerated, IPCustomEntity, HostCustomEntity, Protocol_s, DestinationPort_d, Signature_s, Severity_s, SourceCountry_s",
    "queryFrequency": "PT1H",
    "queryPeriod": "PT1H",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "tactics": ["Impact", "InitialAccess"],
    "techniques": ["T0855", "T0812"]
  }
}

hunting_queries_doc = [
  {
    "id": "DentiSystems_Hunting_SSHBruteforce",
    "name": "DentiSystems - SSH Deception Brute Force Hunting",
    "description": "Identifies repeated automated SSH authentication and credential stuffing against honeypot sensors over the last 7 days.",
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(7d)\n| where Protocol_s =~ 'ssh' or DestinationPort_d == 22\n| summarize AttemptCount = count(), NodeCount = dcount(NodeID_s), FirstSeen = min(TimeGenerated), LastSeen = max(TimeGenerated) by SourceIP_s, SourceCountry_s\n| where AttemptCount > 10\n| sort by AttemptCount desc",
    "tactics": ["CredentialAccess", "InitialAccess"]
  },
  {
    "id": "DentiSystems_Hunting_ZeroDayExploitation",
    "name": "DentiSystems - Zero-Day & Web Shell Exploitation Hunting",
    "description": "Hunts for advanced exploit attempts, web shells, and zero-day command payloads captured by DentiSystems.",
    "query": "DENTIGRIDThreats_CL\n| where TimeGenerated >= ago(7d)\n| where Signature_s has_any ('log4j', 'spring4shell', 'cve-', 'webshell', 'cmd.exe', '/bin/sh', 'curl', 'wget')\n| project TimeGenerated, SourceIP_s, SourceCountry_s, DestinationPort_d, Protocol_s, Signature_s, Method_s, URL_s, NodeID_s\n| sort by TimeGenerated desc",
    "tactics": ["Execution", "Persistence"]
  }
]

# Write files
files_to_write = {
    os.path.join(azure_sentinel_dir, "createUiDefinition.json"): create_ui_definition,
    os.path.join(package_dir, "createUiDefinition.json"): create_ui_definition,
    os.path.join(azure_sentinel_dir, "mainTemplate.json"): main_template,
    os.path.join(package_dir, "mainTemplate.json"): main_template,
    os.path.join(azure_sentinel_dir, "SolutionMetadata.json"): solution_metadata,
    os.path.join(connectors_dir, "DentiSystems_CCP.json"): {
        "id": "DentiSystems_CCP",
        "title": "DentiSystems Active Deception & Threat Intelligence",
        "publisher": "DentiSystems Inc.",
        "descriptionMarkdown": "Ingest real-time honeypot traps and zero-trust proxy telemetry.",
        "dataType": "DENTIGRIDThreats_CL"
    },
    os.path.join(rules_dir, "DentiSystems_HighSeverityBreach.json"): rule1,
    os.path.join(rules_dir, "DentiSystems_VolumetricRecon.json"): rule2,
    os.path.join(rules_dir, "DentiSystems_GATE_ThreatIntercept.json"): rule3,
    os.path.join(rules_dir, "DentiSystems_SCADA_Tamper.json"): rule4,
    os.path.join(workbooks_dir, "DentiSystems_ThreatOverview.json"): workbook_serialized,
    os.path.join(hunting_dir, "DentiSystems_HuntingQueries.json"): hunting_queries_doc
}

for filepath, content in files_to_write.items():
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)
    print(f"Wrote {filepath} ({os.path.getsize(filepath)} bytes)")

# Write Parser KQL
parser_kql = """// DentiSystemsThreats ASIM Parser Function
// Usage: DentiSystemsThreats
DENTIGRIDThreats_CL
| extend EventVendor = 'DentiSystems', EventProduct = 'DentiGrid', EventProductVersion = '1.0'
| extend EventStartTime = TimeGenerated, EventEndTime = TimeGenerated
| extend EventType = 'ThreatIntel', EventSeverity = tostring(coalesce(Severity_s, tostring(Severity_d), 'Medium'))
| extend SrcIpAddr = coalesce(SourceIP_s, tostring(column_ifexists('ip_s', '')))
| extend SrcGeoCountry = coalesce(SourceCountry_s, tostring(column_ifexists('country_s', '')))
| extend SrcGeoCity = coalesce(SourceCity_s, tostring(column_ifexists('city_s', '')))
| extend DstPortNumber = toint(coalesce(DestinationPort_d, toint(column_ifexists('port_d', 0))))
| extend NetworkProtocol = coalesce(Protocol_s, tostring(column_ifexists('protocol_s', '')))
| extend ThreatSignature = coalesce(Signature_s, tostring(column_ifexists('signature_s', '')))
| extend TargetNodeId = coalesce(NodeID_s, tostring(column_ifexists('node_id_s', '')))
| extend TargetUrl = coalesce(URL_s, tostring(column_ifexists('url_s', '')))
| extend HttpMethod = coalesce(Method_s, tostring(column_ifexists('method_s', '')))
| extend RawPayload = coalesce(Payload_s, tostring(column_ifexists('payload_s', '')))
| extend IngestionPlatform = coalesce(Platform_s, 'DENTIGRID')
"""

with open(os.path.join(parsers_dir, "DentiSystems_ASIM_Parser.kql"), "w", encoding="utf-8") as f:
    f.write(parser_kql)
print(f"Wrote {os.path.join(parsers_dir, 'DentiSystems_ASIM_Parser.kql')}")

print("All JSON and KQL files generated successfully.")
