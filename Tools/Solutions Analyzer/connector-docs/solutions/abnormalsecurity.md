# AbnormalSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Abnormal Security |
| **Support Tier** | Partner |
| **Support Link** | [https://abnormalsecurity.com/contact](https://abnormalsecurity.com/contact) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [AbnormalSecurity ](../connectors/abnormalsecurity.md)

**Publisher:** AbnormalSecurity

The Abnormal Security data connector provides the capability to ingest threat and case logs into Microsoft Sentinel using the [Abnormal Security Rest API.](https://app.swaggerhub.com/apis/abnormal-security/abx/)

| | |
|--------------------------|---|
| **Tables Ingested** | `ABNORMAL_CASES_CL` |
| | `ABNORMAL_THREAT_MESSAGES_CL` |
| **Connector Definition Files** | [AbnormalSecurity_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity/Data%20Connectors/AbnormalSecurity_API_FunctionApp.json) |

[→ View full connector details](../connectors/abnormalsecurity.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABNORMAL_CASES_CL` | [AbnormalSecurity ](../connectors/abnormalsecurity.md) |
| `ABNORMAL_THREAT_MESSAGES_CL` | [AbnormalSecurity ](../connectors/abnormalsecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
