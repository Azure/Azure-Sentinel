# IllumioSaaS

## Solution Information

| | |
|------------------------|-------|
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

### [Illumio Saas](../connectors/illumiosaasccfdefinition.md)

**Publisher:** Microsoft

The Illumio Saas Cloud data connector provides the capability to ingest Flow logs into Microsoft Sentinel using the Illumio Saas Log Integration through AWS S3 Bucket. Refer to [Illumio Saas Log Integration](https://product-docs-repo.illumio.com/Tech-Docs/CloudSecure/out/en/administer-cloudsecure/connector.html#UUID-c14edaab-9726-1f23-9c4c-bc2937be39ee_section-idm234556433515698) for more information.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
