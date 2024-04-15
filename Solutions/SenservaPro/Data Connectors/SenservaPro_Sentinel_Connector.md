# Connect your SenservaPro to Azure Sentinel 



The SenservaPro connector allows you to connect SenservaPro Azure Active Directory focused advanced security analytics data with your Azure Sentinel, allowing you view dashboards from Senservaa, create custom alerts, and improve investigation with Hunting queries also provided by Senserva. The Senserva data is multi-tenant enabled. 


> [!NOTE]
>Data is stored in the geographic location of the workspace on which you are running Azure Sentinel.
>Senserva analytics data never leaves the tenant in which Senserva is installed.
>Integration between SenservaPro and Azure Sentinel makes use of the Log Analytics Workspace REST API.

## Configure and connect SenservaPro 

SenservaPro is fully integrated into Azure and exports logs directly to Azure Sentinel every time a Senserva monitored Azure Active Directory configuration changes, or account status changes due to something like a Risky User warning.
1. In the Azure Sentinel portal, click Data connectors and select 'SenservaPro' and then Open connector page.

2. You will install the data provider to the connector as part of your SenservaPro setup from [our Azure Marketplace offering.](https://azuremarketplace.microsoft.com/marketplace/apps/senservallc.senserva)


## Find your data

The data appears in Log Analytics under CustomLogs SenservaPro_CL after a successful connection is established. Senserva data  is continually updated automatically once the connection is established. To use the relevant schema in Log Analytics for the SenservaPro, search for SenservaPro_CL.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 


## Next steps
In this document you learned how to connect SenservaPro to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.

