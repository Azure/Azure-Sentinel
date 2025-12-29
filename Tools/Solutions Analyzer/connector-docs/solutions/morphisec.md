# Morphisec

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Morphisec |
| **Support Tier** | Partner |
| **Support Link** | [https://support.morphisec.com/support/home](https://support.morphisec.com/support/home) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Morphisec API Data Connector (via Codeless Connector Framework)](../connectors/morphisecccf.md)

**Publisher:** Morphisec

The [Morphisec](https://www.morphisec.com/) solution for Microsoft Sentinel enables you to seamlessly ingest security alerts directly from the Morphisec API. By leveraging Morphisec's proactive breach prevention and moving target defense capabilities, this integration enriches your security operations with high-fidelity, low-noise alerts on evasive threats.

This solution provides more than just data ingestion; it equips your security team with a full suite of ready-to-use content, including: Data Connector, ASIM Parser, Analytic Rule Templates and Workbook.

With this solution, you can empower your SOC to leverage Morphisec's powerful threat prevention within a unified investigation and response workflow in Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MorphisecAlerts_CL` |
| **Connector Definition Files** | [Morphisec_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Data%20Connectors/Morphisec_CCF/Morphisec_ConnectorDefinition.json) |

[→ View full connector details](../connectors/morphisecccf.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MorphisecAlerts_CL` | [Morphisec API Data Connector (via Codeless Connector Framework)](../connectors/morphisecccf.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                |
|-------------|--------------------------------|---------------------------------------------------|
| 3.1.0       | 10-09-2025                     | 	Adding CCF connector                             |
| 3.0.1       | 26-06-2024                     | 	Deprecating data connectors                      |
| 3.0.0       | 07-09-2023                     | 	Addition of new Morphisec AMA **Data Connector** |

[← Back to Solutions Index](../solutions-index.md)
