# Concepts — how it all fits together

This page explains *what* the connector is and *why* it's built the way it is. No Azure background needed. If you only ever read one page, read this one — every other guide assumes you understand the ideas here.

---

## The one-sentence version

> This connector copies security findings from **Trend Vision One** into **Microsoft Sentinel** automatically, so your security team can investigate everything in one place.

That's it. Everything below is just *how* that copy happens and *why* we do it the way we do.

---

## The cast of characters

Let's meet the players, each explained as if you've never seen them before.

### Trend Vision One

Trend Vision One is Trend Micro's security platform. It watches your endpoints, email, network, and cloud, and produces **findings** — "this laptop ran a suspicious command," "this mailbox got a phishing email," and so on.

Think of it as a very attentive security guard who writes down everything suspicious in a notebook.

### Microsoft Sentinel

Microsoft Sentinel is a **SIEM** — a "Security Information and Event Management" system. In plain terms: it's a giant searchable logbook where a security team collects events from *all* their tools (not just Trend) so they can investigate, correlate, and respond in one place.

Think of Sentinel as the central police station where every security guard in the city sends their notebook pages.

### The problem

The guard (Trend Vision One) keeps its notes in *its own* notebook. The police station (Sentinel) can't see them unless someone carries the pages over. **The connector is the courier** that walks the pages from Trend's notebook to Sentinel's logbook — automatically, every few minutes, forever.

---

## How the courier actually works

Sentinel runs in **Microsoft Azure** (Microsoft's cloud). To get Trend's data into a Sentinel workspace, a few small pieces of Azure plumbing have to exist. Here they are, in the order the data flows through them:

```
 Trend Vision One API   ──▶   Poller   ──▶   DCE   ──▶   DCR   ──▶   Custom table   ──▶   You (queries, alerts, dashboards)
 (the security guard)      (the courier)   (mailbox)  (sorter)    (the logbook page)
```

| Piece | Plain-English name | What it does | Real Azure term |
|-------|--------------------|--------------|-----------------|
| **Poller** | The courier | Every few minutes it calls Trend's API, asks "anything new?", and grabs the latest findings. | The connector's built-in poller (Codeless Connector Platform) |
| **DCE** | The mailbox | A fixed address in Azure that the data gets dropped into. | Data Collection **Endpoint** |
| **DCR** | The sorter | Takes Trend's raw data and reshapes it into tidy columns before filing it. Can also drop data you don't want. | Data Collection **Rule** |
| **Custom table** | The logbook page | Where the data actually lands and lives. You query *this*. | A Log Analytics custom table (ends in `_CL`) |
| **Connector definition** | The reception desk | The page in the Sentinel portal where you type your API token and click **Connect**. | `dataConnectorDefinition` |

The two tables data lands in are:

- `TrendMicro_XDR_WORKBENCH_CL` — for the Workbench connector
- `TrendMicro_XDR_OAT_CL` — for the OAT connector

> 💡 **The `_CL` suffix** just means "Custom Log." Any table you create yourself in Sentinel ends in `_CL`. Built-in Microsoft tables don't.

---

## Why "codeless"? (And why you should care)

This connector is built on Microsoft's **Codeless Connector Platform (CCP)** — sometimes written **CCF** (Codeless Connector *Framework*). Same thing.

"Codeless" means **there is no server, no app, and no code running that you have to babysit.** The poller is a feature *inside Sentinel itself*. Microsoft runs it, patches it, and scales it for you.

This is the single biggest reason this connector exists, so it's worth understanding what it replaced:

| | **Old way** (Azure Function connector) | **New way** (this codeless connector) |
|---|----------------------------------------|---------------------------------------|
| What ran the courier | An **Azure Function App** — a little Python program you had to deploy and host | A poller built into Sentinel |
| Extra Azure resources | Function App, App Service Plan, Storage Account, App Insights | None |
| Who patches it | **You** (Python runtime upgrades, dependency updates) | Microsoft |
| Cost | You pay for the compute that runs the function | No compute cost (you pay only for data stored, as always) |
| Secrets it needed | Trend API token **+** your Log Analytics workspace key | Just the Trend API token |
| When it breaks | You debug a function app | You re-enter a token |

In short: **fewer moving parts, fewer things to break, fewer bills, and less to secure.** That's the "why" behind the whole design.

> If you're coming from the old Function App connector, the [Migration guide](05-migration.md) walks you through the switch.

---

## Why so many little template files? (Modular design)

When you click "Deploy to Azure," it doesn't deploy one giant file. It deploys a small **orchestrator** (`mainTemplate.json`) that calls several small **component** files — one for the table, one for the DCE, one for the DCR, and so on.

Why split it up?

- **You can fix one piece without touching the others.** Need to add a column? Edit only the table file. Need to change how data is reshaped? Edit only the DCR file.
- **You can test one piece on its own.**
- **It follows Microsoft's official recommended pattern**, which means it behaves predictably and is easier for others to review.

You don't need to care about this to *use* the connector — it matters only if you're modifying it. The deep-dive lives in [templates/ARCHITECTURE.md](../templates/ARCHITECTURE.md).

---

## Workbench vs. OAT — which one do I want?

This trips everyone up, so here's the honest comparison.

### Workbench Alerts — *"the conclusions"*

Trend Vision One does its own correlation and produces **Workbench alerts**: higher-level, already-investigated incidents. One Workbench alert might bundle together several suspicious events into a single story ("possible ransomware on FINANCE-PC").

- **Volume:** Medium. You get fewer, richer items.
- **Best for:** Teams that want Trend's curated incidents to show up as Sentinel incidents and drive their alert queue.
- **Comes with:** A **parser function** that digs IOCs (file hashes, IPs, domains) out of the nested data for you, plus a ready-made **analytic rule** (turned off by default) and a **dashboard**.

### OAT (Observed Attack Techniques) — *"the raw observations"*

OAT is the firehose: **every individual detection** Trend mapped to a MITRE ATT&CK technique, including full process trees and command lines. No correlation — just the raw signal.

- **Volume:** High. Expect a lot more rows (and therefore more storage cost).
- **Best for:** Threat hunters and detection engineers who want to write their own correlation/hunting queries over granular data.
- **Comes with:** A **universal parser function** (`TrendMicroOAT_Complete()`) that returns one stable, fully-typed schema and works across both old and new OAT data (see below).

### How to choose

| If you want… | Install… |
|--------------|----------|
| Trend's incidents in my Sentinel queue, minimal noise | **Workbench** |
| Raw technique-level data to hunt and build custom detections | **OAT** |
| Both — incidents *and* raw hunting data | **Both** (they don't conflict) |

You are not locked in. Installing one doesn't affect the other, and you can add the second later.

---

## What you'll have after deployment

After you deploy, this is what exists in your Azure subscription. (Exact set depends on the connector — Workbench installs more extras than OAT.)

| Thing | Workbench | OAT | What it's for |
|-------|:---------:|:---:|---------------|
| Custom table (`*_CL`) | ✅ | ✅ | Where data lands |
| Data Collection Endpoint (DCE) | ✅ | ✅ | The mailbox |
| Data Collection Rule (DCR) | ✅ | ✅ | The sorter/transform |
| Connector definition | ✅ | ✅ | The "Connect" page in the portal |
| Parser function | ✅ | ✅ | Workbench: extracts IOCs from nested fields. OAT: universal old+new normalizer |
| Analytic rule (disabled) | ✅ | — | Auto-creates Sentinel incidents when you enable it |
| Workbook (dashboard) | ✅ | — | Charts and overview |
| Active poller | optional* | optional* | Starts pulling data immediately |

\* The poller is created automatically **only if you supply your API token at deploy time**. If you leave the token blank, everything else still deploys and you connect later from the portal. See [Deployment](03-deployment.md).

> ℹ️ **Heads-up on OAT extras:** the OAT template installs the connector, table, DCR, and a parser function, but does **not** currently ship its own analytic rule or workbook the way Workbench does. The [usage guide](04-using-the-connector.md) shows OAT queries you can build into a rule or workbook yourself.

---

## Key terms cheat-sheet

Keep this handy while reading the other guides.

| Term | Plain meaning |
|------|---------------|
| **SIEM** | The central security logbook (here: Sentinel). |
| **Workspace** | A single Sentinel/Log Analytics "logbook." Data lives in a workspace. |
| **Log Analytics** | The database engine under Sentinel that stores and searches the logs. |
| **KQL** | Kusto Query Language — the search language you type to query the data. Like SQL, but for logs. |
| **DCE** | Data Collection Endpoint — the fixed address data is delivered to. |
| **DCR** | Data Collection Rule — reshapes/filters incoming data before storing. |
| **CCP / CCF** | Codeless Connector Platform/Framework — the "no server to babysit" way of building connectors. |
| **ARM template** | A JSON file that tells Azure what to build. The "Deploy to Azure" button runs one. |
| **IOC** | Indicator of Compromise — a file hash, IP, domain, etc. that points to malicious activity. |
| **API token** | The secret password the connector uses to read data out of Trend Vision One. |

Next up: [the permissions you'll need →](02-permissions.md)
