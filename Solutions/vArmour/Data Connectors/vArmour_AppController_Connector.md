# Connect your vArmour Application Controller to Azure Sentinel

This article explains how to connect your vArmour Application Controller appliance to Azure Sentinel. The vArmour data connector allows you to easily connect your Application Controller logs with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. Integration between the Application Controller and Azure Sentinel makes use of CEF.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward vArmour Application Controller logs to the Syslog agent

Configure the Application Controller to forward Syslog messages in CEF format to your Azure workspace via the Syslog agent.
1. Download the user guide from https://support.varmour.com/hc/en-us/articles/360057444831-vArmour-Application-Controller-6-0-User-Guide
2. In the user guide - refer to "Configuring Syslog for Monitoring and Violations" and follow steps 1 to 3.
3. To use the relevant schema in Log Analytics for the Application Controller search for CommonSecurityLog.
4. Continue to [STEP 3: Validate connectivity](connect-cef-verify.md).


## Next steps
In this document, you learned how to connect the Application Controller to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.
