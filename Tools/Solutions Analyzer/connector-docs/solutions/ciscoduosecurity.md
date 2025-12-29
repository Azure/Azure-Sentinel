# CiscoDuoSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cisco Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://duo.com/support](https://duo.com/support) |
| **Categories** | domains |
| **First Published** | 2022-01-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cisco Duo Security](../connectors/ciscoduosecurity.md)

**Publisher:** Cisco

The Cisco Duo Security data connector provides the capability to ingest [authentication logs](https://duo.com/docs/adminapi#authentication-logs), [administrator logs](https://duo.com/docs/adminapi#administrator-logs), [telephony logs](https://duo.com/docs/adminapi#telephony-logs), [offline enrollment logs](https://duo.com/docs/adminapi#offline-enrollment-logs) and [Trust Monitor events](https://duo.com/docs/adminapi#trust-monitor) into Microsoft Sentinel using the Cisco Duo Admin API. Refer to [API documentation](https://duo.com/docs/adminapi) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CiscoDuo_CL` |
| **Connector Definition Files** | [CiscoDuo_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Data%20Connectors/CiscoDuo_API_FunctionApp.json) |

[→ View full connector details](../connectors/ciscoduosecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CiscoDuo_CL` | [Cisco Duo Security](../connectors/ciscoduosecurity.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
|  3.0.4      |  26-09-2025                    | Updated support **Microsoft** to **Partner**                   |
|  3.0.3      |  02-09-2025                    | Added support for new log endpoints                   |
|  3.0.2      |  16-04-2024                    | Added Deploy to Azure Goverment button for Government portal in **Dataconnector**<br/> Fixed **Parser** issue for Parser name and ParentID mismatch |
|  3.0.1      |  30-01-2024                    | Updated solution to fix **parser** query                   |
|  3.0.0      |  08-01-2024                    | Updated solution to fix Api version of saved searches  |

[← Back to Solutions Index](../solutions-index.md)
