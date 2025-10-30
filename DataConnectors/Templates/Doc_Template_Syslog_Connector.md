# Connect your <<Partner Appliance Name>> to Microsoft Sentinel

This article explains how to connect your <<Partner Appliance Name>> appliance to Microsoft Sentinel. The <<Partner Appliance Name>> data connector allows you to easily connect your <<Partner Appliance Name>> logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. <<Add additional specific insights this data connectivity provides to customers>>. Integration between <<Partner Appliance Name>> and Microsoft Sentinel makes use of Syslog.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward <<Partner Appliance Name>> logs to the Syslog agent  

Configure <<Partner Appliance Name>> to forward Syslog messages to your Azure workspace via the Syslog agent.
1. <Add specific steps on how customers can configure your appliance to send logs to Syslog. Adjust numbering below as needed for the last steps that follows.>
2. In the Azure portal, navigate to Azure Microsoft > Data connectors and then select the <<Partner Appliance Name>> connector.
3. Select Open connector page.
4. Follow the instructions on the <<Partner Appliance Name>> page.

## Find your data

After a successful connection is established, the data appears in Log Analytics under Syslog.

## Validate connectivity
It may take upwards of 20 minutes until your logs start to appear in Log Analytics. 

## Next steps
In this document, you learned how to connect <<Partner Appliance Name>> to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.

<### Install as a solution (Preview)

Include this section if you are planning on publishing your data connector as a Microsoft Sentinel solution. Microsoft Sentinel solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Microsoft Sentinel. For example, use solutions to deliver your data connector packaged with related analytics rules, workbooks, playbooks, and more. 
         
- When relevant, add instructions for installing your solution, either from the Azure Marketplace, or from the Microsoft Sentinel content hub. 
- If your solution is being published to the content hub, also open a PR to have it listed in our [content hub catalog](https://docs.microsoft.com/azure/sentinel/sentinel-solutions-catalog). On the docs page, click Edit to open your PR.
         
For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and our [Guide to Building Microsoft Sentinel Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#readme).>
