# Semperis Directory Services Protector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Semperis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.semperis.com/contact-us/](https://www.semperis.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Semperis Directory Services Protector](../connectors/semperisdsp.md)

**Publisher:** SEMPERIS

Semperis Directory Services Protector data connector allows for the export of its Windows event logs (i.e. Indicators of Exposure and Indicators of Compromise) to Microsoft Sentinel in real time.

It provides a data parser to manipulate the Windows event logs more easily. The different workbooks ease your Active Directory security monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityEvent` |
| **Connector Definition Files** | [SemperisDSP-connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Data%20Connectors/SemperisDSP-connector.json) |

[→ View full connector details](../connectors/semperisdsp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityEvent` | [Semperis Directory Services Protector](../connectors/semperisdsp.md) |

[← Back to Solutions Index](../solutions-index.md)
