# QualysVM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2020-12-14 |
| **Last Updated** | 2025-11-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Qualys Vulnerability Management (via Codeless Connector Framework)](../connectors/qualysvmlogsccpdefinition.md)
- [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`QualysHostDetectionV2_CL`](../tables/qualyshostdetectionv2-cl.md) | [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md) | Analytics, Workbooks |
| [`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md) | [Qualys Vulnerability Management (via Codeless Connector Framework)](../connectors/qualysvmlogsccpdefinition.md) | Analytics, Workbooks |
| [`QualysHostDetection_CL`](../tables/qualyshostdetection-cl.md) | [[DEPRECATED] Qualys Vulnerability Management](../connectors/qualysvulnerabilitymanagement.md) | Analytics, Workbooks |

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 4 |
| Analytic Rules | 2 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [High Number of Urgent Vulnerabilities Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Analytic%20Rules/HighNumberofVulnDetectedV2.yaml) | Medium | InitialAccess | [`QualysHostDetectionV2_CL`](../tables/qualyshostdetectionv2-cl.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`QualysHostDetection_CL`](../tables/qualyshostdetection-cl.md) |
| [New High Severity Vulnerability Detected Across Multiple Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Analytic%20Rules/NewHighSeverityVulnDetectedAcrossMulitpleHostsV2.yaml) | Medium | InitialAccess | [`QualysHostDetectionV2_CL`](../tables/qualyshostdetectionv2-cl.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`QualysHostDetection_CL`](../tables/qualyshostdetection-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [QualysVMv2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Workbooks/QualysVMv2.json) | [`QualysHostDetectionV2_CL`](../tables/qualyshostdetectionv2-cl.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`QualysHostDetection_CL`](../tables/qualyshostdetection-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [QualysVM-GetAssetDetails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Playbooks/QualysVMPlaybooks/QualysVM-GetAssetDetails/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [QualysVM-GetAssets-ByCVEID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Playbooks/QualysVMPlaybooks/QualysVM-GetAssets-ByCVEID/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [QualysVM-GetAssets-ByOpenPort](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Playbooks/QualysVMPlaybooks/QualysVM-GetAssets-ByOpenPort/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [QualysVM-LaunchVMScan-GenerateReport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Playbooks/QualysVMPlaybooks/QualysVM-LaunchVMScan-GenerateReport/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [QualysHostDetection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Parsers/QualysHostDetection.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                            	|
|-------------|--------------------------------|----------------------------------------------------------------|
| 3.0.7       | 18-11-2025                     | Adding adjustable API partition limit & rate limit protection. |
| 3.0.6       | 18-09-2025                     | Updated Analytic rules, Parsers, and Workbooks in Sentinel solution content for **CCF connector** compatibility.     |
| 3.0.5       | 29-07-2025                     | Removed Deprecated **Data Connector**.							|  
| 3.0.4 	  | 30-06-2025 					   | QualysVM **CCF Data Connector** moving to GA 					|
| 3.0.3       | 27-05-2025                     | New **CCP Connector** added to the Solution.                   |
| 3.0.2       | 08-04-2025                     | Add HostTags to **Data Connector** and **Parsers**.            |
| 3.0.1       | 07-01-2025                     | Removed Custom Entity mappings from **Analytic Rule**.         |
| 3.0.0       | 16-04-2024                     | Added Deploy to Azure Goverment button for Government portal in **Dataconnector**.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
