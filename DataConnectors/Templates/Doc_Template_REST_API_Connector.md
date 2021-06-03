# Connect your <<Partner Appliance Name>> to Azure Sentinel 



<<Partner Appliance Name>> connector allows you to easily connect all your <<Partner Appliance Name>> security solution logs with your Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. <<Add additional specific insights this data connectivity provides to customers>>. Integration between <<Partner Appliance Name>> and Azure Sentinel makes use of REST API.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Configure and connect <<Partner Appliance Name>> 

<<Partner Appliance Name>> can integrate and export logs directly to Azure Sentinel.
1. In the Azure Sentinel portal, click Data connectors and select <<Partner Appliance Name>> and then Open connector page.

2. <If you have documentation to connect on your side link to that - refer to 'https://docs.microsoft.com/azure/sentinel/connect-f5-big-ip' as an example for this section>

ELSE

2. <Provide detailed steps to discover the connection in your product with screenshots - refer to 'https://docs.microsoft.com/azure/sentinel/connect-symantec' as an example for this section>


## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs <<schema name>>.
To use the relevant schema in Log Analytics for the <<Partner Appliance Name>>, search for <<Schema name>>.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 


## Next steps
In this document, you learned how to connect <<Partner Appliance Name>> to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.

