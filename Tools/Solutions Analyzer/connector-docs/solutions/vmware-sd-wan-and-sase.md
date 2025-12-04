# VMware SD-WAN and SASE

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | VMware by Broadcom |
| **Support Tier** | Partner |
| **Support Link** | [https://developer.vmware.com/](https://developer.vmware.com/) |
| **Categories** | domains |
| **First Published** | 2023-12-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md)

**Publisher:** VMware by Broadcom

The [VMware SD-WAN & SASE](https://sase.vmware.com) data connector offers the capability to ingest VMware SD-WAN and CWS events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.vmware.com/apis/vmware-sase-platform/) for more information. The connector provides ability to get events which helps to examine potential network security issues, identify misconfigured network devices and monitor SD-WAN and SASE usage. If you have your own custom connector, make sure that the connector is deployed under an isolated Log Analytics Workspace first. In case of issues, questions or feature requests, please contact us via email on sase-siem-integration@vmware.com.

| | |
|--------------------------|---|
| **Tables Ingested** | `VMware_CWS_DLPLogs_CL` |
| | `VMware_CWS_Health_CL` |
| | `VMware_CWS_Weblogs_CL` |
| | `VMware_VECO_EventLogs_CL` |
| **Connector Definition Files** | [VMwareSASE_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Data%20Connectors/Function%20App%20Connector/VMwareSASE_API_FunctionApp.json) |

[→ View full connector details](../connectors/vmwaresdwan.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VMware_CWS_DLPLogs_CL` | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) |
| `VMware_CWS_Health_CL` | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) |
| `VMware_CWS_Weblogs_CL` | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) |
| `VMware_VECO_EventLogs_CL` | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) |

[← Back to Solutions Index](../solutions-index.md)
