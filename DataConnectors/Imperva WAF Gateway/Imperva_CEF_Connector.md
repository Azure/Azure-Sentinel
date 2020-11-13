# Connect your Imperva WAF Gateway to Azure Sentinel

This article explains how to connect your Imperva WAF Gateway appliance to Azure Sentinel. The Imperva WAF Gateway data connector allows you to easily connect your WAF Gateway logs with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. 

> !NOTE
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Forward Imperva WAF Gateway logs to the Syslog agent  

Configure Imperva WAF Gateway to forward Syslog messages in CEF format to your Azure workspace via the Syslog agent.

1. SecureSphere MX Configuration - The connector requires an Action Interface and Action Set to be created on the Imperva SecureSphere MX.  Refer to [this document](https://community.imperva.com/blogs/craig-burlingame1/2020/11/13/steps-for-enabling-imperva-waf-gateway-alert) to create the requirements.
2. Apply the Action Set - Apply the Action Set to any Security Policies you wish to have alerts for sent to Azure Sentinel.
3. Validate connection - Open Log Analytics to check if the logs are received using the CommonSecurityLog schema

## Next steps
In this document, you learned how to connect Imperva WAF Gateway to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.