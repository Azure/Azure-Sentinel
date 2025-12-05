# Armis

## Solution Information

| | |
|------------------------|-------|
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

### [Armis Alerts](../connectors/armisalerts.md)

**Publisher:** Armis

### [Armis Alerts Activities](../connectors/armisalertsactivities.md)

**Publisher:** Armis

### [Armis Devices](../connectors/armisdevices.md)

**Publisher:** Armis

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
