# Armis Alerts

| | |
|----------|-------|
| **Connector ID** | `ArmisAlerts` |
| **Publisher** | Armis |
| **Tables Ingested** | [`Armis_Alerts_CL`](../tables-index.md#armis_alerts_cl) |
| **Used in Solutions** | [Armis](../solutions/armis.md) |
| **Connector Definition Files** | [ArmisAlerts_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisAlerts/ArmisAlerts_API_FunctionApp.json) |

The [Armis](https://www.armis.com/) Alerts connector gives the capability to ingest Armis Alerts into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

[← Back to Connectors Index](../connectors-index.md)
