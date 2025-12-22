# [Deprecated] McAfee ePolicy Orchestrator (ePO)

| | |
|----------|-------|
| **Connector ID** | `McAfeeePO` |
| **Publisher** | McAfee |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [McAfee ePolicy Orchestrator](../solutions/mcafee-epolicy-orchestrator.md) |
| **Connector Definition Files** | [Connector_McAfee_ePO.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Data%20Connectors/Connector_McAfee_ePO.json) |

The McAfee ePolicy Orchestrator data connector provides the capability to ingest [McAfee ePO](https://www.mcafee.com/enterprise/en-us/products/epolicy-orchestrator.html) events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.mcafee.com/bundle/epolicy-orchestrator-landing/page/GUID-0C40020F-5B7F-4549-B9CC-0E017BC8797F.html) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>This data connector depends on a parser based on a Kusto Function to work as expected [**McAfeeEPOEvent**](https://aka.ms/sentinel-McAfeeePO-parser) which is deployed with the Microsoft Sentinel Solution.

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

**3. Configure McAfee ePolicy Orchestrator event forwarding to Syslog server**

[Follow these instructions](https://kcm.trellix.com/corporate/index?page=content&id=KB87927) to add register syslog server.

[← Back to Connectors Index](../connectors-index.md)
