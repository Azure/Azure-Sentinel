# Armis Activities

| | |
|----------|-------|
| **Connector ID** | `ArmisActivities` |
| **Publisher** | Armis |
| **Tables Ingested** | [`Armis_Activities_CL`](../tables-index.md#armis_activities_cl) |
| **Used in Solutions** | [Armis](../solutions/armis.md) |
| **Connector Definition Files** | [ArmisActivities_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisActivities/ArmisActivities_API_FunctionApp.json) |

The [Armis](https://www.armis.com/) Activities connector gives the capability to ingest Armis device Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/doc` for more information. The connector provides the ability to get device activity information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis detects what all devices are doing in your environment and classifies those activities to get a complete picture of device behavior. These activities are analyzed for an understanding of normal and abnormal device behavior and used to assess device and network risk.

[← Back to Connectors Index](../connectors-index.md)
