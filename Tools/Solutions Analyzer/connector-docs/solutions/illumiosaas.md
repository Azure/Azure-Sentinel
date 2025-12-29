# IllumioSaaS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Illumio |
| **Support Tier** | Partner |
| **Support Link** | [https://www.illumio.com/support/support](https://www.illumio.com/support/support) |
| **Categories** | domains |
| **First Published** | 2024-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Illumio SaaS](../connectors/illumiosaasdataconnector.md)

**Publisher:** Illumio

[Illumio](https://www.illumio.com/) connector provides the capability to ingest events into Microsoft Sentinel. The connector provides ability to ingest auditable and flow events from AWS S3 bucket.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Illumio_Auditable_Events_CL` |
| | `Illumio_Flow_Events_CL` |
| **Connector Definition Files** | [IllumioSaaS_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaaS_FunctionApp.json) |

[→ View full connector details](../connectors/illumiosaasdataconnector.md)

### [Illumio Saas](../connectors/illumiosaasccfdefinition.md)

**Publisher:** Microsoft

The Illumio Saas Cloud data connector provides the capability to ingest Flow logs into Microsoft Sentinel using the Illumio Saas Log Integration through AWS S3 Bucket. Refer to [Illumio Saas Log Integration](https://product-docs-repo.illumio.com/Tech-Docs/CloudSecure/out/en/administer-cloudsecure/connector.html#UUID-c14edaab-9726-1f23-9c4c-bc2937be39ee_section-idm234556433515698) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `IllumioFlowEventsV2_CL` |
| **Connector Definition Files** | [IllumioSaasLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaasLogs_ccf/IllumioSaasLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/illumiosaasccfdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `IllumioFlowEventsV2_CL` | [Illumio Saas](../connectors/illumiosaasccfdefinition.md) |
| `Illumio_Auditable_Events_CL` | [Illumio SaaS](../connectors/illumiosaasdataconnector.md) |
| `Illumio_Flow_Events_CL` | [Illumio SaaS](../connectors/illumiosaasdataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     				 |
|-------------|--------------------------------|---------------------------------------------------------|
| 3.4.0       | 03-02-2025                     | Added 2 new **Parser**. <br/> Added new connectorid SyslogAma to **Analytic Rules**. <br/> Resolved **Playbook** deployment error.<br/> Made minor visualization changes to **Workbooks**.                   |
| 3.3.0       | 12-12-2024                     | Version fixed 3.2.3 to 3.3.0.                          |
| 3.2.2       | 24-10-2024                     | Bump up package to 3.2.2 version.                        |
| 3.2.0       | 01-10-2024                     | Added new **Analytic Rules**.                            |
| 3.1.0       | 04-08-2024                     | Solution packaged with Modified logo link.               |
| 3.0.0       | 13-05-2024                     | Initial Solution Release.         					     |

[← Back to Solutions Index](../solutions-index.md)
