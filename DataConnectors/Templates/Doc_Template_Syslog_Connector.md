# Connect your <<Partner Appliance Name>> to Azure Sentinel

This article explains how to connect your <<Partner Appliance Name>> appliance to Azure Sentinel. The <<Partner Appliance Name>> data connector allows you to easily connect your <<Partner Appliance Name>> logs with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. <<Add additional specific insights this data connectivity provides to customers>>. Integration between <<Partner Appliance Name>> and Azure Sentinel makes use of Syslog.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward <<Partner Appliance Name>> logs to the Syslog agent  

Configure <<Partner Appliance Name>> to forward Syslog messages to your Azure workspace via the Syslog agent.
1. <Add specific steps on how customers can configure your appliance to send logs to Syslog. Adjust numbering below as needed for the last steps that follows.>
2. In the Azure portal, navigate to Azure Sentinel > Data connectors and then select the <<Partner Appliance Name>> connector.
3. Select Open connector page.
4. Follow the instructions on the <<Partner Appliance Name>> page.

## Find your data

After a successful connection is established, the data appears in Log Analytics under Syslog.

## Validate connectivity
It may take upwards of 20 minutes until your logs start to appear in Log Analytics. 

## Next steps
In this document, you learned how to connect <<Partner Appliance Name>> to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.