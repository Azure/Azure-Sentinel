# UEBA Behaviors Layer for Microsoft Sentinel

## Turn Complexity into Clarity

Security teams today face an overwhelming challenge: every data point is now a potential security signal, and SOCs are drowning in fragmented, high-volume logs from countless sources - firewalls, cloud platforms, identity systems, and more. The UEBA Behaviors layer is a breakthrough AI-based capability in Microsoft Sentinel that fundamentally changes how SOC teams understand and respond to security events.

## What Are Behaviors?

The Behaviors layer translates low-level, noisy telemetry into human-readable behavioral insights that answer the critical question: **"Who did what to whom, and why does it matter?"**

Instead of sifting through thousands of raw CloudTrail events or firewall logs, you get enriched, normalized behaviors - each one:
- Mapped to **MITRE ATT&CK** tactics and techniques
- Tagged with **entity roles** (Source, Destination, Contextual)
- Presented with a clear, **natural-language explanation**

All behaviors are aggregated and sequenced within a time window or specific trigger, to give you the security story that resides in the logs.

## Behaviors vs. Alerts vs. Anomalies

| Type | Purpose | Action Required |
|------|---------|-----------------|
| **Alerts** | Signal potential threats - work items for SOC | Immediate investigation |
| **Anomalies** | Flag unusual activity for a specific event | Contextual review |
| **Behaviors** | Neutral, descriptive observations of meaningful actions | Building blocks for detection |

Behaviors don't decide if something is malicious; they simply describe meaningful actions in a consistent, security-focused way.

## How It Works: Aggregation and Sequencing

### Aggregation Behaviors
Detect volume-based patterns within a time window.

**Example:** *"User accessed 50+ AWS resources in 1 hour"*

These are invaluable for spotting unusual activity levels and turning high-volume logs into actionable security insights.

### Sequencing Behaviors
Detect multi-step patterns that surface complex chains invisible in individual events.

**Example:** *"Access key created → used from new IP → privileged API calls"*

This helps you spot sophisticated tactics and procedures across sources.

## Contents

- **Behaviors-rules/**: Directory containing markdown table files for each behavior detection rule organized by data source
- **rules_format.md**: Documentation explaining the structure and format of each markdown file
- **use_cases.md**: SOC personas and use case examples with KQL queries

## Supported Data Sources

This collection focuses on non-Microsoft data sources that traditionally lack easy behavioral context in Sentinel:

| Data Source | Coverage |
|-------------|----------|
| **CommonSecurityLog** | CyberArk Vault, Palo Alto Threats |
| **AWSCloudTrail** | EC2, IAM, S3, EKS, Secrets Manager |
| **GCPAuditLogs** | Data Catalog, BigQuery, Compute Engine, IAM, Resource Manager |

## MITRE ATT&CK Coverage

All behaviors are mapped to the MITRE ATT&CK framework, covering tactics including:

- **Collection** - Data gathering and exfiltration activities
- **Discovery** - Reconnaissance and environment mapping
- **Defense Evasion** - Attempts to avoid detection
- **Initial Access** - Entry point activities
- **Persistence** - Maintaining access to systems
- **Command and Control** - Communication with external controllers
- **Lateral Movement** - Moving through the environment
- **Privilege Escalation** - Gaining higher access levels

## Getting Started

1. Navigate to your Sentinel workspace settings and enable the Behaviors layer
2. Explore the `BehaviorInfo` and `BehaviorEntities` tables in Advanced Hunting
3. Build detection rules, hunting queries, and automation workflows using behaviors as building blocks

For detailed rule format information, see `rules_format.md`.
For use case examples and KQL queries, see `use_cases.md`.
