# Microsoft Defender for IoT

| | |
|----------|-------|
| **Connector ID** | `IoT` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityAlert`](../tables-index.md#securityalert) |
| **Used in Solutions** | [IoTOTThreatMonitoringwithDefenderforIoT](../solutions/iototthreatmonitoringwithdefenderforiot.md) |
| **Connector Definition Files** | [template_IoT.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Data%20Connectors/template_IoT.JSON) |

Gain insights into your IoT security by connecting Microsoft Defender for IoT alerts to Microsoft Sentinel.

You can get out-of-the-box alert metrics and data, including alert trends, top alerts, and alert breakdown by severity.

You can also get information about the recommendations provided for your IoT hubs including top recommendations and recommendations by severity. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224002&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Subscription**: Contributor permissions to the subscription of your IoT Hub.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Defender for IoT to Microsoft Sentinel**

Select Connect next to each Subscription whose IoT Hub's alerts you want to stream to Microsoft Sentinel.
- **Configure IoT pricing**
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `IotV2`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
