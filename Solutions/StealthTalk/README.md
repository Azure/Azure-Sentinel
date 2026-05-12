# StealthTalk Anomalous Authentication — Microsoft Sentinel Solution

The StealthTalk Anomalous Authentication solution surfaces suspicious user-authentication events from the StealthTalk private business messenger inside Microsoft Sentinel, providing a normalised ASIM-compliant view, four scheduled detections, three hunting queries, an interactive workbook, and a Teams-notification playbook. It is intended for organisations running StealthTalk Enterprise on Microsoft Azure and wanting their SOC to operate StealthTalk anomalies through standard Sentinel workflows.

## What's inside

| Artefact                             | Count | Notes                                                                                                                 |
| ------------------------------------ | ----- | --------------------------------------------------------------------------------------------------------------------- |
| Data Connector (Logs Ingestion API)  | 1     | Custom log table + DCE + DCR. Stream `Custom-StealthTalkAnomalousAuth_CL`. 21 fields covering 4 anomaly classes.      |
| Scheduled Analytic Rules             | 4     | After-Hours Work (Low), Multi New Devices Registration (Medium), Login Outside Work Zone (High), Password Brute Force (High). MITRE-mapped. |
| Hunting Queries                      | 3     | Impossible Travel, Account Takeover Sequence, Brute Force followed by Suspicious Access.                              |
| ASIM Parsers (Authentication 0.1.3)  | 3     | `vimAuthenticationStealthTalk` (filtering), `ASimAuthenticationStealthTalk` (non-filtering), and an `imAuthentication` union extension that registers the StealthTalk source. |
| Workbook                             | 1     | 17 panels across Overview, Off-Hours, New Devices, Geo Anomaly, Brute Force. Includes a User Risk Leaderboard, Multi-Vector Correlation, and a World Map. |
| Playbook                             | 1     | Logic App that posts incident details into a Microsoft Teams channel via webhook.                                     |

## Prerequisites

1. A Microsoft Sentinel-enabled Log Analytics workspace.
2. A deployed StealthTalk Enterprise instance configured to send anomalous-auth events to the Log Analytics workspace via the Logs Ingestion API. StealthTalk authenticates to Azure with a service principal granted the **Monitoring Metrics Publisher** role on the deployed Data Collection Rule.
3. Workspace ASIM Authentication parsers (Microsoft's `FullDeploymentAuthentication.json`) deployed in the workspace before this Solution is installed. The Solution's `imAuthentication` extension parser overrides the union so that StealthTalk events are returned by `imAuthentication()` alongside Microsoft-built-in sources.
4. For the Teams playbook: a Microsoft Teams channel with an incoming-webhook workflow already created. The webhook URL is configured as a deployment parameter.

## Installation

This solution is published as a partner Sentinel Solution to the **Microsoft Sentinel Content Hub**. To install:

1. Open Microsoft Defender → Microsoft Sentinel → your workspace → **Content management** → **Content hub**.
2. Search for **StealthTalk Anomalous Authentication** and click **Install**.
3. After install, configure each artefact under **Content management → Content hub → StealthTalk → Manage**:
   - Open the **StealthTalk Anomalous Authentication** Data Connector page; copy the DCE Logs Ingestion endpoint and DCR Immutable ID and paste them into your StealthTalk admin console.
   - Enable the four Analytic Rule templates (review default lookback windows and severities).
   - Enable the three Hunting Query templates if your SOC uses proactive hunting.
   - Open the **StealthTalk Anomalous Auth Monitor** workbook to verify ingestion and visualise anomalies.
   - Deploy the Teams Playbook and pass the webhook URL of your existing Teams channel as a parameter.
   - Create an Automation Rule that runs the Playbook on incidents from any of the four StealthTalk analytic rules.

A separate **Deployment & Validation Guide** (PDF) is published alongside the solution with full step-by-step screenshots.

## Validation

After installation, you can validate end-to-end ingestion with the following queries.

```kql
// 1) Raw events arriving at the custom table
StealthTalkAnomalousAuth_CL
| where TimeGenerated > ago(1h)
| count
```

```kql
// 2) ASIM-normalised events via the StealthTalk vim parser
vimAuthenticationStealthTalk
| where TimeGenerated > ago(1h)
| count
```

```kql
// 3) StealthTalk events visible through the ASIM Authentication union
imAuthentication
| where TimeGenerated > ago(1h)
| where EventVendor == "StealthTalk"
| count
```

If query (3) returns zero while (1) and (2) return matches, the `imAuthentication` extension parser was not deployed; redeploy the **Parsers** content from the Solution.

## Detections

| Rule                              | Severity | Lookback | Schedule  | Trigger                                                                                                          |
| --------------------------------- | -------- | -------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| After Hours Work                  | Low      | 48 h     | every 1 h | ≥ 3 off-hours logins (`IsWeekend` OR `DeviationMinutes ≥ 180`) on ≥ 2 distinct calendar days, per user.          |
| Multi New Devices Registration    | Medium   | 24 h     | every 30 min | ≥ 2 distinct `NewDeviceLogin` events for the same user within the window.                                     |
| Login Outside Work Zone           | High     | 1 h      | every 15 min | A `GeoAnomalyLogin` event where `LoginCountry ≠ AssignedCountry` OR `LoginCity ≠ AssignedCity`.              |
| Password Brute Force              | High     | 5 h      | every 15 min | A `MultiFailLogin` event with `PassedAttempts ≥ 9`.                                                          |

All four rules emit `Account` (UserId), `Host` (DeviceId), and where relevant `IP` (IpAddress) entities, plus alert-detail overrides describing the anomaly in plain language for the SOC analyst.

## Support

This is a partner-published Sentinel Solution. For support contact **support@stealthtalk.com** or open a ticket via your StealthTalk support portal.
