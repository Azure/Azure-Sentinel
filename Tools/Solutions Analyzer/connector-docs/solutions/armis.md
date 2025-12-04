# Armis

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Armis Corporation |
| **Support Tier** | Partner |
| **Support Link** | [https://support.armis.com/](https://support.armis.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-02 |
| **Last Updated** | 2024-08-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis) |\n\n## Data Connectors

This solution provides **4 data connector(s)**.

### Armis Activities

**Publisher:** Armis

The [Armis](https://www.armis.com/) Activities connector gives the capability to ingest Armis device Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/doc` for more information. The connector provides the ability to get device activity information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis detects what all devices are doing in your environment and classifies those activities to get a complete picture of device behavior. These activities are analyzed for an understanding of normal and abnormal device behavior and used to assess device and network risk.

**Tables Ingested:**

- `Armis_Activities_CL`

**Connector Definition Files:**

- [ArmisActivities_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisActivities/ArmisActivities_API_FunctionApp.json)

### Armis Alerts

**Publisher:** Armis

The [Armis](https://www.armis.com/) Alerts connector gives the capability to ingest Armis Alerts into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

**Tables Ingested:**

- `Armis_Alerts_CL`

**Connector Definition Files:**

- [ArmisAlerts_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisAlerts/ArmisAlerts_API_FunctionApp.json)

### Armis Alerts Activities

**Publisher:** Armis

The [Armis](https://www.armis.com/) Alerts Activities connector gives the capability to ingest Armis Alerts and Activities into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get alert and activity information from the Armis platform and to identify and prioritize threats in your environment. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. 

**Tables Ingested:**

- `Armis_Activities_CL`
- `Armis_Alerts_CL`

**Connector Definition Files:**

- [ArmisAlertsActivities_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisAlertsActivities/ArmisAlertsActivities_API_FunctionApp.json)

### Armis Devices

**Publisher:** Armis

The [Armis](https://www.armis.com/) Device connector gives the capability to ingest Armis Devices into Microsoft Sentinel through the Armis REST API. Refer to the API documentation: `https://<YourArmisInstance>.armis.com/api/v1/docs` for more information. The connector provides the ability to get device information from the Armis platform. Armis uses your existing infrastructure to discover and identify devices without having to deploy any agents. Armis can also integrate with your existing IT & security management tools to identify and classify each and every device, managed or unmanaged in your environment.

**Tables Ingested:**

- `Armis_Devices_CL`

**Connector Definition Files:**

- [ArmisDevice_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Data%20Connectors/ArmisDevice/ArmisDevice_API_FunctionApp.json)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Armis_Activities_CL` | Armis Activities, Armis Alerts Activities |
| `Armis_Alerts_CL` | Armis Alerts, Armis Alerts Activities |
| `Armis_Devices_CL` | Armis Devices |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n