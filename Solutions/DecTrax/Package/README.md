# DECTRAX Solution for Microsoft Sentinel

[![Azure Marketplace](https://img.shields.io/badge/Azure-Marketplace_Ready-blue.svg)](https://azuremarketplace.microsoft.com/)
[![Microsoft Sentinel](https://img.shields.io/badge/Microsoft_Sentinel-Content_Hub-0078D4.svg)](https://learn.microsoft.com/en-us/azure/sentinel/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

The **DECTRAX Solution for Microsoft Sentinel** delivers automated, high-fidelity threat intelligence, active deception honeypot telemetry, and zero-trust gateway blocks directly into your Azure Log Analytics workspace via the Microsoft Codeless Connector Framework (CCF).

---

## 🏗️ Architecture & Data Flow

```text
  +-----------------------------------------------------------------------+
  |                           DECTRAX ECOSYSTEM                           |
  |                                                                       |
  |  +-------------------+  +------------------+  +--------------------+  |
  |  |      DECTRAX      |  |       GATE       |  |       LEAKS        |  |
  |  | Deception Sensors |  | Edge WAF/Proxy   |  | Credential Breach  |  |
  |  +---------+---------+  +--------+---------+  +---------+----------+  |
  |            |                     |                      |             |
  |            +---------------------+----------------------+             |
  |                                  |                                    |
  |                       [ DECTRAX Core REST API ]                       |
  |                       https://api.dectrax.com                         |
  +----------------------------------+------------------------------------+
                                     |
                          HTTPS Polling (CCF) /
                          HTTP Data Collector
                                     |
                                     v
  +-----------------------------------------------------------------------+
  |                          MICROSOFT SENTINEL                           |
  |                                                                       |
  |  [ Codeless Connector Framework (CCF) / RestApiPoller ]               |
  |                           |                                           |
  |                           v                                           |
  |  [ Log Analytics Workspace: DECTRAXThreats_CL ]                       |
  |                           |                                           |
  |             +-------------+-------------+                             |
  |             |                           |                             |
  |             v                           v                             |
  |  [ 4x Analytic Rules ]        [ Interactive Workbook ]                |
  |  - High Severity Breach       - Threat Geo Map                        |
  |  - Volumetric Recon/Scan      - Attack Protocols                      |
  |  - GATE Threat Intercept      - Deception Nodes                       |
  |  - SCADA/BMS Tamper           - Attacker IP Top 20                    |
  +-----------------------------------------------------------------------+
```

---

## 📦 Solution Package Contents

| Component | File / Resource | Description |
|---|---|---|
| **ARM Package Template** | `Package/mainTemplate.json` | Master ARM deployment template for Azure Marketplace / Content Hub. |
| **Azure UI Definition** | `Package/createUiDefinition.json` | Azure Portal wizard definition with workspace validation and secret masking. |
| **Solution Metadata** | `SolutionMetadata.json` | Package manifest defining Microsoft taxonomy domains, version (1.0.0), and publisher info. |
| **Data Connector** | `Data Connectors/DecTrax_CCF/` | Codeless Connector Framework (CCF) definition targeting `/api/attacks/recent`. |
| **Analytic Rules** | `Analytic Rules/` | 4 high-fidelity alert rules with MITRE ATT&CK mappings. |
| **Hunting Queries** | `Hunting Queries/` | Proactive threat hunting queries for brute-force and zero-day payloads. |
| **Parsers** | `Parsers/` | ASIM KQL parser functions normalizing telemetry to standard schema. |
| **Workbook** | `Workbooks/` | Interactive SecOps visual dashboard. |

---

## 🚀 Quick Deployment

1. Search for **DECTRAX** in the Microsoft Sentinel Content Hub.
2. Click **Install**.
3. In the Data Connector configuration page, input your DECTRAX API endpoint and Bearer Token.
4. Save and verify telemetry streaming into `DECTRAXThreats_CL`.

For technical support or inquiries: [support@dectrax.com](mailto:support@dectrax.com) | [https://dectrax.com](https://dectrax.com)
