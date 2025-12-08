# JBoss

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] JBoss Enterprise Application Platform](../connectors/jbosseap.md)

**Publisher:** Red Hat

The JBoss Enterprise Application Platform data connector provides the capability to ingest [JBoss](https://www.redhat.com/en/technologies/jboss-middleware/application-platform) events into Microsoft Sentinel. Refer to [Red Hat documentation](https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/7.0/html/configuration_guide/logging_with_jboss_eap) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `JBossLogs_CL` |
| **Connector Definition Files** | [Connector_JBoss.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JBoss/Data%20Connectors/Connector_JBoss.json) |

[→ View full connector details](../connectors/jbosseap.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `JBossLogs_CL` | [[Deprecated] JBoss Enterprise Application Platform](../connectors/jbosseap.md) |

[← Back to Solutions Index](../solutions-index.md)
