# Connect your <<Partner Appliance Name>> to Microsoft Sentinel 



<<Partner Appliance Name>> connector allows you to easily connect all your <<Partner Appliance Name>> security solution logs with your Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. <<Add additional specific insights this data connectivity provides to customers>>. Integration between <<Partner Appliance Name>> and Microsoft Sentinel makes use of REST API.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Configure and connect <<Partner Appliance Name>> 

<<Partner Appliance Name>> can integrate and export logs directly to Microsoft Sentinel.
1. In the Microsoft Sentinel portal, click Data connectors and select <<Partner Appliance Name>> and then Open connector page.

2. <If you have documentation to connect on your side link to that. If you don't, provide detailed steps to discover the connection in your product. For more information, see our [generic REST API-based data connector documentation](https://docs.microsoft.com/azure/sentinel/connect-rest-api-template).>

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs <<schema name>>.
To use the relevant schema in Log Analytics for the <<Partner Appliance Name>>, search for <<Schema name>>.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 


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

