# Armis Devices

| | |
|----------|-------|
| **Connector ID** | `ArmisDevices` |
| **Publisher** | Armis |
| **Tables Ingested** | [`Armis_Devices_CL`](../tables-index.md#armis_devices_cl) |
| **Used in Solutions** | [Armis](../solutions/armis.md) |
| **Connector Definition Files** | [ArmisDevice_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisDevice/ArmisDevice_API_FunctionApp.json) |

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

[← Back to Connectors Index](../connectors-index.md)
