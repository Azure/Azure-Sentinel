# CiscoDuoSecurity

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `CiscoDuo_CL` |
| **Connector Definition Files** | [CiscoDuo_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Data%20Connectors/CiscoDuo_API_FunctionApp.json) |

[→ View full connector details](../connectors/ciscoduosecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CiscoDuo_CL` | [Cisco Duo Security](../connectors/ciscoduosecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
