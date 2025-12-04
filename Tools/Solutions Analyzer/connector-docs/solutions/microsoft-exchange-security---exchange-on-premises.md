# Microsoft Exchange Security - Exchange On-Premises

## Solution Information

| | |
|------------------------|-------|
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

### [Exchange Security Insights On-Premises Collector](../connectors/esi-exchangeonpremisescollector.md)

**Publisher:** Microsoft

### [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md)

**Publisher:** Microsoft

### [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

**Publisher:** Microsoft

### [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange Message Tracking Logs](../connectors/esi-opt6exchangemessagetrackinglogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange HTTP Proxy Logs](../connectors/esi-opt7exchangehttpproxylogs.md)

**Publisher:** Microsoft

[Option 7] - Using Azure Monitor Agent - You can stream HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you create custom alerts, and improve investigation. [Learn more](https://aka.ms/ESI_DataConnectorOptions)

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
