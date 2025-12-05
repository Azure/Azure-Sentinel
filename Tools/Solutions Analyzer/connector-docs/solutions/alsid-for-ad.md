# Alsid For AD

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Alsid |
| **Support Tier** | Partner |
| **Support Link** | [https://www.alsid.com/contact-us/](https://www.alsid.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Alsid for Active Directory](../connectors/alsidforad.md)

**Publisher:** Alsid

Alsid for Active Directory connector allows to export Alsid Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.

It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

| | |
|--------------------------|---|
| **Tables Ingested** | `AlsidForADLog_CL` |
| **Connector Definition Files** | [AlsidForAD.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Data%20Connectors/AlsidForAD.json) |

[→ View full connector details](../connectors/alsidforad.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AlsidForADLog_CL` | [Alsid for Active Directory](../connectors/alsidforad.md) |

[← Back to Solutions Index](../solutions-index.md)
