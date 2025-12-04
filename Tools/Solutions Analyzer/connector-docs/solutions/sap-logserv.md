# SAP LogServ

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/announcing-limited-preview-of-sap-logserv-integration-with-microsoft/ba-p/13942180](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/announcing-limited-preview-of-sap-logserv-integration-with-microsoft/ba-p/13942180) |
| **Categories** | domains |
| **First Published** | 2025-02-17 |
| **Last Updated** | 2025-07-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP LogServ (RISE), S/4HANA Cloud private edition](../connectors/saplogserv.md)

**Publisher:** SAP SE

SAP LogServ is an SAP Enterprise Cloud Services (ECS) service aimed at collection, storage, forwarding and access of logs. LogServ centralizes the logs from all systems, applications, and ECS services used by a registered customer. 

 Main Features include:

Near Realtime Log Collection: With ability to integrate into Microsoft Sentinel as SIEM solution.

LogServ complements the existing SAP application layer threat monitoring and detections in Microsoft Sentinel with the log types owned by SAP ECS as the system provider. This includes logs like: SAP Security Audit Log (AS ABAP), HANA database, AS JAVA, ICM, SAP Web Dispatcher, SAP Cloud Connector, OS, SAP Gateway, 3rd party Database, Network, DNS, Proxy, Firewall

| | |
|--------------------------|---|
| **Tables Ingested** | `SAPLogServ_CL` |
| **Connector Definition Files** | [SAPLogServ.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ.json) |
| | [SAPLogServ_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ_PUSH_CCP/SAPLogServ_connectorDefinition.json) |

[→ View full connector details](../connectors/saplogserv.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SAPLogServ_CL` | [SAP LogServ (RISE), S/4HANA Cloud private edition](../connectors/saplogserv.md) |

[← Back to Solutions Index](../solutions-index.md)
