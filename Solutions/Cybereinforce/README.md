# Cybereinforce Threat Enforcement (CTE) for Microsoft Sentinel

[Cybereinforce](https://cybereinforce.com) enforces Microsoft Defender and Cybereinforce threat intelligence at the browser, in the inbox and on the host.

This solution brings events from every Cybereinforce product into Microsoft Sentinel for SOC investigation, hunting, and alerting: Browser protection (URL blocks, threat-intelligence matches, devices, rules), Email Security, Host Enforcement, Brand Protection and platform audit events. The `Product` column tells them apart.

## Contents

- **Data Connectors**: 1 - Codeless Connector Platform (RestApiPoller): Microsoft Sentinel collects new events every 5 minutes from the Cybereinforce API into the `CybereinforceCTE_CL` custom table. The only value to enter is a Cybereinforce MicrosoftToken.
- **Workbooks**: 1 - ingestion health, URL blocks, audit activity, and IOC synchronization.
- **Analytic Rules**: 18 - covering URL enforcement, threat-intelligence matches, device risk patterns (repeated/spiking blocks, suspected compromise, company-wide campaigns), administrative/audit activity, and license/rule capacity health.

## Prerequisites

- An active Cybereinforce Threat Enforcement subscription.
- A Microsoft Sentinel workspace.
- Tenant Administration access to the [Cybereinforce admin console](https://cybereinforce.com/admin/) to generate a MicrosoftToken (Deployment -> Tokens & Deployment).

## Support

See [SolutionMetadata.json](./SolutionMetadata.json) for support contact details, or visit [cybereinforce.com/support.html](https://cybereinforce.com/support.html).

See [ReleaseNotes.md](./ReleaseNotes.md) for version history.
