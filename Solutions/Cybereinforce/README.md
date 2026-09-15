# Cybereinforce Threat Enforcement (CTE) for Microsoft Sentinel

[Cybereinforce Threat Enforcement](https://cybereinforce.com) enforces Microsoft Defender threat intelligence directly at the browser (Chrome, Firefox, Safari) on enrolled endpoints, blocking access to known-malicious and policy-restricted URLs before they load.

This solution brings Cybereinforce's enforcement and audit activity into Microsoft Sentinel for SOC investigation, hunting, and alerting.

## Contents

- **Data Connectors**: 1 - scheduled Logic App that polls the Cybereinforce API and ingests events into the `CybereinforceCTE_CL` custom table via the Azure Monitor Logs Ingestion API.
- **Workbooks**: 1 - ingestion health, URL blocks, audit activity, and IOC synchronization.
- **Analytic Rules**: 18 - covering URL enforcement, threat-intelligence matches, device risk patterns (repeated/spiking blocks, suspected compromise, company-wide campaigns), administrative/audit activity, and license/rule capacity health.

## Prerequisites

- An active Cybereinforce Threat Enforcement subscription.
- A Microsoft Sentinel workspace.
- Admin access to the [Cybereinforce Admin portal](https://cybereinforce.com/admin/) to generate a MicrosoftToken (see the data connector's in-product deployment instructions).

## Support

See [SolutionMetadata.json](./SolutionMetadata.json) for support contact details, or visit [cybereinforce.com/support.html](https://cybereinforce.com/support.html).

See [ReleaseNotes.md](./ReleaseNotes.md) for version history.
