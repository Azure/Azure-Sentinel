# OracleDatabaseAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md)

**Publisher:** Oracle

The Oracle DB Audit data connector provides the capability to ingest [Oracle Database](https://www.oracle.com/database/technologies/) audit events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/dbseg/introduction-to-auditing.html#GUID-94381464-53A3-421B-8F13-BD171C867405) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Oracle Database Audit and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Parsers/OracleDatabaseAuditEvent.txt). The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.

1.  Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
2.  Select **Apply below configuration to my machines** and select the facilities and severities.
3.  Click **Save**.
- **Open Syslog settings**

**3. Configure Oracle Database Audit events to be sent to Syslog**

Follow the below instructions 

 1. Create the Oracle database [Follow these steps.](https://learn.microsoft.com/en-us/azure/virtual-machines/workloads/oracle/oracle-database-quick-create) 

 2. Login to Oracle database created from the above step [Follow these steps.](https://docs.oracle.com/cd/F49540_01/DOC/server.815/a67772/create.htm) 

 3. Enable unified logging over syslog by **Alter the system to enable unified logging** [Following these steps.](https://docs.oracle.com/en/database/oracle/oracle-database/21/refrn/UNIFIED_AUDIT_COMMON_SYSTEMLOG.html#GUID-9F26BC8E-1397-4B0E-8A08-3B12E4F9ED3A) 

 4. Create and  **enable an Audit policy for unified auditing** [Follow these steps.](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-AUDIT-POLICY-Unified-Auditing.html#GUID-8D6961FB-2E50-46F5-81F7-9AEA314FC693) 

 5. **Enabling syslog and Event Viewer** Captures for the Unified Audit Trail [Follow these steps.](https://docs.oracle.com/en/database/oracle/oracle-database/18/dbseg/administering-the-audit-trail.html#GUID-3EFB75DB-AE1C-44E6-B46E-30E5702B0FC4)

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_OracleDatabaseAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Data%20Connectors/Connector_OracleDatabaseAudit.json) |

[→ View full connector details](../connectors/oracledatabaseaudit.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md) |

[← Back to Solutions Index](../solutions-index.md)
