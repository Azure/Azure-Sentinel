# DentiSystems Solution for Microsoft Sentinel

[![Azure Marketplace](https://img.shields.io/badge/Azure-Marketplace_Ready-blue.svg)](https://azuremarketplace.microsoft.com/)
[![Microsoft Sentinel](https://img.shields.io/badge/Microsoft_Sentinel-Content_Hub-0078D4.svg)](https://learn.microsoft.com/en-us/azure/sentinel/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

The **DentiSystems Solution for Microsoft Sentinel** delivers automated, high-fidelity threat intelligence, active deception honeypot telemetry, and zero-trust gateway blocks directly into your Azure Log Analytics workspace.

---

## 🏗️ Architecture & Data Flow

```text
  +-----------------------------------------------------------------------+
  |                        DENTISYSTEMS ECOSYSTEM                         |
  |                                                                       |
  |  +-------------------+  +------------------+  +--------------------+  |
  |  |     DENTIGRID     |  |       GATE       |  |       LEAKS        |  |
  |  | Deception Sensors |  | Edge WAF/Proxy   |  | Credential Breach  |  |
  |  +---------+---------+  +--------+---------+  +---------+----------+  |
  |            |                     |                      |             |
  |            +---------------------+----------------------+             |
  |                                  |                                    |
  |                     [ DentiGrid Core REST API ]                       |
  |                     https://api.grid.denti.systems                    |
  +----------------------------------+------------------------------------+
                                     |
                          HTTPS Polling (CCP) /
                          HTTP Data Collector
                                     |
                                     v
  +-----------------------------------------------------------------------+
  |                          MICROSOFT SENTINEL                           |
  |                                                                       |
  |  [ Codeless Data Connector (CCP) / RestApiPoller ]                    |
  |                           |                                           |
  |                           v                                           |
  |  [ Log Analytics Workspace: DENTIGRIDThreats_CL ]                     |
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
| **ARM Package Template** | `mainTemplate.json` | Master ARM deployment template for Azure Marketplace / Content Hub. |
| **Azure UI Definition** | `createUiDefinition.json` | Azure Portal wizard definition with workspace validation and secret masking. |
| **Solution Metadata** | `SolutionMetadata.json` | Package manifest defining categories, version (1.0.0), and publisher info. |
| **Data Connector** | `DataConnectors/DentiSystems_CCP.json` | Codeless Connector Platform (CCP) definition targeting `/api/attacks/recent`. |
| **Analytic Rules** | `AnalyticRules/*.json` | 4 MITRE ATT&CK mapped scheduled alert rules for automated incident creation. |
| **Visual Dashboard** | `Workbooks/DentiSystems_ThreatOverview.json` | Multi-view Azure Monitor / Sentinel Workbook for real-time threat analysis. |
| **Hunting Queries** | `HuntingQueries/DentiSystems_HuntingQueries.json` | Proactive threat hunting queries for brute force and zero-day exploits. |
| **ASIM Parser** | `Parsers/DentiSystems_ASIM_Parser.kql` | KQL parser normalizing telemetry to the Advanced Security Information Model. |

---

## 🚨 Included Detection Rules

1. **DentiSystems - High Severity Honeypot Breach Detected**
   - **Severity:** High | **Tactics:** `InitialAccess`, `Execution`, `LateralMovement` (T1190, T1078, T1021)
   - **Trigger:** Intercepts critical exploitation attempts, unauthorized shell breakouts, or severity scores $\ge 8$.
2. **DentiSystems - Volumetric Port Scanning & Reconnaissance**
   - **Severity:** Medium | **Tactics:** `Discovery`, `Reconnaissance` (T1046, T1595)
   - **Trigger:** Identifies automated adversary scanners probing $\ge 5$ ports or firing $\ge 20$ attempts in 15 minutes.
3. **DentiSystems - GATE Zero-Trust Threat & Injection Intercepted**
   - **Severity:** High | **Tactics:** `InitialAccess`, `DefenseEvasion` (T1190, T1059)
   - **Trigger:** Alerts on SQLi, Command Injection, XSS, or Prompt Injection blocked by the GATE edge proxy.
4. **DentiSystems - Critical SCADA / BMS / IoT Protocol Tampering**
   - **Severity:** High | **Tactics:** `Impact`, `InitialAccess` (T0855, T0812)
   - **Trigger:** Detects unauthorized traffic on Modbus (502), BACnet (47808), S7comm (102), MQTT (1883), or DNP3.

---

## 🚀 Deployment Instructions

### Method 1: Azure Portal / Marketplace Deployment
1. Search for **DentiSystems Threat Intelligence** in Azure Marketplace / Microsoft Sentinel Content Hub.
2. Select your Log Analytics Workspace where Sentinel is onboarded.
3. Enter your **DentiSystems API Bearer Token** (obtained from DentiGrid under **Settings > Integrations > SIEM & SOAR**).
4. Complete the validation and click **Create**.

### Method 2: Azure CLI / ARM Template Deployment
```bash
az deployment group create \
  --name "DentiSystems-Sentinel-Deploy" \
  --resource-group "<Your-Resource-Group>" \
  --template-file "./mainTemplate.json" \
  --parameters \
      workspace="<Your-LogAnalytics-Workspace-Name>" \
      dentiSystemsApiKey="<Your-DentiSystems-API-Key>" \
      enableDataConnector=true \
      enableAnalyticRules=true \
      enableWorkbooks=true
```

---

## 📊 KQL Schema (`DENTIGRIDThreats_CL`)

| Field Name | Type | Description |
|---|---|---|
| `TimeGenerated` | `datetime` | UTC timestamp of the captured threat event |
| `SourceIP_s` | `string` | Attacker IP address |
| `SourceCountry_s` | `string` | Attacker geolocation country |
| `SourceCity_s` | `string` | Attacker geolocation city |
| `DestinationPort_d` | `int` | Targeted destination port (e.g. 22, 80, 502) |
| `Protocol_s` | `string` | Network protocol (`tcp`, `udp`, `http`, `ssh`, `modbus`) |
| `Signature_s` | `string` | Threat classification / attack signature |
| `Severity_s` / `Severity_d` | `int/string` | Threat severity score (1-10) |
| `NodeID_s` | `string` | Deception honeypot sensor or edge gateway identifier |
| `Method_s` | `string` | HTTP method (if applicable) |
| `URL_s` | `string` | Targeted URI / endpoint |
| `Platform_s` | `string` | Origin platform (`DENTIGRID`, `GATE`, `LEAKS`) |

---

## 📄 License
Copyright (c) 2026 DentiSystems Inc. Licensed under the Apache License, Version 2.0.
