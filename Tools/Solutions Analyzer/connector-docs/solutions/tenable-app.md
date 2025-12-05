# Tenable App

## Solution Information

| | |
|------------------------|-------|
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

### [Tenable Vulnerability Management](../connectors/tenablevm.md)

**Publisher:** Tenable

The TVM data connector provides the ability to ingest Asset, Vulnerability, Compliance, WAS assets and WAS vulnerabilities data into Microsoft Sentinel using TVM REST APIs. Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
