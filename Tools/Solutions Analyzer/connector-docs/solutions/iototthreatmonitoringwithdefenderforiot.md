# IoTOTThreatMonitoringwithDefenderforIoT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Defender for IoT](../connectors/iot.md)

**Publisher:** Microsoft

Gain insights into your IoT security by connecting Microsoft Defender for IoT alerts to Microsoft Sentinel.

You can get out-of-the-box alert metrics and data, including alert trends, top alerts, and alert breakdown by severity.

You can also get information about the recommendations provided for your IoT hubs including top recommendations and recommendations by severity. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224002&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [template_IoT.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Data%20Connectors/template_IoT.JSON) |

[→ View full connector details](../connectors/iot.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft Defender for IoT](../connectors/iot.md) |

[← Back to Solutions Index](../solutions-index.md)
