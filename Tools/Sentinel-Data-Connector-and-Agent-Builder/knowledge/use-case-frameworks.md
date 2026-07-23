# Agentic Use Case Frameworks for ISV Developers

## Overview

ISV developers building Security Copilot agents should align their solution with one of six security domain frameworks. Each framework defines:
- The security problem being solved
- What data signals are needed
- How to correlate ISV data with Sentinel/Microsoft data
- The investigation workflow for SOC analysts

## Framework 1: Identity Intelligence

**Security Problem:** Detecting identity-based threats, unauthorized access, privilege escalation

**ISV Data Signals:**
- Authentication events (success/failure)
- Privilege access patterns
- Identity risk scores
- MFA challenge outcomes
- Session anomalies

**Correlation Opportunities:**
- Cross-reference with Entra ID SignInLogs
- Correlate with AADRiskDetection events
- Map to Microsoft Defender for Identity alerts
- Combine with endpoint process execution data

**Investigation Scenario Example:**
"A user shows unusual authentication from a new geography → MFA bypassed → privileged access to production resources → was this legitimate or an initial access event?"

---

## Framework 2: Cyber Resilience

**Security Problem:** Ensuring backup integrity, detecting ransomware, validating recovery readiness

**ISV Data Signals:**
- Backup job status and success/failure
- Data change rates (indicating possible encryption)
- Recovery point objectives met/missed
- Anomalous deletion patterns
- Snapshot integrity verification

**Correlation Opportunities:**
- Correlate backup anomalies with Microsoft Defender for Endpoint alerts
- Cross-reference with file modification events
- Map to known ransomware IOCs in Sentinel ThreatIntelligence
- Combine with network session data for lateral movement

**Investigation Scenario Example:**
"Backup success rate dropped from 99% to 40% → large-scale file encryption detected → correlate with endpoint alerts → determine blast radius and recovery plan"

---

## Framework 3: Network Access Control

**Security Problem:** Detecting unauthorized network access, segmentation violations, lateral movement

**ISV Data Signals:**
- Network flow data (allow/deny)
- Segmentation policy violations
- Micro-segmentation enforcement logs
- East-west traffic anomalies
- Zero trust policy decisions

**Correlation Opportunities:**
- Correlate with Microsoft Defender for Cloud network alerts
- Cross-reference with Azure NSG flow logs
- Map to identity events for user-to-resource access
- Combine with vulnerability data for exploitable paths

**Investigation Scenario Example:**
"Workload A communicating with Workload B for the first time → segmentation policy violation → correlate with identity of the initiator → was this authorized change or lateral movement?"

---

## Framework 4: Endpoint Detection & Response (EDR)

**Security Problem:** Detecting endpoint threats, malware, suspicious process execution

**ISV Data Signals:**
- Process creation/execution events
- File system modifications
- Registry changes
- Network connections from endpoints
- Behavioral anomaly scores

**Correlation Opportunities:**
- Correlate with Microsoft Defender for Endpoint DeviceProcessEvents
- Cross-reference with Sentinel SecurityEvent table
- Map to MITRE ATT&CK techniques
- Combine with identity data for user attribution

**Investigation Scenario Example:**
"Unknown process executed → making outbound connections to suspicious domain → correlate with DNS logs and threat intel → determine if C2 communication"

---

## Framework 5: Asset Exploitability

**Security Problem:** Prioritizing vulnerability remediation based on exploitability and exposure

**ISV Data Signals:**
- Vulnerability scan results
- Asset inventory and criticality
- Exploit availability data
- Attack surface exposure scores
- Patch compliance status

**Correlation Opportunities:**
- Correlate with Microsoft Defender Vulnerability Management
- Cross-reference with Azure Resource Graph for asset context
- Map to active threat campaigns targeting these vulnerabilities
- Combine with network exposure data

**Investigation Scenario Example:**
"Critical vulnerability found on production server → exploit is publicly available → server is internet-facing → correlate with any exploitation attempts in network logs"

---

## Framework 6: Threat Intelligence

**Security Problem:** Operationalizing threat intelligence for proactive defense

**ISV Data Signals:**
- IOCs (IPs, domains, file hashes)
- Threat actor profiles
- Campaign tracking data
- Dark web monitoring
- Brand impersonation detection

**Correlation Opportunities:**
- Correlate IOCs with Sentinel ThreatIntelligenceIndicator table
- Cross-reference with network flow and DNS data
- Map to active incidents for attribution
- Combine with vulnerability data for threat-vulnerability intersection

**Investigation Scenario Example:**
"New IOC published by threat intel feed → scan all historical logs for matches → identify any communication with malicious infrastructure → assess scope of potential compromise"

---

## How to Use This Framework

1. **Identify your domain** — Which framework best matches your product?
2. **Map your signals** — What specific data does your product generate?
3. **Design correlation** — How does your data combine with Microsoft/Sentinel data?
4. **Build the scenario** — What question does the SOC analyst need answered?
5. **Create the agent** — Build instructions that execute this investigation workflow
