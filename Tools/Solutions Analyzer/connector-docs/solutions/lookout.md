# Lookout

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Lookout |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lookout.com/support](https://www.lookout.com/support) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [DEPRECATED] Lookout

**Publisher:** Lookout

The [Lookout](https://lookout.com) data connector provides the capability to ingest [Lookout](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#commoneventfields) events into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. The [Lookout](https://lookout.com) data connector provides ability to get events which helps to examine potential security risks and more.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

**Tables Ingested:**

- `Lookout_CL`

**Connector Definition Files:**

- [Lookout_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/Lookout_API_FunctionApp.json)

### Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)

**Publisher:** Microsoft

The [Lookout Mobile Threat Detection](https://lookout.com) data connector provides the capability to ingest events related to mobile security risks into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. This connector helps you examine potential security risks detected in mobile devices.

**Tables Ingested:**

- `LookoutMtdV2_CL`

**Connector Definition Files:**

- [LookoutStreaming_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DataConnectorDefinition.json)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `LookoutMtdV2_CL` | 1 connector(s) |
| `Lookout_CL` | [DEPRECATED] Lookout |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n