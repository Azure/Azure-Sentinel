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

This solution provides **2 data connector(s)**:

- [Tenable Identity Exposure](../connectors/tenableie.md)
- [Tenable Vulnerability Management](../connectors/tenablevm.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) | [Tenable Identity Exposure](../connectors/tenableie.md) | Analytics, Workbooks |
| [`Tenable_VM_Asset_CL`](../tables/tenable-vm-asset-cl.md) | [Tenable Vulnerability Management](../connectors/tenablevm.md) | Playbooks |
| [`Tenable_VM_Compliance_CL`](../tables/tenable-vm-compliance-cl.md) | [Tenable Vulnerability Management](../connectors/tenablevm.md) | - |
| [`Tenable_VM_Vuln_CL`](../tables/tenable-vm-vuln-cl.md) | [Tenable Vulnerability Management](../connectors/tenablevm.md) | Playbooks |
| [`Tenable_WAS_Asset_CL`](../tables/tenable-was-asset-cl.md) | [Tenable Vulnerability Management](../connectors/tenablevm.md) | - |
| [`Tenable_WAS_Vuln_CL`](../tables/tenable-was-vuln-cl.md) | [Tenable Vulnerability Management](../connectors/tenablevm.md) | - |

## Content Items

This solution includes **20 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 12 |
| Playbooks | 3 |
| Parsers | 3 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [TIE Active Directory attacks pathways](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEADAttacksPathways.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE DCShadow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEDCShadow.yaml) | High | DefenseEvasion | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE DCSync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEDCSync.yaml) | High | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Golden Ticket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEGoldenTicket.yaml) | High | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Indicators of Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEIndicatorsOfAttack.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Indicators of Exposures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEIndicatorsOfExposures.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE LSASS Memory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIELSASSMemory.yaml) | High | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Password Guessing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEPasswordGuessing.yaml) | High | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Password Spraying](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEPasswordSpraying.yaml) | High | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE Password issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEPasswordIssues.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE privileged accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEPrivilegedAccountIssues.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TIE user accounts issues](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Analytic%20Rules/TIEUserAccountIssues.yaml) | Low | CredentialAccess | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TenableIEIoA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Workbooks/TenableIEIoA.json) | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |
| [TenableIEIoE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Workbooks/TenableIEIoE.json) | [`Tenable_IE_CL`](../tables/tenable-ie-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Tenable VM - Enrich incident with asset info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Playbooks/Playbooks/Tenable-EnrichIncidentWithAssetsInfo/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | [`Tenable_VM_Asset_CL`](../tables/tenable-vm-asset-cl.md) *(read)* |
| [Tenable VM - Enrich incident with vulnerability info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Playbooks/Playbooks/Tenable-EnrichIncidentWithVulnInfo/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | [`Tenable_VM_Vuln_CL`](../tables/tenable-vm-vuln-cl.md) *(read)* |
| [Tenable VM - Launch Scan](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Playbooks/Playbooks/Tenable-LaunchScan/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TenableVMAssets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Parsers/TenableVMAssets.yaml) | - | - |
| [TenableVMVulnerabilities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Parsers/TenableVMVulnerabilities.yaml) | - | - |
| [afad_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tenable%20App/Parsers/afad_parser.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.1       | 12-09-2025                     | Added button for Azure Gov Cloud in the UI page of the data connector.
| 3.1.0       | 19-06-2025                     | Updated the python runtime version to 3.12. Updated pyTenable sdk version to 1.7.4. Added support for WAS Asset and WAS Vuln data ingestion. Removed Queue Trigger functions and updated with Durable Functions. Added support for Log Ingestion API and updated parsers and playbooks accordingly |
| 3.0.1       | 05-09-2024                     | Updated the python runtime version to 3.11 |
| 3.0.0       | 03-07-2024                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
