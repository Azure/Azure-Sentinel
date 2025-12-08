# VMware SD-WAN and SASE Connector

| | |
|----------|-------|
| **Connector ID** | `VMwareSDWAN` |
| **Publisher** | VMware by Broadcom |
| **Tables Ingested** | [`VMware_CWS_DLPLogs_CL`](../tables-index.md#vmware_cws_dlplogs_cl), [`VMware_CWS_Health_CL`](../tables-index.md#vmware_cws_health_cl), [`VMware_CWS_Weblogs_CL`](../tables-index.md#vmware_cws_weblogs_cl), [`VMware_VECO_EventLogs_CL`](../tables-index.md#vmware_veco_eventlogs_cl) |
| **Used in Solutions** | [VMware SD-WAN and SASE](../solutions/vmware-sd-wan-and-sase.md) |
| **Connector Definition Files** | [VMwareSASE_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Data%20Connectors/Function%20App%20Connector/VMwareSASE_API_FunctionApp.json) |

The [VMware SD-WAN & SASE](https://sase.vmware.com) data connector offers the capability to ingest VMware SD-WAN and CWS events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.vmware.com/apis/vmware-sase-platform/) for more information. The connector provides ability to get events which helps to examine potential network security issues, identify misconfigured network devices and monitor SD-WAN and SASE usage. If you have your own custom connector, make sure that the connector is deployed under an isolated Log Analytics Workspace first. In case of issues, questions or feature requests, please contact us via email on sase-siem-integration@vmware.com.

[← Back to Connectors Index](../connectors-index.md)
