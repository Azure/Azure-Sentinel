# Exercise 14 — Sentinel MCP Server Demo Prompts

These prompts are designed for Solutions Engineers to demonstrate the Microsoft Sentinel MCP Server capabilities during customer PoCs. Each prompt showcases a different MCP capability and maps to the PoCaaS attack scenario data.

> **Tip:** Paste these prompts directly into GitHub Copilot Chat (or any MCP-enabled AI assistant) with the Sentinel MCP server connected. The AI will call the appropriate MCP tools automatically.

---

## Prerequisites — Setting Up MCP in VS Code

Before running any of the prompts below, you need to connect VS Code to the Sentinel MCP server. The setup takes under a minute:

1. Open the Command Palette (`Ctrl + Shift + P`) → **MCP: Add Server** → choose **HTTP (HTTP or Server-Sent Events)**.
2. Enter the MCP server URL for the collection you want (see the table below).
3. Give it a friendly Server ID (e.g. `Sentinel Data Exploration`).
4. When prompted, **Allow** authentication — sign in with an account that has at least the **Security Reader** role.
5. Open **Copilot Chat** (`Ctrl + Alt + I`), switch to **Agent mode**, and confirm the MCP tools appear under the tools icon.

Repeat steps 1–3 for each collection you want to connect (Data Exploration + Triage recommended for PoCs).

> **Full step-by-step guide with screenshots:** [Use an MCP tool in Visual Studio Code — Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-use-tool-visual-studio-code)

---

## MCP Server Architecture — Three Tool Collections

The Sentinel MCP server is **not** just data lake querying. It exposes **three distinct tool collections**, each with its own server URL:

| Collection | Server URL | What It Does |
|---|---|---|
| **Data Exploration** | `https://sentinel.microsoft.com/mcp/data-exploration` | `search_tables`, `query_lake`, `analyze_user_entity`, `analyze_url_entity`, `list_sentinel_workspaces` — explore and query raw data in the Sentinel Data Lake |
| **Triage** | `https://sentinel.microsoft.com/mcp/triage` | `ListIncidents`, `GetIncidentById`, `ListAlerts`, `GetAlertByID`, `RunAdvancedHuntingQuery`, `GetDefenderFileInfo`, `GetDefenderIpAlerts`, `GetDefenderMachine`, `GetDefenderMachineAlerts`, `ListDefenderIndicators`, `ListDefenderInvestigations`, + more — direct API access to Defender XDR incidents, alerts, devices, files, IOCs, vulnerabilities, and automated investigations |
| **Security Copilot Agent Creation** | `https://sentinel.microsoft.com/mcp/security-copilot-agent-creation` | Create Security Copilot agents for complex workflows |

> **For PoC demos:** Connect **both** the Data Exploration and Triage collections. The prompts below indicate which collection each prompt targets.

---

## 1 — Incident Triage & Prioritisation

**Collection:** Triage | **Tools:** `ListIncidents`, `GetIncidentById`, `ListAlerts`

> *"List the most recent security incidents in my tenant, sorted by severity. For the most critical one, pull its full details including all correlated alerts and their evidence. Which incident should I triage first and why?"*

---

## 2 — Attack Timeline & Kill Chain Diagram

**Collection:** Data Exploration | **Tools:** `query_lake` (multi-table) + Mermaid rendering

> *"Build me a chronological attack timeline for the user mirage@pkwork.onmicrosoft.com by correlating security alerts across all data sources — CrowdStrike, Okta, AWS CloudTrail, Palo Alto, and MailGuard. Map each stage to the MITRE ATT&CK tactic and the data source that detected it. Then render the full kill chain as a Mermaid flow diagram, colour-coded by severity."*

---

## 3 — Cross-Source Threat Hunting

**Collection:** Data Exploration | **Tools:** `search_tables`, `query_lake`

> *"I want to threat-hunt across all my third-party data sources. First discover what tables are available, then for each source — CrowdStrike endpoint detections, Okta identity events, AWS CloudTrail activity, and Palo Alto firewall logs — summarise the most suspicious activity in the last 7 days. Which data source shows the most critical findings?"*

---

## 4 — User Entity Behaviour Analysis

**Collection:** Data Exploration | **Tools:** `analyze_user_entity`

> *"Run a full security analysis on the user mirage@pkwork.onmicrosoft.com. Check for anomalous behaviour, risk indicators, authentication anomalies, and any security incidents associated with this user over the last 7 days. Is this user compromised?"*

---

## 5 — IOC & Entity Investigation (Domain + File)

**Collection:** Data Exploration + Triage | **Tools:** `analyze_url_entity`, `GetDefenderFileInfo`, `GetDefenderFileStatistics`, `GetDefenderFileRelatedMachines`, `ListDefenderIndicators`

> *"Investigate these two IOCs from our attack scenario: (1) Analyse the domain update-service-cdn.xyz — is it malicious, has it been seen in our environment, and what does threat intelligence say? (2) Look up the file hash e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 in Defender — get its prevalence, related alerts, and which devices have seen it. Also list any IOC indicators we've configured."*

---

## 6 — Entity Relationship Graph

**Collection:** Data Exploration | **Tools:** `query_lake` + Mermaid rendering

> *"For the active multi-stage incident in my Sentinel workspace, map out all the entities involved — users, hosts, IP addresses, domains, and file hashes. Show me a visual entity relationship graph that connects them, so I can see how the attacker pivoted through the environment. Render it as a Mermaid diagram."*

---

## 7 — Device Investigation & Lateral Movement

**Collection:** Triage | **Tools:** `GetDefenderMachine`, `GetDefenderMachineAlerts`, `GetDefenderMachineLoggedOnUsers`, `FindDefenderMachineByIp`, `ListUserRelatedMachines` + Mermaid rendering

> *"Investigate the compromised endpoint at IP 10.0.1.50. Get its full device profile from Defender — OS, health status, risk score, vulnerabilities. Then find who else has logged into that device, what other devices those users accessed, and whether any of those users have security alerts. Render the lateral movement paths as a Mermaid diagram."*

---

## 8 — Advanced Hunting (Defender XDR)

**Collection:** Triage | **Tools:** `FetchAdvancedHuntingTablesOverview`, `FetchAdvancedHuntingTablesDetailedSchema`, `RunAdvancedHuntingQuery`

> *"Using Defender advanced hunting, find all devices that communicated with IP address 192.0.2.100 in the last 7 days. First discover what hunting tables are available, then run the query. Show me the device names, connection timestamps, and data volumes."*

---

## 9 — Alert Correlation & Severity Chart

**Collection:** Data Exploration | **Tools:** `query_lake` + Mermaid rendering

> *"Show me all security alerts from the last 7 days, grouped by alert name, severity, and data source. Sort by volume. For the top alert types, explain what attack stage they represent. Then render a visual chart showing alert distribution by data source and severity as a Mermaid diagram."*

---

## 10 — Data Source Health & Coverage

**Collection:** Data Exploration | **Tools:** `search_tables`, `query_lake`

> *"What third-party data sources are currently ingesting data into my Sentinel workspace? For each one — CrowdStrike, Okta, Palo Alto, AWS, and email security — tell me how many events have been ingested in the last 7 days and whether the data looks healthy. Render a Mermaid diagram showing the data flow from each source into Sentinel."*

---

## 11 — Create a Custom MCP Tool

Beyond using the built-in tool collections, you can **create your own custom MCP tools** from saved Advanced Hunting KQL queries. This gives you granular control over the data your AI agent can access and lets you build deterministic agentic workflows tailored to your environment.

### Why Custom Tools?

| Benefit | Description |
|---|---|
| **Controlled data access** | Limit exactly which tables and columns the AI can query |
| **Reusable workflows** | Save proven hunting queries as tools the whole SOC team can invoke |
| **Parameterised inputs** | Convert query values into parameters the AI populates from conversation context |
| **Custom collections** | Organise tools into scenario-focused collections (e.g., "Firewall Investigations") |

### Steps — Save a KQL Query as a Custom MCP Tool

1. In the **Microsoft Defender portal**, navigate to **Hunting** → **Advanced hunting**
2. Write or open a saved KQL query — for example, a query that summarises denied firewall connections by source IP:

```kusto
CommonSecurityLog
| where TimeGenerated > ago({Lookback})
| where DeviceVendor == "Palo Alto Networks"
| where Activity in ("drop", "deny", "reset-both")
| summarize
    DeniedConnections = count(),
    DistinctPorts = dcount(DestinationPort),
    PortList = make_set(DestinationPort, 25)
    by SourceIP
| where DeniedConnections > 50
| sort by DeniedConnections desc
```

> **Note:** The `{Lookback}` value uses the `{ParameterName}` format — this will become a configurable parameter in the tool.

3. Click the **context menu** (⋯) on the query or the **query box menu** → select **Save as tool**
4. In the **Save tool** flyout panel, fill in:
   - **Name:** `firewall_denied_connections` (discoverable, action-oriented)
   - **Description:** `Retrieves a summary of denied firewall connections grouped by source IP, including distinct port counts, for the specified lookback window. Use this to identify potential port scanners or blocked attackers.`
   - **Collection:** Select **Create new collection** → name it `Custom Firewall Tools`
   - **Default workspace:** Select your Sentinel workspace
   - **Parameters:** Add `Lookback` with description `Time range to query, e.g. 7d, 24h, 4h`
5. Click **Save**

### Steps — Use the Custom Tool in VS Code

1. Open VS Code → Command Palette → **MCP: Add Server** → **HTTP**
2. Enter the custom collection URL — find it under **Advanced hunting** → **Tools** tab → your collection
3. Open **Copilot Chat** in Agent mode and confirm the custom tool appears
4. Test with a prompt:

> *"Using my custom firewall tools, show me all source IPs that were denied more than 50 connections in the last 24 hours. Which IPs look like they're performing port scans?"*

The AI will call your `firewall_denied_connections` tool with `Lookback = 24h` and reason over the results.

### Best Practices for Tool Descriptions

- **Start with a verb** — "Retrieves...", "Identifies...", "Summarises..."
- **Focus on purpose, not parameters** — describe what the tool does, not how to call it
- **Include workflow hints** if the tool depends on another — e.g., "Call `risky_users_tool` first"
- **Keep it to 1–2 sentences** — AI models perform better with concise descriptions

> **Reference:** [Create and use custom Microsoft Sentinel MCP tools](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-create-custom-tool)

---

## Quick Reference — MCP Capabilities Showcased

| # | Prompt | Collection | Tools Used | Visual? | Key Feature |
|---|--------|-----------|------------|---------|-------------|
| 1 | Incident Triage | Triage | `ListIncidents`, `GetIncidentById` | | Incident API access |
| 2 | Kill Chain Diagram | Data Exploration | `query_lake` + Mermaid | ✅ | Attack timeline + visual |
| 3 | Cross-Source Hunting | Data Exploration | `search_tables` + `query_lake` | | Multi-source threat hunting |
| 4 | User Analysis | Data Exploration | `analyze_user_entity` | | UEBA & risk profiling |
| 5 | IOC Investigation | Both | `analyze_url_entity` + `GetDefenderFile*` | | Entity + Defender APIs |
| 6 | Entity Graph | Data Exploration | `query_lake` + Mermaid | ✅ | Investigation graph |
| 7 | Device & Lateral Movement | Triage | `GetDefenderMachine*` + Mermaid | ✅ | Graph-style investigation |
| 8 | Advanced Hunting | Triage | `RunAdvancedHuntingQuery` | | Defender hunting engine |
| 9 | Alert Heatmap | Data Exploration | `query_lake` + Mermaid | ✅ | Alert distribution chart |
| 10 | Data Source Health | Data Exploration | `search_tables` + `query_lake` + Mermaid | ✅ | Connector health + arch diagram |
| 11 | Custom MCP Tool | Custom | Saved KQL → custom tool | | Extensibility + custom workflows |

---

## References

- [Use an MCP tool in Visual Studio Code](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-use-tool-visual-studio-code) — setup guide
- [Tool collections in Microsoft Sentinel MCP server](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-tools-overview) — full tool reference
- [Get started with Microsoft Sentinel MCP server](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-get-started) — overview & prerequisites
- [Create and use custom Microsoft Sentinel MCP tools](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-create-custom-tool) — custom tool authoring

