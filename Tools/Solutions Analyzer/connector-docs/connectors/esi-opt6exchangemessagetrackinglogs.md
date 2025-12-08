# Microsoft Exchange Message Tracking Logs

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt6ExchangeMessageTrackingLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`MessageTrackingLog_CL`](../tables-index.md#messagetrackinglog_cl) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt6ExchangeMessageTrackingLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt6ExchangeMessageTrackingLogs.json) |

[Option 6] - Using Azure Monitor Agent - You can stream all Exchange Message Tracking from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. Those logs can be used to track the flow of messages in your Exchange environment. This data connector is based on the option 6 of the [Microsoft Exchange Security wiki](https://aka.ms/ESI_DataConnectorOptions).

[← Back to Connectors Index](../connectors-index.md)
