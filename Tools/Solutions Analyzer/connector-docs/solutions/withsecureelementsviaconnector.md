# WithSecureElementsViaConnector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | WithSecure |
| **Support Tier** | Partner |
| **Support Link** | [https://www.withsecure.com/en/support](https://www.withsecure.com/en/support) |
| **Categories** | domains |
| **First Published** | 2022-11-03 |
| **Last Updated** | 2022-11-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaConnector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] WithSecure Elements via Connector](../connectors/withsecureelementsviaconnector.md)

**Publisher:** WithSecure

WithSecure Elements is a unified cloud-based cyber security platform.

By connecting WithSecure Elements via Connector to Microsoft Sentinel, security events can be received in Common Event Format (CEF) over syslog.

It requires deploying "Elements Connector" either on-prem or in cloud.

The Common Event Format (CEF) provides natively search & correlation, alerting and threat intelligence enrichment for each data log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [WithSecureElementsViaConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaConnector/Data%20Connectors/WithSecureElementsViaConnector.json) |

[→ View full connector details](../connectors/withsecureelementsviaconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] WithSecure Elements via Connector](../connectors/withsecureelementsviaconnector.md) |

## Release Notes

| **Version**   | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                                          |
|---------------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
|  3.0.1        |  01-07-2024                    | Deprecating data connectors |
|  3.0.0        |  31-10-2023                    | Updated legacy F-Secure links related to the connector installation and event forwarding configuration with WithSecure links|

[← Back to Solutions Index](../solutions-index.md)
