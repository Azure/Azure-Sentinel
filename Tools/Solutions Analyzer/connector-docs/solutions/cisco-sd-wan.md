# Cisco SD-WAN

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cisco Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://globalcontacts.cloudapps.cisco.com/contacts/contactDetails/en_US/c1o1-c2o2-c3o8](https://globalcontacts.cloudapps.cisco.com/contacts/contactDetails/en_US/c1o1-c2o2-c3o8) |
| **Categories** | domains |
| **First Published** | 2023-06-01 |
| **Last Updated** | 2024-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cisco Software Defined WAN](../connectors/ciscosdwan.md)

**Publisher:** Cisco

The Cisco Software Defined WAN(SD-WAN) data connector provides the capability to ingest [Cisco SD-WAN](https://www.cisco.com/c/en_in/solutions/enterprise-networks/sd-wan/index.html) Syslog and Netflow data into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CiscoSDWANNetflow_CL` |
| | `Syslog` |
| **Connector Definition Files** | [CiscoSDWAN.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Data%20Connectors/CiscoSDWAN.json) |

[→ View full connector details](../connectors/ciscosdwan.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CiscoSDWANNetflow_CL` | [Cisco Software Defined WAN](../connectors/ciscosdwan.md) |
| `Syslog` | [Cisco Software Defined WAN](../connectors/ciscosdwan.md) |

[← Back to Solutions Index](../solutions-index.md)
