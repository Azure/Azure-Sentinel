# ApacheHTTPServer

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### [Deprecated] Apache HTTP Server

**Publisher:** Apache

The Apache HTTP Server data connector provides the capability to ingest [Apache HTTP Server](http://httpd.apache.org/) events into Microsoft Sentinel. Refer to [Apache Logs documentation](https://httpd.apache.org/docs/2.4/logs.html) for more information.

**Tables Ingested:**

- `ApacheHTTPServer_CL`

**Connector Definition Files:**

- [Connector_ApacheHTTPServer_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ApacheHTTPServer/Data%20Connectors/Connector_ApacheHTTPServer_agent.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ApacheHTTPServer_CL` | [Deprecated] Apache HTTP Server |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n