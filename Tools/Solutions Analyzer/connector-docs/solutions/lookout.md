# Lookout

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Lookout |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lookout.com/support](https://www.lookout.com/support) |
| **Categories** | domains |
| **Version** | 3.0.1 |
| **First Published** | 2021-10-18 |
| **Last Updated** | 2025-11-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Lookout](../connectors/lookoutapi.md)
- [Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)](../connectors/lookoutstreaming-definition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) | [Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)](../connectors/lookoutstreaming-definition.md) | Analytics, Hunting, Workbooks |
| [`Lookout_CL`](../tables/lookout-cl.md) | [[DEPRECATED] Lookout](../connectors/lookoutapi.md) | Analytics |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Workbooks | 5 |
| Hunting Queries | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Lookout - Critical Audit and Policy Changes (v2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Analytic%20Rules/LookoutAuditEventV2.yaml) | Medium | DefenseEvasion, Persistence, PrivilegeEscalation, Impact | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [Lookout - Critical Smishing and Phishing Alerts (v2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Analytic%20Rules/LookoutSmishingAlertV2.yaml) | High | InitialAccess, CredentialAccess, Collection, Discovery | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [Lookout - Device Compliance and Security Status Changes (v2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Analytic%20Rules/LookoutDeviceComplianceV2.yaml) | Medium | Discovery, DefenseEvasion, Persistence | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [Lookout - High Severity Mobile Threats Detected (v2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Analytic%20Rules/LookoutThreatEventV2.yaml) | High | Discovery, DefenseEvasion, Persistence, PrivilegeEscalation | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [Lookout - New Threat events found.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Analytic%20Rules/LookoutThreatEvent.yaml) | High | Discovery | [`Lookout_CL`](../tables/lookout-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Lookout Advanced Threat Hunting - Multi-Vector Attacks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Hunting%20Queries/LookoutAdvancedThreatHunting.yaml) | Discovery, Persistence, DefenseEvasion | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [LookoutEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Workbooks/LookoutEvents.json) | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [LookoutEventsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Workbooks/LookoutEventsV2.json) | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [LookoutExecutiveDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Workbooks/LookoutExecutiveDashboard.json) | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [LookoutIOAInvestigationDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Workbooks/LookoutIOAInvestigationDashboard.json) | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |
| [LookoutSecurityInvestigationDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Workbooks/LookoutSecurityInvestigationDashboard.json) | [`LookoutMtdV2_CL`](../tables/lookoutmtdv2-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [LookoutEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Parsers/LookoutEvents.yaml) | - | - |

## Additional Documentation

> 📄 *Source: [Lookout/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/README.md)*

## 🚀 Overview

The Lookout Mobile Risk API v2 solution provides comprehensive mobile threat detection, device compliance monitoring, and security intelligence for Microsoft Sentinel. This enhanced version leverages the full capabilities of Lookout's Mobile Risk API v2 to deliver advanced threat correlation, smishing detection, and sophisticated security analytics.

## ✨ What's New in v2

### 🆕 New Capabilities
- **Smishing Detection**: Advanced SMS phishing protection with impersonation analysis
- **Enhanced Device Intelligence**: 50+ v2 fields including MDM integration details
- **Audit Trail**: Complete administrative action tracking for compliance
- **Advanced Risk Scoring**: Multi-dimensional threat assessment
- **Campaign Detection**: Sophisticated coordinated attack identification

### 📊 Enhanced Components
- **4 Analytics Rules**: Comprehensive threat detection across all event types
- **6 Hunting Queries**: Advanced threat correlation scenarios
- **Enhanced Workbook**: Rich visualizations with v2 data insights
- **Validation Framework**: Complete testing and validation methodology

## 📁 Solution Structure

```
Solutions/Lookout/
├── 📋 README.md                           # This file
├── 🚀 DEPLOYMENT_GUIDE.md                 # Production deployment guide
├── 🧪 DEV_TESTING_GUIDE.md               # Development testing guide
├── 🔌 CODELESS_CONNECTOR_GUIDE.md         # 🆕 Codeless Connector Framework guide
├── 📊 UPGRADE_ANALYSIS.md                 # v1 to v2 upgrade analysis
├── 🗺️ V2_FIELD_MAPPING.md                # Complete v2 field mapping
├── 🏗️ ARCHITECTURE_DIAGRAM.md            # Solution architecture
├── 📝 TEST_DATA_SAMPLES.md               # Test data documentation
├── 📄 TEST_DATA_SAMPLES.json             # Sample v2 event data
├── 
├── 📊 Data/
│   └── Solution_Lookout.json             # Solution metadata
├── 
├── 🔌 Data Connectors/
│   ├── requirements.txt                  # Python dependencies
│   ├── LookoutAPISentinelConnector/      # Legacy function app connector
│   └── LookoutStreamingConnector_ccp/    # Enhanced CCP connector
│       ├── LookoutStreaming_DataConnectorDefinition.json
│       ├── LookoutStreaming_DCR.json     # Data Collection Rule
│       ├── LookoutStreaming_Table.json   # Table schema
│       └── LookoutStreaming_PollingConfig.json
├── 
├── 🔍 Parsers/
│   └── LookoutEvents.yaml                # Enhanced v2 parser
├── 
├── 🚨 Analytic Rules/
│   ├── LookoutThreatEvent.yaml           # Legacy threat detection
│   ├── LookoutThreatEventV2.yaml         # Enhanced threat detection
│   ├── LookoutDeviceComplianceV2.yaml    # Device compliance monitoring
│   ├── LookoutSmishingAlertV2.yaml       # 🆕 Smishing detection
│   └── LookoutAuditEventV2.yaml          # 🆕 Audit event monitoring
├── 
├── 🎯 Hunting Queries/
│   └── LookoutAdvancedThreatHunting.yaml # 🆕 6 advanced hunting scenarios
├── 
├── 📊 Workbooks/
│   ├── LookoutEvents.json                # Legacy workbook

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 12-11-2025                     | **Parser** updates have been implemented, along with the development of comprehensive and executive dashboards. Additionally, **Analytic Rules** have been updated to include MITRE mappings. |
| 3.0.0       | 07-11-2025                     | New **CCF Connector** added to Solution - *Lookout Mobile Threat Detection Connector*.    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
