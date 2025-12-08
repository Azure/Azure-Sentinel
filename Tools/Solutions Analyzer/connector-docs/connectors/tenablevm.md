# Tenable Vulnerability Management

| | |
|----------|-------|
| **Connector ID** | `TenableVM` |
| **Publisher** | Tenable |
| **Tables Ingested** | [`Tenable_VM_Asset_CL`](../tables-index.md#tenable_vm_asset_cl), [`Tenable_VM_Compliance_CL`](../tables-index.md#tenable_vm_compliance_cl), [`Tenable_VM_Vuln_CL`](../tables-index.md#tenable_vm_vuln_cl), [`Tenable_WAS_Asset_CL`](../tables-index.md#tenable_was_asset_cl), [`Tenable_WAS_Vuln_CL`](../tables-index.md#tenable_was_vuln_cl) |
| **Used in Solutions** | [Tenable App](../solutions/tenable-app.md) |
| **Connector Definition Files** | [TenableVM.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Data%20Connectors/TenableVM/TenableVM.json) |

The TVM data connector provides the ability to ingest Asset, Vulnerability, Compliance, WAS assets and WAS vulnerabilities data into Microsoft Sentinel using TVM REST APIs. Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

[← Back to Connectors Index](../connectors-index.md)
