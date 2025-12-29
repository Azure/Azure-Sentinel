# RSA SecurID

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] RSA® SecurID (Authentication Manager)](../connectors/rsasecuridam.md)

**Publisher:** RSA

The [RSA® SecurID Authentication Manager](https://www.securid.com/) data connector provides the capability to ingest [RSA® SecurID Authentication Manager events](https://community.rsa.com/t5/rsa-authentication-manager/rsa-authentication-manager-log-messages/ta-p/630160) into Microsoft Sentinel. Refer to [RSA® SecurID Authentication Manager documentation](https://community.rsa.com/t5/rsa-authentication-manager/getting-started-with-rsa-authentication-manager/ta-p/569582) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [RSASecurID.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID/Data%20Connectors/RSASecurID.json) |

[→ View full connector details](../connectors/rsasecuridam.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] RSA® SecurID (Authentication Manager)](../connectors/rsasecuridam.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.1       | 26-12-2024                     | Removed Deprecated **Data connector**                                          |
| 3.0.0       | 01-08-2024                     |Update **Parser** as part of Syslog migration                                   |
|             |                                |Deprecating data connectors                                                     |

[← Back to Solutions Index](../solutions-index.md)
