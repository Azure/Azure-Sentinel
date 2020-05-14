# About
This folder tracks sample data of CEF format and can be pushed to Azure Log Analytics CommonEventFormat.

## Pushing CEF log data via CEF connector
To enable the CEF connector, deploy a dedicated proxy Linux machine (VM or on premises) to support the communication between your security solution (the product that sends the CEF messages) and Azure Sentinel.

Enable the CEF connector as follows:

1. Go to **Azure Sentinel**
2. Open the **Data Connectors** page and choose the relevant connector and click **Open connector page**
3. Follow the CEF instructions below (also in the CEF connector documentation).

_1. Install and configure Linux Syslog agent_

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Azure Sentinel.

_1.1 Select a Linux machine_

Select or create a Linux machine that Azure Sentinel will use as the proxy between your security solution and Azure Sentinel this machine can be on your on-prem environment, Azure or other clouds.

_1.2 Install the CEF collector on the Linux machine_

Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Azure Sentinel workspace.

Note:

1. Make sure that you have Python on your machine using the following command:

        python –version

2. You must have elevated permissions (sudo) on your machine <p>Run the following command to install and apply the CEF collector:

        sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef\_installer.py&&sudo python cef\_installer.py [WorkspaceID]_ [Workspace Primary Key]

_2. Forward Common Event Format (CEF) logs to Syslog agent_

2.1 Set your security solution to send Syslog messages in CEF format to the proxy machine. This varies from product to product and follow the process for your product. There are couple of ways to choose from pushing your logs

1. The agent can collect logs from multiple sources but must be installed on dedicated machine per the following diagram
![collect logs](syslog_step1.png)
2. Alternatively, you can deploy the agent manually on an existing Azure VM, on a VM in another cloud, or on an on-premises machine as shown in the diagram below
![deploy agent](syslog_step2.png)
2.2 Make sure to send the logs to port 514 TCP on the machine&#39;s IP address.

2.3 Outline specific steps custom for sending your product logs along with link to your (partner) product documentation on how customers should configure their agent to send CEF logs from the respective product into Azure Sentinel.

**Example connectors to refer to** : ZScaler

**Connector Validation Steps**

Follow the instructions to validate your connectivity:

1. Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.
Note: It may take about 20 minutes until the connection streams data to your workspace.
2. If the logs are not received, run the following connectivity validation script:
     1. Note:
        1. Make sure that you have Python on your machine using the following command:<p>
        _python –version_
        2. You must have elevated permissions (sudo) on your machine
     2. _sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef\_troubleshoot.py&&sudo python cef\_troubleshoot.py [WorkspaceID]_
3. From a data quality perspective,
     1. Ensure the data you send is complete and contains the same fields available in your product.
     2. Ensure the data is valid and easy to query using Log Analytics.

4. Design and validate a few key queries that lands the value of the data stream using Kusto Query Language. Share these as sample queries in the data connector.

To use TLS communication between the security solution and the Syslog machine, you will need to configure the Syslog daemon (rsyslog or syslog-ng) to communicate in TLS: [Encrypting Syslog Traffic with TLS - rsyslog](https://www.rsyslog.com/doc/v8-stable/tutorials/tls_cert_summary.html), [Encrypting log messages with TLS – syslog-ng](https://support.oneidentity.com/technical-documents/syslog-ng-open-source-edition/3.22/administration-guide/60#TOPIC-1209298).
