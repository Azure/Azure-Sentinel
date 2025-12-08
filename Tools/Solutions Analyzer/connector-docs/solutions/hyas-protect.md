# HYAS Protect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | HYAS |
| **Support Tier** | Partner |
| **Support Link** | [https://www.hyas.com/contact](https://www.hyas.com/contact) |
| **Categories** | domains |
| **First Published** | 2023-09-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [HYAS Protect](../connectors/hyasprotect.md)

**Publisher:** HYAS

HYAS Protect provide logs based on reputation values - Blocked, Malicious, Permitted, Suspicious.

| | |
|--------------------------|---|
| **Tables Ingested** | `HYASProtectDnsSecurityLogs_CL` |
| **Connector Definition Files** | [HYASProtect_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HYAS%20Protect/Data%20Connectors/HYASProtect_FunctionApp.json) |

[→ View full connector details](../connectors/hyasprotect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `HYASProtectDnsSecurityLogs_CL` | [HYAS Protect](../connectors/hyasprotect.md) |

[← Back to Solutions Index](../solutions-index.md)
