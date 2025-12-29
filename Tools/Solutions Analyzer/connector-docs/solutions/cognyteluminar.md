# CognyteLuminar

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cognyte Luminar |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cognyte.com/contact/](https://www.cognyte.com/contact/) |
| **Categories** | domains |
| **First Published** | 2023-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Luminar IOCs and Leaked Credentials](../connectors/cognyteluminar.md)

**Publisher:** Cognyte Technologies Israel Ltd

Luminar IOCs and Leaked Credentials connector allows integration of intelligence-based IOC data and customer-related leaked records identified by Luminar.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [CognyteLuminar_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar/Data%20Connectors/CognyteLuminar_FunctionApp.json) |

[→ View full connector details](../connectors/cognyteluminar.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | [Luminar IOCs and Leaked Credentials](../connectors/cognyteluminar.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 15-04-2025                     | Added Cognyte Luminar Taxii Server          |
| 3.0.1       | 07-08-2024                     | Updated the python runtime version to 3.11  |
| 3.0.0       | 15-09-2023                     | Initial Solution Release                    |

[← Back to Solutions Index](../solutions-index.md)
