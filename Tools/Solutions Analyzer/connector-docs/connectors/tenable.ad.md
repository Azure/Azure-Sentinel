# Tenable.ad

| | |
|----------|-------|
| **Connector ID** | `Tenable.ad` |
| **Publisher** | Tenable |
| **Tables Ingested** | [`Tenable_ad_CL`](../tables-index.md#tenable_ad_cl) |
| **Used in Solutions** | [TenableAD](../solutions/tenablead.md) |
| **Connector Definition Files** | [Tenable.ad.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableAD/Data%20Connectors/Tenable.ad.json) |

Tenable.ad connector allows to export Tenable.ad Indicators of Exposures, trailflow and Indicators of Attacks logs to Azure Sentinel in real time.

It provides a data parser to manipulate the logs more easily. The different workbooks ease your Active Directory monitoring and provide different ways to visualize the data. The analytic templates allow to automate responses regarding different events, exposures, or attacks.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Access to Tenable.ad Configuration**: Permissions to configure syslog alerting engine

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>This data connector depends on a parser based on a Kusto Function to work as expected. [Follow these steps](https://raw.githubusercontent.com/tenable/Azure-Sentinel/Tenable.ad-connector/Solutions/TenableAD/Parsers/afad_parser.kql) to create the Kusto Functions alias, **afad_parser**

**1. Configure the Syslog server**

You will first need a **linux Syslog** server that Tenable.ad will send logs to. Typically you can run **rsyslog** on **Ubuntu**.
 You can then configure this server as you wish, but it is recommended to be able to output Tenable.ad logs in a separate file.

Configure rsyslog to accept logs from your Tenable.ad IP address.:

```shell
sudo -i

# Set Tenable.ad source IP address
export TENABLE_AD_IP={Enter your IP address}

# Create rsyslog configuration file
cat > /etc/rsyslog.d/80-tenable.conf << EOF
\$ModLoad imudp
\$UDPServerRun 514
\$ModLoad imtcp
\$InputTCPServerRun 514
\$AllowedSender TCP, 127.0.0.1, $TENABLE_AD_IP
\$AllowedSender UDP, 127.0.0.1, $TENABLE_AD_IP
\$template MsgTemplate,"%TIMESTAMP:::date-rfc3339% %HOSTNAME% %programname%[%procid%]:%msg%\n"
\$template remote-incoming-logs, "/var/log/%PROGRAMNAME%.log"
*.* ?remote-incoming-logs;MsgTemplate
EOF

# Restart rsyslog
systemctl restart rsyslog
```

**2. Install and onboard the Microsoft agent for Linux**

The OMS agent will receive the Tenable.ad syslog events and publish it in Sentinel :
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**3. Check agent logs on the Syslog server**

```shell
tail -f /var/opt/microsoft/omsagent/log/omsagent.log
```

**4. Configure Tenable.ad to send logs to your Syslog server**

On your **Tenable.ad** portal, go to *System*, *Configuration* and then *Syslog*.
From there you can create a new Syslog alert toward your Syslog server.

Once this is done, check that the logs are correctly gathered on your server in a separate file (to do this, you can use the *Test the configuration* button in the Syslog alert configuration in Tenable.ad).
If you used the Quickstart template, the Syslog server will by default listen on port 514 in UDP and 1514 in TCP, without TLS.

**5. Configure the custom logs**

Configure the agent to collect the logs.

1. In Sentinel, go to **Configuration** -> **Settings** -> **Workspace settings** -> **Custom logs**.
2. Click **Add custom log**.
3. Upload a sample Tenable.ad.log Syslog file from the **Linux** machine running the **Syslog** server and click **Next**
4. Set the record delimiter to **New Line** if not already the case and click **Next**.
5. Select **Linux** and enter the file path to the **Syslog** file, click **+** then **Next**. The default location of the file is `/var/log/Tenable.ad.log` if you have a Tenable version <3.1.0, you must also add this linux file location `/var/log/AlsidForAD.log`.
6. Set the **Name** to *Tenable_ad_CL* (Azure automatically adds *_CL* at the end of the name, there must be only one, make sure the name is not *Tenable_ad_CL_CL*).
7. Click **Next**, you will see a resume, then click **Create**

**6. Enjoy !**

> You should now be able to receive logs in the *Tenable_ad_CL* table, logs data can be parse using the **afad_parser()** function, used by all query samples, workbooks and analytic templates.

[← Back to Connectors Index](../connectors-index.md)
