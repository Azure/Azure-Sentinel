# Gigamon Connector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Gigamon |
| **Support Tier** | Partner |
| **Support Link** | [https://www.gigamon.com/](https://www.gigamon.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md)

**Publisher:** Gigamon

Use this data connector to integrate with Gigamon Application Metadata Exporter (AMX) and get data sent directly to Microsoft Sentinel. 

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Gigamon Data Connector**

1. Application Metadata Exporter (AMX) application converts the output from the Application Metadata Intelligence (AMI) in CEF format into JSON format and sends it to the cloud tools and Kafka.
 2. The AMX application can be deployed only on a V Series Node and can be connected to Application Metadata Intelligence running on a physical node or a virtual machine.
 3. The AMX application and the AMI are managed by GigaVUE-FM. This application is supported on VMware ESXi, VMware NSX-T, AWS and Azure.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Gigamon_CL` |
| **Connector Definition Files** | [Connector_Analytics_Gigamon.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector/Data%20Connectors/Connector_Analytics_Gigamon.json) |

[→ View full connector details](../connectors/gigamondataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Gigamon_CL` | [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
