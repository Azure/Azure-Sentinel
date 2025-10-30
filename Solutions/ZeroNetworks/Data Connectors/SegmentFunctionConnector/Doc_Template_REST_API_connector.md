# Connect your Zero Networks Segment to Microsoft Sentinel 



Zero Networks Segment connector allows you to easily connect all your Zero Networks Segment security solution logs with your Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This connecor will collect Zero Networks Segment Audit logs. Integration between Zero Networks Segment and Microsoft Sentinel makes use of REST API.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Configure and connect Zero Networks Segment 

Zero Networks Segment can integrate and export logs directly to Microsoft Sentinel.
1. In the Microsoft Sentinel portal, click Data connectors and select Zero Networks Segment and then Open connector page and follow the documented instructions.

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs ZNSegmentAudit.
To use the relevant schema in Log Analytics for the Zero Networks Segment, search for ZNSegmentAudit.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 

## Next steps
In this document, you learned how to connect Zero Networks Segment to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.

### Install as a solution (Preview)
1. In the Microsoft Sentinel portal, click Content Hub and search Zero Networks. 

2. Click Install.
         
For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and our [Guide to Building Microsoft Sentinel Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#readme).>

