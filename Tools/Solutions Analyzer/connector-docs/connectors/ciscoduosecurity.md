# Cisco Duo Security

| | |
|----------|-------|
| **Connector ID** | `CiscoDuoSecurity` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`CiscoDuo_CL`](../tables-index.md#ciscoduo_cl) |
| **Used in Solutions** | [CiscoDuoSecurity](../solutions/ciscoduosecurity.md) |
| **Connector Definition Files** | [CiscoDuo_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Data%20Connectors/CiscoDuo_API_FunctionApp.json) |

The Cisco Duo Security data connector provides the capability to ingest [authentication logs](https://duo.com/docs/adminapi#authentication-logs), [administrator logs](https://duo.com/docs/adminapi#administrator-logs), [telephony logs](https://duo.com/docs/adminapi#telephony-logs), [offline enrollment logs](https://duo.com/docs/adminapi#offline-enrollment-logs) and [Trust Monitor events](https://duo.com/docs/adminapi#trust-monitor) into Microsoft Sentinel using the Cisco Duo Admin API. Refer to [API documentation](https://duo.com/docs/adminapi) for more information.

[← Back to Connectors Index](../connectors-index.md)
