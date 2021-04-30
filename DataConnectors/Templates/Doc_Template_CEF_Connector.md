# Connect your <<Partner Appliance Name>> to Azure Sentinel

This article explains how to connect your <<Partner Appliance Name>> appliance to Azure Sentinel. The <<Partner Appliance Name>> data connector allows you to easily connect your <<Partner Appliance Name>> logs with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. <<Add additional specific insights this data connectivity provides to customers>> 


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward <<Partner Appliance Name>> logs to the Syslog agent  

Configure <<Partner Appliance Name>> to forward Syslog messages in CEF format to your Azure workspace via the Syslog agent.
1. <Add specific steps on how customers can configure your appliance to send logs to Syslog - refer to 'https://docs.microsoft.com/azure/sentinel/connect-paloalto' as an example for this section. Adjust numbering below as needed for the last two steps that follows.>
2. To use the relevant schema in Log Analytics for the <<Partner Appliance Name>>, search for CommonSecurityLog.
3. Continue to [STEP 3: Validate connectivity](connect-cef-verify.md).


## Next steps
In this document, you learned how to connect <<Partner Appliance Name>> to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.