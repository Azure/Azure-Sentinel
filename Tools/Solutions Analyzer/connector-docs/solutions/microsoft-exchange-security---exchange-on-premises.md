# Microsoft Exchange Security - Exchange On-Premises

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises) |\n\n## Data Connectors

This solution provides **8 data connector(s)**.

### [Deprecated] Microsoft Exchange Logs and Events

**Publisher:** Microsoft

Deprecated, use the 'ESI-Opt' dataconnectors. You can stream all Exchange Audit events, IIS Logs, HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

**Tables Ingested:**

- `Event`
- `ExchangeHttpProxy_CL`
- `MessageTrackingLog_CL`
- `SecurityEvent`
- `W3CIISLog`

**Connector Definition Files:**

- [ESI-ExchangeAdminAuditLogEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeAdminAuditLogEvents.json)

### Exchange Security Insights On-Premises Collector

**Publisher:** Microsoft

Connector used to push Exchange On-Premises Security configuration for Microsoft Sentinel Analysis

**Tables Ingested:**

- `ESIExchangeConfig_CL`

**Connector Definition Files:**

- [ESI-ExchangeOnPremisesCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeOnPremisesCollector.json)

### Microsoft Exchange Admin Audit Logs by Event Logs

**Publisher:** Microsoft

[Option 1] - Using Azure Monitor Agent - You can stream all Exchange Audit events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

**Tables Ingested:**

- `Event`

**Connector Definition Files:**

- [ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json)

### Microsoft Exchange Logs and Events

**Publisher:** Microsoft

[Option 2] - Using Azure Monitor Agent - You can stream all Exchange Security & Application Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

**Tables Ingested:**

- `Event`

**Connector Definition Files:**

- [ESI-Opt2ExchangeServersEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt2ExchangeServersEventLogs.json)

###  Microsoft Active-Directory Domain Controllers Security Event Logs

**Publisher:** Microsoft

[Option 3 & 4] - Using Azure Monitor Agent -You can stream a part or all Domain Controllers Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

**Tables Ingested:**

- `SecurityEvent`

**Connector Definition Files:**

- [ESI-Opt34DomainControllersSecurityEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt34DomainControllersSecurityEventLogs.json)

### IIS Logs of Microsoft Exchange Servers

**Publisher:** Microsoft

[Option 5] - Using Azure Monitor Agent - You can stream all IIS Logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

**Tables Ingested:**

- `W3CIISLog`

**Connector Definition Files:**

- [ESI-Opt5ExchangeIISLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt5ExchangeIISLogs.json)

### Microsoft Exchange Message Tracking Logs

**Publisher:** Microsoft

[Option 6] - Using Azure Monitor Agent - You can stream all Exchange Message Tracking from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. Those logs can be used to track the flow of messages in your Exchange environment. This data connector is based on the option 6 of the [Microsoft Exchange Security wiki](https://aka.ms/ESI_DataConnectorOptions).

**Tables Ingested:**

- `MessageTrackingLog_CL`

**Connector Definition Files:**

- [ESI-Opt6ExchangeMessageTrackingLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt6ExchangeMessageTrackingLogs.json)

### Microsoft Exchange HTTP Proxy Logs

**Publisher:** Microsoft

[Option 7] - Using Azure Monitor Agent - You can stream HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you create custom alerts, and improve investigation. [Learn more](https://aka.ms/ESI_DataConnectorOptions)

**Tables Ingested:**

- `ExchangeHttpProxy_CL`

**Connector Definition Files:**

- [ESI-Opt7ExchangeHTTPProxyLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt7ExchangeHTTPProxyLogs.json)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeConfig_CL` | Exchange Security Insights On-Premises Collector |
| `Event` | 3 connector(s) |
| `ExchangeHttpProxy_CL` | 2 connector(s) |
| `MessageTrackingLog_CL` | 2 connector(s) |
| `SecurityEvent` | 2 connector(s) |
| `W3CIISLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n