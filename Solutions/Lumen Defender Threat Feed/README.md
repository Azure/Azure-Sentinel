[![Lumen](Workbooks/Images/Logo/Lumen.svg)](https://www.lumen.com/)

# Lumen Defender Threat Feed for Microsoft Sentinel

Within a SIEM like Microsoft Sentinel, threat indicators (IoCs) help correlate known-bad artifacts—such as IPs, domains, URLs, and file hashes—with activity in your environment. Lumen’s Black Lotus Labs® (BLL) harnesses unmatched network visibility and machine intelligence to produce high-confidence indicators that can be operationalized at scale for detection and investigation.

Learn more:

- Black Lotus Labs overview: [https://www.lumen.com/en-us/security/black-lotus-labs.html](https://www.lumen.com/en-us/security/black-lotus-labs.html)
- BLL blog archive: [https://blog.lumen.com/black-lotus-labs/](https://blog.lumen.com/black-lotus-labs/)
- BLL on X/Twitter: [https://twitter.com/blacklotuslabs](https://twitter.com/blacklotuslabs)

## Key features

Lumen Defender Threat Feed for Microsoft Sentinel offers powerful intelligence capabilities designed for security operations:

### Lumen Defender Threat Feed Data Connector

- The Lumen Defender Threat Feed connector (Azure Durable Functions) pulls indicators from Lumen’s Threat Feed API and writes them to the Sentinel Threat Intelligence store via the STIX Objects Upload API.
- Microsoft Sentinel analytic rules correlate Lumen indicators with your logs and create alerts/incidents for matches.

### Threat Research Workbook (Visibility)

- The Lumen workbook surfaces ingestion trends, active indicators by type, risk distribution, tags, sightings across curated tables, and correlated alerts/incidents.

### Hunting (Proactive)

- Included hunting queries help you pivot on a suspicious indicator across common data sources (e.g., CommonSecurityLog, Device* tables, DNS, SigninLogs, OfficeActivity).

## Solution contents

- Data Connector
  - `Data Connectors/LumenThreatFeed` (ARM templates + Function App implementation)
- Analytic Rules (examples)
  - `Lumen_DomainEntity_DNS.yaml`
  - `Lumen_IPEntity_CommonSecurityLog.yaml`
  - `Lumen_IPEntity_DeviceEvents.yaml`
  - `Lumen_IPEntity_IdentityLogonEvents.yaml`
  - `Lumen_IPEntity_OfficeActivity.yaml`
  - `Lumen_IPEntity_SecurityEvent.yaml`
  - `Lumen_IPEntity_SigninLogs.yaml`
  - `Lumen_IPEntity_WindowsEvents.yaml`
- Hunting Queries
  - `Lumen_IPIndicator_CommonSecurityLog.yaml`
- Workbook
  - `Workbooks/Lumen-Threat-Feed-Overview.json`

## Support

- Lumen Defender Threat Feed/API access: [DefenderThreatFeedSales@Lumen.com](mailto:DefenderThreatFeedSales@Lumen.com?subject=API%20Access%20Request) or your Lumen representative
- If you need assistance in setting up the solution: [DefenderThreatFeedSupport@lumen.com](mailto:DefenderThreatFeedSupport@Lumen.com?subject=Solution%20Support%20Request)
- Microsoft Sentinel configuration: Your Azure admin team
- Solution content issues: Contact Lumen for assistance

— For release history, see `ReleaseNotes.md`. Solution metadata: `SolutionMetadata.json`.
