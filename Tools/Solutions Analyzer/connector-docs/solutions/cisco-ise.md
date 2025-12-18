# Cisco ISE

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md)

**Publisher:** Cisco

The Cisco Identity Services Engine (ISE) data connector provides the capability to ingest [Cisco ISE](https://www.cisco.com/c/en/us/products/security/identity-services-engine/index.html) events into Microsoft Sentinel. It helps you gain visibility into what is happening in your network, such as who is connected, which applications are installed and running, and much more. Refer to [Cisco ISE logging mechanism documentation](https://www.cisco.com/c/en/us/td/docs/security/ise/2-7/admin_guide/b_ise_27_admin_guide/b_ISE_admin_27_maintain_monitor.html#reference_BAFBA5FA046A45938810A5DF04C00591) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-ciscoise-parser) to create the Kusto Functions alias, **CiscoISEEvent**

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

**3. Configure Cisco ISE Remote Syslog Collection Locations**

[Follow these instructions](https://www.cisco.com/c/en/us/td/docs/security/ise/2-7/admin_guide/b_ise_27_admin_guide/b_ISE_admin_27_maintain_monitor.html#ID58) to configure remote syslog collection locations in your Cisco ISE deployment.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Cisco_ISE.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Data%20Connectors/Connector_Cisco_ISE.json) |

[→ View full connector details](../connectors/ciscoise.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md) |

[← Back to Solutions Index](../solutions-index.md)
