# vArmour Application Controller

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | vArmour Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varmour.com/contact-us/](https://www.varmour.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] vArmour Application Controller via Legacy Agent](../connectors/varmourac.md)

**Publisher:** vArmour

### [[Deprecated] vArmour Application Controller via AMA](../connectors/varmouracama.md)

**Publisher:** vArmour

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_vArmour_AppControllerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/template_vArmour_AppControllerAMA.json) |

[→ View full connector details](../connectors/varmouracama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] vArmour Application Controller via AMA](../connectors/varmouracama.md), [[Deprecated] vArmour Application Controller via Legacy Agent](../connectors/varmourac.md) |

[← Back to Solutions Index](../solutions-index.md)
