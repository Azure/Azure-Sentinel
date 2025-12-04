# Cisco ACI

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Application Centric Infrastructure](../connectors/ciscoaci.md)

**Publisher:** Cisco

[Cisco Application Centric Infrastructure (ACI)](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/solution-overview-c22-741487.html) data connector provides the capability to ingest [Cisco ACI logs](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/all/syslog/guide/b_ACI_System_Messages_Guide/m-aci-system-messages-reference.html) into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [CiscoACI_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI/Data%20Connectors/CiscoACI_Syslog.json) |

[→ View full connector details](../connectors/ciscoaci.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Application Centric Infrastructure](../connectors/ciscoaci.md) |

[← Back to Solutions Index](../solutions-index.md)
