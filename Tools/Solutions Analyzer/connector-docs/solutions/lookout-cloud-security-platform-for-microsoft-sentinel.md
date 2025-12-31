# Lookout Cloud Security Platform for Microsoft Sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Lookout |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lookout.com/support](https://www.lookout.com/support) |
| **Categories** | domains |
| **First Published** | 2023-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Lookout Cloud Security for Microsoft Sentinel](../connectors/lookoutcloudsecuritydataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`LookoutCloudSecurity_CL`](../tables/lookoutcloudsecurity-cl.md) | [Lookout Cloud Security for Microsoft Sentinel](../connectors/lookoutcloudsecuritydataconnector.md) | - |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 3 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [LookoutCSActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel/Parsers/LookoutCSActivities.yaml) | - | - |
| [LookoutCSAnomalies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel/Parsers/LookoutCSAnomalies.yaml) | - | - |
| [LookoutCSViolations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel/Parsers/LookoutCSViolations.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 05-09-2024                     | Updated the python runtime version to 3.11  |
|             | 14-11-2023                     | **Data Connector** Updated data connector to use Lookout SASE Platform Integration API v23.2|
| 2.0.0       | 20-02-2023                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
