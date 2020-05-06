# About
This folder tracks sample data of CEF format and can be pushed to Azure Log Analytics CommonEventFormat 

## Linux Syslog Agent Configuration
Follow these following steps to install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Azure Sentinel.

Notice that the data from all regions will be stored in your workspace.

1. Select or create a Linux machine
Select or create a Linux machine that Azure Sentinel will use as the proxy between your security solution and Azure Sentinel this machine can be on your on-prem environment, Azure or other clouds.

2. Install the CEF collector on the Linux machine
Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Azure Sentinel workspace. The CEF collector colects CEF messages on port 514 TCP.

3. Make sure that you have Python on your machine using the following command: python –version. You must have elevated permissions (sudo) on your machine. Run the following command to install and apply the CEF collector:

        sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py f109320f-f1a0-4e3a-9df9-3f5367682eb4 RXYYY7ZlSsLF7MdwPZpe8WOJQzWpH9d4p2OhIFYh7a1ydpa2P5pdN1R5BFu8VVsGbLq4lz9Wot/aTGl6FRuReg==
4. Forward Common Event Format (CEF) logs to Syslog agent
Set your security solution to send Syslog messages in CEF format to the proxy machine. Make sure you send the logs to port 514 TCP on the machine's IP address.

5. Validate connection: Follow the instructions to validate your connectivity:

>* Open Log Analytics to check if the logs are received using the CommonSecurityLog schema. It may take about 20 minutes until the connection streams data to your workspace.
>* If the logs are not received, run the following connectivity validation script. Make sure that you have Python on your machine using the following command: python –version. You must have elevated permissions (sudo) on your machine. Run the following command to validate your connectivity:

        sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  f109320f-f1a0-4e3a-9df9-3f5367682eb4
6. Secure your machine: Make sure to configure the machine's security according to your organization's security policy
7. Your posted CEF log data can be viewed under CommonSecurityLog in Azure Sentinel logs or your Azure Log Analytics CEF logs.
