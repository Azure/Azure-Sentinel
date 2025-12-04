# Tomcat

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Apache Tomcat](../connectors/apachetomcat.md)

**Publisher:** Apache

The Apache Tomcat solution provides the capability to ingest [Apache Tomcat](http://tomcat.apache.org/) events into Microsoft Sentinel. Refer to [Apache Tomcat documentation](http://tomcat.apache.org/tomcat-10.0-doc/logging.html) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Tomcat_CL` |
| **Connector Definition Files** | [Connector_Tomcat_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Tomcat/Data%20Connectors/Connector_Tomcat_agent.json) |

[→ View full connector details](../connectors/apachetomcat.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Tomcat_CL` | [[Deprecated] Apache Tomcat](../connectors/apachetomcat.md) |

[← Back to Solutions Index](../solutions-index.md)
