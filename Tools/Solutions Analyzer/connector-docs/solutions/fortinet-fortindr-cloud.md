# Fortinet FortiNDR Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Fortinet |
| **Support Tier** | Partner |
| **Support Link** | [https://www.fortinet.com/support](https://www.fortinet.com/support) |
| **Categories** | domains |
| **First Published** | 2024-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`FncEventsDetections_CL`](../tables/fnceventsdetections-cl.md) | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) | Workbooks |
| [`FncEventsObservation_CL`](../tables/fnceventsobservation-cl.md) | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) | Workbooks |
| [`FncEventsSuricata_CL`](../tables/fnceventssuricata-cl.md) | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [FortinetFortiNdrCloudWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud/Workbooks/FortinetFortiNdrCloudWorkbook.json) | [`FncEventsDetections_CL`](../tables/fnceventsdetections-cl.md)<br>[`FncEventsObservation_CL`](../tables/fnceventsobservation-cl.md)<br>[`FncEventsSuricata_CL`](../tables/fnceventssuricata-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Fortinet_FortiNDR_Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud/Parsers/Fortinet_FortiNDR_Cloud.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                    |
|-------------|--------------------------------|-------------------------------------------------------|
| 3.0.3       | 05-05-2025                     | Use Flex Consumption plan to hold Data Connector      |
| 3.0.2       | 30-09-2024                     | Show mitre attack ids and link to detection rule page |
| 3.0.1       | 31-05-2024                     | Replace Metastream with FortiNDR Cloud API            |
| 3.0.0       | 29-02-2024                     | Initial Solution Release                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
