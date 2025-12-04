# CiscoASA

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### Cisco ASA via Legacy Agent

**Publisher:** Cisco

The Cisco ASA firewall connector allows you to easily connect your Cisco ASA logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [CiscoASA.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/CiscoASA.JSON)

### Cisco ASA/FTD via AMA

**Publisher:** Microsoft

The Cisco ASA firewall connector allows you to easily connect your Cisco ASA logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_CiscoAsaAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/template_CiscoAsaAma.JSON)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | Cisco ASA via Legacy Agent, Cisco ASA/FTD via AMA |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n