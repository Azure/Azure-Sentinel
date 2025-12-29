# Microsoft Exchange Security - Exchange On-Premises

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises) |

## Data Connectors

This solution provides **8 data connector(s)**.

### [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)

**Publisher:** Microsoft

Deprecated, use the 'ESI-Opt' dataconnectors. You can stream all Exchange Audit events, IIS Logs, HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Event` |
| | `ExchangeHttpProxy_CL` |
| | `MessageTrackingLog_CL` |
| | `SecurityEvent` |
| | `W3CIISLog` |
| **Connector Definition Files** | [ESI-ExchangeAdminAuditLogEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeAdminAuditLogEvents.json) |

[→ View full connector details](../connectors/esi-exchangeadminauditlogevents.md)

### [Exchange Security Insights On-Premises Collector](../connectors/esi-exchangeonpremisescollector.md)

**Publisher:** Microsoft

Connector used to push Exchange On-Premises Security configuration for Microsoft Sentinel Analysis

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ESIExchangeConfig_CL` |
| **Connector Definition Files** | [ESI-ExchangeOnPremisesCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeOnPremisesCollector.json) |

[→ View full connector details](../connectors/esi-exchangeonpremisescollector.md)

### [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

**Publisher:** Microsoft

[Option 1] - Using Azure Monitor Agent - You can stream all Exchange Audit events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Event` |
| **Connector Definition Files** | [ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json) |

[→ View full connector details](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

### [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md)

**Publisher:** Microsoft

[Option 2] - Using Azure Monitor Agent - You can stream all Exchange Security & Application Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Event` |
| **Connector Definition Files** | [ESI-Opt2ExchangeServersEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt2ExchangeServersEventLogs.json) |

[→ View full connector details](../connectors/esi-opt2exchangeserverseventlogs.md)

### [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

**Publisher:** Microsoft

[Option 3 & 4] - Using Azure Monitor Agent -You can stream a part or all Domain Controllers Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityEvent` |
| **Connector Definition Files** | [ESI-Opt34DomainControllersSecurityEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt34DomainControllersSecurityEventLogs.json) |

[→ View full connector details](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

### [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md)

**Publisher:** Microsoft

[Option 5] - Using Azure Monitor Agent - You can stream all IIS Logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `W3CIISLog` |
| **Connector Definition Files** | [ESI-Opt5ExchangeIISLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt5ExchangeIISLogs.json) |

[→ View full connector details](../connectors/esi-opt5exchangeiislogs.md)

### [Microsoft Exchange Message Tracking Logs](../connectors/esi-opt6exchangemessagetrackinglogs.md)

**Publisher:** Microsoft

[Option 6] - Using Azure Monitor Agent - You can stream all Exchange Message Tracking from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. Those logs can be used to track the flow of messages in your Exchange environment. This data connector is based on the option 6 of the [Microsoft Exchange Security wiki](https://aka.ms/ESI_DataConnectorOptions).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MessageTrackingLog_CL` |
| **Connector Definition Files** | [ESI-Opt6ExchangeMessageTrackingLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt6ExchangeMessageTrackingLogs.json) |

[→ View full connector details](../connectors/esi-opt6exchangemessagetrackinglogs.md)

### [Microsoft Exchange HTTP Proxy Logs](../connectors/esi-opt7exchangehttpproxylogs.md)

**Publisher:** Microsoft

[Option 7] - Using Azure Monitor Agent - You can stream HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you create custom alerts, and improve investigation. [Learn more](https://aka.ms/ESI_DataConnectorOptions)

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ExchangeHttpProxy_CL` |
| **Connector Definition Files** | [ESI-Opt7ExchangeHTTPProxyLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt7ExchangeHTTPProxyLogs.json) |

[→ View full connector details](../connectors/esi-opt7exchangehttpproxylogs.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeConfig_CL` | [Exchange Security Insights On-Premises Collector](../connectors/esi-exchangeonpremisescollector.md) |
| `Event` | [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md), [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `ExchangeHttpProxy_CL` | [Microsoft Exchange HTTP Proxy Logs](../connectors/esi-opt7exchangehttpproxylogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `MessageTrackingLog_CL` | [Microsoft Exchange Message Tracking Logs](../connectors/esi-opt6exchangemessagetrackinglogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `SecurityEvent` | [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `W3CIISLog` | [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.3.2       | 26-03-2025                     | Update documentation link to new repository     |
| 3.3.0       | 26-08-2024                     | Add Compare in Exchange Security Review. Create DataConnectors for Azure Monitor Agent. Correct bugs      |
| 3.2.0       | 09-04-2024                     | Explode "ExchangeAdminAuditLogEvents" dataconnector to multiple simplier dataconnectors      |
| 3.1.5       | 26-04-2024                     | Fix Typpo in DataConnector                  |
|             |                                | Repackaged for fix on parser in maintemplate to have old parsername and parentid                    |
| 3.1.4       | 18-04-2024                     | Repackaged for parser issue while redeployment      |
| 3.1.3       | 10-04-2024                     | Updated DataConnector last Log indicator and IsConnected queries by including Application and System Log Event Types      |
| 3.1.2       | 20-02-2024                     | Correct DataConnector last Log indicator and IsConnected queries      |
| 3.1.1       | 18-12-2023                     | Update Parsers parameters         |
| 3.1.0       | 01-11-2023                     | Added **Watchlist** to track activities on VIPs' Mailboxes. Change ExchangeAuditLog parser to work without watchlist and searching all type of VIP information         |
| 3.0.1       | 13-09-2023                     | Readme file for **Parsers** and typo correction                      |
| 3.0.0       | 23-08-2023                     | ExchangeEnvironmentList parser name corrected in **Workbooks**. |

[← Back to Solutions Index](../solutions-index.md)
