# Connect your WireX Systems NFP to Azure Sentinel

This article explains how to connect your WireX Systems NFP appliance to Azure Sentinel. The WireX Systems NFP data connector allows you to easily connect your WireX Systems NFP logs with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. 


> [!NOTE] Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward WireX Systems NFP logs to the Syslog agent  

Configure WireX Systems NFP to forward Syslog messages in CEF format to your Azure workspace via the Syslog agent.
1. Contact support for the proper configuration of your WireX Systems Network forensics platform.
2. To use the relevant schema in Log Analytics for the WireX Systems NFP search for CommonSecurityLog.
3. Continue to [STEP 3: Validate connectivity](connect-cef-verify.md).


## Next steps
In this document, you learned how to connect WireX Systems NFP to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.