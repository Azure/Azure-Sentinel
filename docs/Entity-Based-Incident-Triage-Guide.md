# Entity-Based Incident Triage Guide for Microsoft Sentinel Analysts

## Purpose
This guide helps analysts triage Microsoft Sentinel incidents consistently by focusing on entities, repeated alert patterns, identity context, network context, enrichment, documentation, escalation, and tuning decisions. It is designed to improve investigation quality while reducing avoidable analyst fatigue.

## When to Use This Guide
Use this guide during:
- Initial incident triage when an alert or incident is first assigned.
- Repetitive alert review to determine whether repeated signals indicate noise or a pattern.
- Escalation preparation when evidence suggests broader risk or impact.
- Tuning review when recurring low-value incidents require detection improvements.
- Analyst handover to preserve context and continuity across shifts.

## Triage Principles
- Understand the signal before closing the alert.
- Repetitive alerts are not always noise; they may reveal patterns.
- Start from the entities involved.
- Separate evidence from assumptions.
- Document why an incident was closed or escalated.
- Treat enrichment as supporting context, not final proof.

## Initial Analyst Checklist
- Confirm incident title and severity.
- Confirm alert provider and detection source.
- Identify the triggered analytics rule.
- Verify the relevant time range.
- List all involved entities.
- Review user or account context.
- Review IP and network context.
- Review host or device context.
- Review domain, URL, and hash context.
- Check related incidents for the same entities.
- Record MITRE ATT&CK mapping if available.
- Decide and record the recommended next action.

## Entity-Based Triage Flow

### User or Account
- Is the account privileged or associated with sensitive business functions?
- Is the sign-in behavior unusual for the user, device, geography, or time?
- Are there failed sign-ins before a successful sign-in?
- Is MFA involved, bypassed, challenged, or unexpectedly absent?
- Are there recent password resets, role changes, or conditional access changes?
- Are there related alerts or incidents for the same identity?

### IP Address
- Is the IP internal, external, VPN, proxy, cloud, or hosting provider space?
- Has this IP appeared in previous incidents or repeated alerts?
- Is the IP associated with multiple users or hosts in a suspicious way?
- Is geolocation or ASN context relevant to the activity pattern?
- Is approved threat intelligence context available for this IP?

### Host or Device
- Is the device managed and known in the organization inventory?
- Is the device critical, internet-exposed, or business-sensitive?
- Are there related endpoint alerts on the same host?
- Are there suspicious process, network, or authentication events around the same time?
- Is the device associated with repeated alerts across multiple incidents?

### Domain, URL, or FQDN
- Is the domain newly observed or unusual in the environment?
- Is activity potentially related to phishing, command and control, or suspicious redirection?
- Are multiple users or hosts contacting the same domain or URL?
- Is supporting DNS, proxy, or firewall context available for correlation?

### File Hash or File Name
- Is the file observed on one device or multiple devices?
- Is relevant endpoint telemetry available for execution and behavior?
- Is the hash recognized by approved security tooling in the environment?
- Is there evidence of execution, persistence, or lateral movement context?

## Repetitive Alert Review Flow
- Cluster repeated incidents by primary entity, such as user, host, IP, domain, or hash.
- Cluster by time window to identify periodic, burst, or continuous behavior.
- Compare current behavior with historical baseline for the same entities.
- Determine whether the pattern reflects expected activity, misconfiguration, weak tuning, or potential recurring attacker behavior.
- Choose one documented outcome:
  - Close as benign with clear evidence.
  - Escalate for deeper investigation.
  - Suppress based on approved policy and validated low risk.
  - Submit a tuning request.
  - Submit a detection improvement request.

## Identity Investigation Prompts
- Is the sign-in risk level elevated or inconsistent with normal identity behavior?
- Are there impossible travel indicators supported by timeline evidence?
- Did the account access unusual applications, resources, or privileged scopes?
- Is there evidence of token misuse, consent abuse, or suspicious session behavior?
- Are there role assignment, group membership, or access policy changes near the alert window?
- Do related identities show similar patterns indicating broader targeting?

## Network Investigation Prompts
- Do source and destination patterns align with known business communication paths?
- Are unusual outbound destinations, ports, or protocols present?
- Is DNS activity consistent with normal resolver behavior and known domains?
- Do proxy logs show suspicious categories, downloads, or redirects?
- Do VPN events indicate anomalous login origin, device changes, or session overlap?
- Do firewall or WAF logs indicate scanning, exploitation attempts, or blocked high-risk traffic?
- Is there corroborating activity across IP, DNS, proxy, VPN, firewall, and WAF telemetry?

## MITRE ATT&CK Mapping
MITRE ATT&CK mapping helps analysts interpret activity as behavior patterns rather than isolated events. It supports consistent triage language, clearer escalation rationale, and better tuning prioritization.

High-level tactic examples to consider:
- Initial Access
- Credential Access
- Persistence
- Defense Evasion
- Discovery
- Lateral Movement
- Command and Control
- Exfiltration

Use mapping to strengthen triage documentation and to identify where detection coverage or investigation depth may need improvement.

## Safe Enrichment
Preferred safe enrichment sources include:
- Microsoft Sentinel incident entities
- Microsoft Defender portal context
- Entra ID sign-in logs
- Azure Activity
- Device timeline
- DNS, proxy, firewall, VPN, and WAF logs available in the workspace
- Internal asset inventory or approved CMDB
- Approved threat intelligence connectors configured by the organization

Third-party enrichment such as IP, domain, or hash reputation may be useful when approved by the organization, but it should not be a required dependency of this guide.

## Closure Notes Template
Use the following template for consistent closure notes:

- Summary: What happened and what was concluded.
- Entities reviewed: User, IP, host, domain, URL, hash, and related entities.
- Evidence reviewed: Key logs, alerts, timelines, and cross-source correlations.
- Enrichment performed: Internal and approved enrichment sources used.
- MITRE context: Tactics or techniques relevant to observed behavior.
- Reason for closure: Why the incident is closed, with evidence-based rationale.
- Business or known-good justification: Operational explanation when activity is expected.
- Escalation decision: Escalated or not escalated, with justification.
- Tuning recommendation: Suggested tuning or detection improvement, if applicable.

## Escalation Criteria
Escalation is generally appropriate when one or more of the following apply:
- Privileged identity is involved.
- Multiple entities are affected.
- Malicious indicator is confirmed by trusted evidence.
- Suspicious successful authentication is observed.
- Signs of lateral movement are present.
- Unusual cloud activity suggests elevated risk.
- Repeated alerts show increasing scope or impact.
- Evidence is insufficient to close safely.

## Tuning Candidates
An incident may be a tuning candidate when:
- Activity is repeatedly confirmed as known benign.
- Expected automation regularly triggers the same alert.
- Detection thresholds appear misconfigured for the environment.
- Entity context is missing and reduces analyst decision quality.
- The rule is consistently noisy without analyst value.
- Detection logic requires additional filters, grouping, or correlation context.

## What Not To Do
- Do not close incidents only because they are repetitive.
- Do not treat enrichment as absolute proof.
- Do not investigate private individuals outside the incident scope.
- Do not use leaked data sources or unapproved sources.
- Do not include customer names, internal processes, secrets, or sensitive data in notes.
- Do not suppress alerts without understanding the impact.
- Do not escalate without documenting evidence and reasoning.

## Related Microsoft Sentinel Content
This guide is intended to complement existing Microsoft Sentinel detections, hunting queries, playbooks, workbooks, and SOC process content.
