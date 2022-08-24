# Connect your Zero Networks Access Orchestrator to Microsoft Sentinel 



Zero Networks Access Orchestrator connector allows you to easily connect all your Zero Networks Access Orchestrator security solution logs with your Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This connecor will collect Zero Networks Access Orchestrator Audit logs. Integration between Zero Networks Access Orchestrator and Microsoft Sentinel makes use of REST API.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Configure and connect Zero Networks Access Orchestrator 

Zero Networks Access Orchestrator can integrate and export logs directly to Microsoft Sentinel.
1. In the Microsoft Sentinel portal, click Data connectors and select Zero Networks Access Orchestrator and then Open connector page and follow the documented instructions.

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs ZNAccessOrchestratorAudit.
To use the relevant schema in Log Analytics for the Zero Networks Access Orchestrator, search for ZNAccessOrchestratorAudit.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 

## Next steps
In this document, you learned how to connect Zero Networks Access Orchestrator to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.

### Install as a solution (Preview)
1. In the Microsoft Sentinel portal, click Content Hub and search Zero Networks. 

2. Click Install.
         
For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and our [Guide to Building Microsoft Sentinel Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#readme).>

