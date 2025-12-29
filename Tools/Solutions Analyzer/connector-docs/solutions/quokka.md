# Quokka

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Quokka |
| **Support Tier** | Partner |
| **Support Link** | [https://www.quokka.io/contact-us#customer-support](https://www.quokka.io/contact-us#customer-support) |
| **Categories** | domains |
| **First Published** | 2025-10-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [QscoutAppEventsConnector](../connectors/qscoutappeventsccfdefinition.md)

**Publisher:** Quokka

Ingest Qscout application events into Microsoft Sentinel

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `QscoutAppEvents_CL` |
| **Connector Definition Files** | [QuokkaQscoutAppEventsLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka/Data%20Connectors/QuokkaQscoutAppEventsLogs_ccf/QuokkaQscoutAppEventsLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/qscoutappeventsccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `QscoutAppEvents_CL` | [QscoutAppEventsConnector](../connectors/qscoutappeventsccfdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                     |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------------------|
| 3.0.0       | 07-11-2025                     | Initial Solution Release for Quokka **CCF Data Connector** with an Analytic Rule and a Workbook        |

[← Back to Solutions Index](../solutions-index.md)
