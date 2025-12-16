# [Deprecated] Citrix ADC (former NetScaler)

| | |
|----------|-------|
| **Connector ID** | `CitrixADC` |
| **Publisher** | Citrix |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Citrix ADC](../solutions/citrix-adc.md) |
| **Connector Definition Files** | [Connector_CitrixADC_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Data%20Connectors/Connector_CitrixADC_syslog.json) |

The [Citrix ADC (former NetScaler)](https://www.citrix.com/products/citrix-adc/) data connector provides the capability to ingest Citrix ADC logs into Microsoft Sentinel. If you want to ingest Citrix WAF logs into Microsoft Sentinel, refer this [documentation](https://learn.microsoft.com/azure/sentinel/data-connectors/citrix-waf-web-app-firewall)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** 1. This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias CitrixADCEvent and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Parsers/CitrixADCEvent.yaml), this function maps Citrix ADC (former NetScaler) events to Advanced Security Information Model [ASIM](https://docs.microsoft.com/azure/sentinel/normalization). The function usually takes 10-15 minutes to activate after solution installation/update. 

>**NOTE:** 2. This parser requires a watchlist named **`Sources_by_SourceType`** 

> i. If you don't have watchlist already created, please click [here](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdeploy%2FWatchlists%2FASimSourceType.json) to create. 

> ii. Open watchlist **`Sources_by_SourceType`** and add entries for this data source.

> iii. The SourceType value for CitrixADC is **`CitrixADC`**. 

> You can refer [this](https://learn.microsoft.com/en-us/azure/sentinel/normalization-manage-parsers?WT.mc_id=Portal-fx#configure-the-sources-relevant-to-a-source-specific-parser) documentation for more details

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
 1. Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
 2. Select **Apply below configuration to my machines** and select the facilities and severities.
 3.  Click **Save**.
- **Open Syslog settings**

**3. Configure Citrix ADC to forward logs via Syslog**

3.1 Navigate to **Configuration tab > System > Auditing > Syslog > Servers tab**

 3.2 Specify **Syslog action name**.

 3.3 Set IP address of remote Syslog server and port.

 3.4 Set **Transport type** as **TCP** or **UDP** depending on your remote Syslog server configuration.

 3.5 You can refer Citrix ADC (former NetScaler) [documentation](https://docs.netscaler.com/) for more details.

**4. Check logs in Microsoft Sentinel**

Open Log Analytics to check if the logs are received using the Syslog schema.

>**NOTE:** It may take up to 15 minutes before new logs will appear in Syslog table.

[← Back to Connectors Index](../connectors-index.md)
