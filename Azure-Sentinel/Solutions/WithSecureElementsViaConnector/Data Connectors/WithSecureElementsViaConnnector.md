# Connect your WithSecure Elements Connector to Microsoft Sentinel

This article explains how to connect your WithSecure Elements Connector appliance to Microsoft Sentinel. The WithSecure Elements Connector data connector allows you to easily connect your WithSecure Elements logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

**Note**: Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Forward WithSecure Elements logs to the Syslog agent

Configure With Secure Elements Connector to forward Syslog messages in CEF format to your Log Analytics workspace via the Syslog agent.
1. Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your WithSecurity solution and Sentinel. The machine can be on-prem environment, Microsoft Azure or other cloud based. Linux needs to have `syslog-ng` and `python`/`python3` installed.
2. Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP. You must have elevated permissions (sudo) on your machine.
3. Go to EPP in WithSecure Elements Portal. Then navigate to Downloads and in Elements Connector section click 'Create subscription key' button. You can check Your subscription key in Subscriptions.
4. In Downloads in WithSecure Elements Connector section select correct installer and download it.
5. When in EPP open account settings in top right corner. Then select Get management API key. If key has been created earlier it can be read there as well.
6. To install Elements Connector follow [Elements Connector Docs](https://help.f-secure.com/product.html#business/connector/latest/en/concept_BA55FDB13ABA44A8B16E9421713F4913-latest-en).
7. If api access has not been configured during installation follow [Configuring API access for Elements Connector](https://help.f-secure.com/product.html#business/connector/latest/en/task_F657F4D0F2144CD5913EE510E155E234-latest-en).
8. Go to EPP, then Profiles, then use For Connector from where you can see the connector profiles. Create a new profile (or edit an existing not read-only profile). In Event forwarding enable it. SIEM system address: **127.0.0.1:514**. Set format to **Common Event Format**. Protocol is **TCP**. Save profile and assign it to Elements Connector in Devices tab.
9. To use the relevant schema in Log Analytics for the WithSecure Elements Connector, search for CommonSecurityLog.
10. Continue with [validating your CEF connectivity](https://docs.microsoft.com/azure/sentinel/troubleshooting-cef-syslog?tabs=rsyslog#validate-cef-connectivity).

## Next steps
In this document, you learned how to connect WithSecurity Elements Connector to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.
