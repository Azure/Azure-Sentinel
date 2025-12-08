#  Microsoft Active-Directory Domain Controllers Security Event Logs

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt34DomainControllersSecurityEventLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityEvent`](../tables-index.md#securityevent) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt34DomainControllersSecurityEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt34DomainControllersSecurityEventLogs.json) |

[Option 3 & 4] - Using Azure Monitor Agent -You can stream a part or all Domain Controllers Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

[← Back to Connectors Index](../connectors-index.md)
