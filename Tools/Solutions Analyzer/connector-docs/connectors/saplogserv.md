# SAP LogServ (RISE), S/4HANA Cloud private edition

| | |
|----------|-------|
| **Connector ID** | `SAPLogServ` |
| **Publisher** | SAP SE |
| **Tables Ingested** | [`SAPLogServ_CL`](../tables-index.md#saplogserv_cl) |
| **Used in Solutions** | [SAP LogServ](../solutions/sap-logserv.md) |
| **Connector Definition Files** | [SAPLogServ.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ.json), [SAPLogServ_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ_PUSH_CCP/SAPLogServ_connectorDefinition.json) |

SAP LogServ is an SAP Enterprise Cloud Services (ECS) service aimed at collection, storage, forwarding and access of logs. LogServ centralizes the logs from all systems, applications, and ECS services used by a registered customer. 

 Main Features include:

Near Realtime Log Collection: With ability to integrate into Microsoft Sentinel as SIEM solution.

LogServ complements the existing SAP application layer threat monitoring and detections in Microsoft Sentinel with the log types owned by SAP ECS as the system provider. This includes logs like: SAP Security Audit Log (AS ABAP), HANA database, AS JAVA, ICM, SAP Web Dispatcher, SAP Cloud Connector, OS, SAP Gateway, 3rd party Database, Network, DNS, Proxy, Firewall

[← Back to Connectors Index](../connectors-index.md)
