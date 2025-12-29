# Cisco ISE

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md)

**Publisher:** Cisco

The Cisco Identity Services Engine (ISE) data connector provides the capability to ingest [Cisco ISE](https://www.cisco.com/c/en/us/products/security/identity-services-engine/index.html) events into Microsoft Sentinel. It helps you gain visibility into what is happening in your network, such as who is connected, which applications are installed and running, and much more. Refer to [Cisco ISE logging mechanism documentation](https://www.cisco.com/c/en/us/td/docs/security/ise/2-7/admin_guide/b_ise_27_admin_guide/b_ISE_admin_27_maintain_monitor.html#reference_BAFBA5FA046A45938810A5DF04C00591) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Cisco_ISE.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Data%20Connectors/Connector_Cisco_ISE.json) |

[→ View full connector details](../connectors/ciscoise.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                              |
|-------------|-------------------------------|-------------------------------------------------|
| 3.0.3       | 20-05-2025                    | Updated **Parser** to parse new fields          |
| 3.0.2       | 04-12-2024                    | Removed Deprecated **Data connectors**          |
| 3.0.1       | 23-07-2024                    | Deprecated data connectors                      |
| 3.0.0       | 11-07-2023                    | **Parser** query optimization done		        |

[← Back to Solutions Index](../solutions-index.md)
