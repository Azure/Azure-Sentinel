# Connect your Zimperium Mobile Threat Defense to Azure Sentinel



Zimperium Mobile Threat Defense connector gives you the ability to connect the Zimperium threat log with Azure Sentinel to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's mobile threat landscape and enhances your security operation capabilities.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Configure and connect Zimperium Mobile Threat Defense

Zimperium Mobile Threat Defense can integrate and export logs directly to **Azure Sentinel**.
1. In the Azure Sentinel portal, click Data connectors and select **Zimperium Mobile Threat Defense**.

2. Select **Open connector page**.

3. Follow the instructions on the **Zimperium Mobile Threat Defense** connector page.


## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs ZimperiumThreatLog_CL and ZimperiumMitigationLog_CL.
To use the relevant schema in Log Analytics for the Zimperium Mobile Threat Defense, search for ZimperiumThreatLog_CL and ZimperiumMitigationLog_CL.

## Validate connectivity
It may take upwards of 20 minutes until your logs start to appear in Log Analytics.


## Next steps
In this document, you learned how to connect Zimperium Mobile Threat Defense to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:

- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.

To learn more about Zimperium, see the following:

- [Zimperium] (https://zimperium.com)
- [Zimperium Mobile Security Blog] (https://blog.zimperium.com)
- [Customer Support Portal] (https://support.zimperium.com)
