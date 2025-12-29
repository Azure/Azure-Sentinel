# Tenable App

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Tenable |
| **Support Tier** | Partner |
| **Support Link** | [https://www.tenable.com/support/technical-support](https://www.tenable.com/support/technical-support) |
| **Categories** | domains |
| **First Published** | 2024-06-06 |
| **Last Updated** | 2025-06-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Tenable Identity Exposure](../connectors/tenableie.md)

**Publisher:** Tenable

Tenable Identity Exposure connector allows Indicators of Exposure, Indicators of Attack and trailflow logs to be ingested into Microsoft Sentinel.The different work books and data parsers allow you to more easily manipulate logs and monitor your Active Directory environment.  The analytic templates allow you to automate responses regarding different events, exposures and attacks.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Tenable_IE_CL` |
| **Connector Definition Files** | [TenableIE.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Data%20Connectors/TenableIE/TenableIE.json) |

[→ View full connector details](../connectors/tenableie.md)

### [Tenable Vulnerability Management](../connectors/tenablevm.md)

**Publisher:** Tenable

The TVM data connector provides the ability to ingest Asset, Vulnerability, Compliance, WAS assets and WAS vulnerabilities data into Microsoft Sentinel using TVM REST APIs. Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Tenable_VM_Asset_CL` |
| | `Tenable_VM_Compliance_CL` |
| | `Tenable_VM_Vuln_CL` |
| | `Tenable_WAS_Asset_CL` |
| | `Tenable_WAS_Vuln_CL` |
| **Connector Definition Files** | [TenableVM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Data%20Connectors/TenableVM/TenableVM.json) |

[→ View full connector details](../connectors/tenablevm.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Tenable_IE_CL` | [Tenable Identity Exposure](../connectors/tenableie.md) |
| `Tenable_VM_Asset_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_VM_Compliance_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_VM_Vuln_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_WAS_Asset_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |
| `Tenable_WAS_Vuln_CL` | [Tenable Vulnerability Management](../connectors/tenablevm.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.1       | 12-09-2025                     | Added button for Azure Gov Cloud in the UI page of the data connector.
| 3.1.0       | 19-06-2025                     | Updated the python runtime version to 3.12. Updated pyTenable sdk version to 1.7.4. Added support for WAS Asset and WAS Vuln data ingestion. Removed Queue Trigger functions and updated with Durable Functions. Added support for Log Ingestion API and updated parsers and playbooks accordingly |
| 3.0.1       | 05-09-2024                     | Updated the python runtime version to 3.11 |
| 3.0.0       | 03-07-2024                     | Initial Solution Release                    |

[← Back to Solutions Index](../solutions-index.md)
