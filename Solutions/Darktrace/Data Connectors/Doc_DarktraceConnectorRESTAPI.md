<!-- Taken from https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Templates/Doc_Template_REST_API_Connector.md -->

# Connect Darktrace to Microsoft Sentinel 


The Darktrace Data Connector allows you to easily connect your AI detections from within Darktrace's Product Suite with your Microsoft Sentinel workspace, to view dashboards, create custom alerts, and improve investigation. The connector allows Darktrace to send AI Analyst Incidents, Model Breaches, Email Alerts and System Health Alerts to Sentinel. Integration between Darktrace and Microsoft Sentinel makes use of REST API: data is sent from Darktrace to Sentinel using HTTPs.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Configure and connect Darktrace to Microsoft Sentinel

Darktrace can integrate and export alerting data directly to Microsoft Sentinel.

1. In the Microsoft Sentinel portal, click Data connectors and select "Darktrace Connector for Microsoft Sentinel REST API" and then Open connector page.

2. Follow the configuration steps in the configuration wizard. Detailed configuration steps can be found on the [Darktrace Customer Portal](https://customerportal.darktrace.com/product-guides/main/microsoft-sentinel-introduction).

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs `darktrace_model_alerts_CL`.
To use the relevant schema in Log Analytics for Darktrace, search for `darktrace_model_alerts_CL`.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. You can look for test alerts sent during connection validation by using one of the sample queries shipping with the connector.


## Next steps
In this document, you learned how to connect Darktrace to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.

### Install as a solution (Preview)

To get the most out of the Data Connector, consider installing the Darktrace Solution for Microsoft Sentinel from the Sentinel Content Hub. The solution will allow you to operationalize Darktrace data in Microsoft Sentinel by visualising alerting using Workbooks as well as turning Darktrace alerting into Microsoft Sentinel Incident and Alerts.

For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and visit the [Azure Marketplace](https://azure.microsoft.com/marketplace/)
