# Armis

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Armis Corporation |
| **Support Tier** | Partner |
| **Support Link** | [https://support.armis.com/](https://support.armis.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-02 |
| **Last Updated** | 2024-08-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis) |

## Data Connectors

This solution provides **4 data connector(s)**.

### [Armis Activities](../connectors/armisactivities.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Activities connector gives the capability to ingest Armis device Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/doc` for more information. The connector provides the ability to get device activity information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis detects what all devices are doing in your environment and classifies those activities to get a complete picture of device behavior. These activities are analyzed for an understanding of normal and abnormal device behavior and used to assess device and network risk.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Armis_Activities_CL` |
| **Connector Definition Files** | [ArmisActivities_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisActivities/ArmisActivities_API_FunctionApp.json) |

[→ View full connector details](../connectors/armisactivities.md)

### [Armis Alerts](../connectors/armisalerts.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Alerts connector gives the capability to ingest Armis Alerts into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Armis_Alerts_CL` |
| **Connector Definition Files** | [ArmisAlerts_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisAlerts/ArmisAlerts_API_FunctionApp.json) |

[→ View full connector details](../connectors/armisalerts.md)

### [Armis Alerts Activities](../connectors/armisalertsactivities.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Alerts Activities connector gives the capability to ingest Armis Alerts and Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert and activity information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Armis_Activities_CL` |
| | `Armis_Alerts_CL` |
| **Connector Definition Files** | [ArmisAlertsActivities_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisAlertsActivities/ArmisAlertsActivities_API_FunctionApp.json) |

[→ View full connector details](../connectors/armisalertsactivities.md)

### [Armis Devices](../connectors/armisdevices.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Armis_Devices_CL` |
| **Connector Definition Files** | [ArmisDevice_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisDevice/ArmisDevice_API_FunctionApp.json) |

[→ View full connector details](../connectors/armisdevices.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Armis_Activities_CL` | [Armis Activities](../connectors/armisactivities.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) |
| `Armis_Alerts_CL` | [Armis Alerts](../connectors/armisalerts.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) |
| `Armis_Devices_CL` | [Armis Devices](../connectors/armisdevices.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.2.0       | 05-12-2025                     | Log Ingestion Support.|
| 3.1.1       | 19-05-2025                     | Updated Armis AlertActivity and Armis Device Data connectors to add keyvault for storing Armis Access Token and Severity parameter in AlertActivity.|
| 3.1.0       | 11-09-2024                     | Updated Armis Alerts Data connector to ingest Armis Activities associated with only Armis Alerts.|
| 3.0.3       | 26-08-2024                     | Updated the python runtime version to **3.11**|
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall|
| 3.0.1       | 15-04-2024                     | Added Deploy to Azure Government button in **Data connectors**|
| 3.0.0       | 03-11-2023                     | Fixed vulnerability related issue by passing the scret key in the body of the request instead of the param in the data connector and playbook        |

[← Back to Solutions Index](../solutions-index.md)
