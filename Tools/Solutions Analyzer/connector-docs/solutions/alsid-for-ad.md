# Alsid For AD

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Alsid |
| **Support Tier** | Partner |
| **Support Link** | [https://www.alsid.com/contact-us/](https://www.alsid.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Alsid for Active Directory](../connectors/alsidforad.md)

**Publisher:** Alsid

Alsid for Active Directory connector allows to export Alsid Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.

It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://aka.ms/sentinel-alsidforad-parser) to create the Kusto Functions alias, **afad_parser**

**1. Configure the Syslog server**

You will first need a **linux Syslog** server that Alsid for AD will send logs to. Typically you can run **rsyslog** on **Ubuntu**.
 You can then configure this server as you wish, but it is recommended to be able to output AFAD logs in a separate file.
Alternatively you can use [this Quickstart template](https://azure.microsoft.com/resources/templates/alsid-syslog-proxy/) which will deploy the Syslog server and the Microsoft agent for you. If you do use this template, you can skip step 3.

**2. Configure Alsid to send logs to your Syslog server**

On your **Alsid for AD** portal, go to *System*, *Configuration* and then *Syslog*.
From there you can create a new Syslog alert toward your Syslog server.

Once this is done, check that the logs are correctly gathered on your server in a seperate file (to do this, you can use the *Test the configuration* button in the Syslog alert configuration in AFAD).
If you used the Quickstart template, the Syslog server will by default listen on port 514 in UDP and 1514 in TCP, without TLS.

**3. Install and onboard the Microsoft agent for Linux**

You can skip this step if you used the Quickstart template in step 1
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**4. Configure the logs to be collected by the agents**

Configure the agent to collect the logs.

1. Under workspace advanced settings **Configuration**, select **Data** and then **Custom Logs**.
2. Select **Apply below configuration to my machines** and click **Add**.
3. Upload a sample AFAD Syslog file from the **Linux** machine running the **Syslog** server and click **Next**, for your convenience, you can find such a file [here](https://github.com/Azure/azure-quickstart-templates/blob/master/alsid-syslog-proxy/logs/AlsidForAD.log).
4. Set the record delimiter to **New Line** if not already the case and click **Next**.
5. Select **Linux** and enter the file path to the **Syslog** file, click **+** then **Next**. If you used the Quickstart template in step 1, the default location of the file is `/var/log/AlsidForAD.log`.
6. Set the **Name** to *AlsidForADLog_CL* then click **Done** (Azure automatically adds *_CL* at the end of the name, there must be only one, make sure the name is not *AlsidForADLog_CL_CL*).

All of these steps are showcased [here](https://www.youtube.com/watch?v=JwV1uZSyXM4&feature=youtu.be) as an example
- **Open Syslog settings**

> You should now be able to receive logs in the *AlsidForADLog_CL* table, logs data can be parse using the **afad_parser()** function, used by all query samples, workbooks and analytic templates.

| | |
|--------------------------|---|
| **Tables Ingested** | `AlsidForADLog_CL` |
| **Connector Definition Files** | [AlsidForAD.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alsid%20For%20AD/Data%20Connectors/AlsidForAD.json) |

[→ View full connector details](../connectors/alsidforad.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AlsidForADLog_CL` | [Alsid for Active Directory](../connectors/alsidforad.md) |

[← Back to Solutions Index](../solutions-index.md)
