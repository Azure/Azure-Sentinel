# vArmour Application Controller

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | vArmour Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varmour.com/contact-us/](https://www.varmour.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] vArmour Application Controller via Legacy Agent

**Publisher:** vArmour

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Connector_vArmour_AppController_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/Connector_vArmour_AppController_CEF.json)

### [Deprecated] vArmour Application Controller via AMA

**Publisher:** vArmour

vArmour reduces operational risk and increases cyber resiliency by visualizing and controlling application relationships across the enterprise. This vArmour connector enables streaming of Application Controller Violation Alerts into Microsoft Sentinel, so you can take advantage of search & correlation, alerting, & threat intelligence enrichment for each log.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_vArmour_AppControllerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/template_vArmour_AppControllerAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n