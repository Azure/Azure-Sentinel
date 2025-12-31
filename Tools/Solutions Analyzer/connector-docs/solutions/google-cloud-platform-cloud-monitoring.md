# Google Cloud Platform Cloud Monitoring

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)](../connectors/gcpmonitorccpdefinition.md)
- [[DEPRECATED] Google Cloud Platform Cloud Monitoring](../connectors/gcpmonitordataconnector.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPMonitoring`](../tables/gcpmonitoring.md) | [Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)](../connectors/gcpmonitorccpdefinition.md) | - |
| [`GCP_MONITORING_CL`](../tables/gcp-monitoring-cl.md) | [[DEPRECATED] Google Cloud Platform Cloud Monitoring](../connectors/gcpmonitordataconnector.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GCP_MONITOR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Parsers/GCP_MONITOR.yaml) | - | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 26-08-2025                    | Moving Google Cloud Platform Cloud Monitoring **CCF Data Connector** to GA.   			 |
| 3.0.1      | 07-07-2025                    | Migrated the **Function app** connector to new CCF **Data Connector** - *Google Cloud Platform Cloud Monitoring* and updated **Parser**.  |
| 3.0.0      | 05-09-2024                    | Updated the python runtime version to 3.11 in Function App **Data Connector**.   		 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
