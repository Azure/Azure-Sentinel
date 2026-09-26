# Prancer PenSuiteAI Integration

Microsoft Sentinel solution for [Prancer](https://www.prancer.io)'s unified security findings
pipeline — Infrastructure-as-Code (IaC) and Cloud Security Posture Management (CSPM), Static/
Dynamic/Software-Composition Application Security Testing (SAST/DAST/SCA), and AI-driven
adversarial exploitation testing (SwarmHack) — ingested into a single `PrancerFindings_CL` table
and surfaced through analytic rules, hunting queries, a workbook, a watchlist-driven escalation
rule, and a set of automation playbooks.

## What it does

- **Data Connector** (`PrancerLogData`) ingests normalized findings from all Prancer scan types
  into `PrancerFindings_CL` via the Azure Monitor Logs Ingestion API (DCE/DCR).
- **Parser** (`PrancerFindings`) centralizes severity ranking, payload extraction, and
  data-quality flagging so every rule/query/workbook tile reads through one consistent function
  instead of re-deriving fields from the raw table.
- **Analytic Rules** cover consolidated CSPM/IaC posture findings, PAC application findings,
  SAST/DAST/SCA findings, SwarmHack high-confidence exploitation, cross-tool correlation (e.g.
  CSPM misconfigurations independently confirmed exploitable by SwarmHack), kill-chain
  decomposition, and a watchlist-driven crown-jewel escalation rule.
- **Watchlist** (`Prancer Crown Jewel Assets`) lets customers declare business-critical assets so
  the crown-jewel escalation rule can flag any finding — from any scan type, not only SwarmHack —
  that touches a declared crown jewel.
- **Hunting Queries** mirror several of the analytic rules for proactive, non-alerting
  investigation (severity triage, MITRE technique corroboration across scan types, recurring
  findings across scan cycles).
- **Workbook** (`Prancer Sentinel Analytics`) visualizes findings by severity, scan type, kill
  chain, crown-jewel exposure, and ATT&CK technique coverage.
- **Playbooks** automate response: kill-chain context enrichment on incident creation,
  confidence-thresholded ticketing, a scheduled executive digest, app-owner notification, and a
  human-approval-gated Teams notification for crown-jewel-reaching findings. All playbooks are
  read-only/notification-only — none execute remediation actions.
- **Ingestion health** is monitored in-product by the *Data-quality degradation or ingestion
  staleness* analytic rule, which raises a Sentinel incident if no new `PrancerFindings_CL` rows
  arrive within the expected window, so a silent connector failure doesn't go unnoticed.

## Prerequisites

- A Prancer account with scan results (IaC/CSPM, PAC, or SwarmHack) configured to push to this
  solution's Log Analytics workspace. Contact [support@prancer.io](mailto:support@prancer.io) or
  your Prancer account team to enable Sentinel export for your tenant.
- Permission to deploy Data Connector Rules (DCR), a Data Collection Endpoint (DCE), and the
  solution's content types (analytic rules, workbook, watchlist, playbooks) in your Sentinel
  workspace.
- For playbooks: permission to create Logic Apps and the relevant API connections
  (Microsoft Sentinel, Office 365, Microsoft Teams, depending on which playbooks you deploy).

## Deployment

Deploy from the Microsoft Sentinel **Content Hub** (search "Prancer PenSuiteAI Integration") or
via the solution's `Package/mainTemplate.json`. After the core solution is installed:

1. Open the **Prancer Data Connector** page in Microsoft Sentinel and deploy it: the solution
   provisions the Data Collection Endpoint, Data Collection Rule and `PrancerFindings_CL` table,
   then grant Prancer's Entra application the *Monitoring Metrics Publisher* role on the deployed
   DCR and configure Prancer with the DCE endpoint and DCR immutable ID shown on the connector page.
2. Populate the `Prancer Crown Jewel Assets` watchlist with your organization's critical assets
   (see `Watchlists/PrancerCrownJewelAssets.json` for the expected schema).
3. Deploy whichever playbooks fit your operating model from `Playbooks/` — each has its own
   `readme.md` with parameters, required API connections, and post-deployment steps (e.g.
   authorizing connections, attaching the playbook to an automation rule).

## Support

- Documentation: [docs.prancer.io](https://docs.prancer.io)
- Support: [support@prancer.io](mailto:support@prancer.io)
- Tier: Partner

## Release notes

See `ReleaseNotes.md` for version history.
