# Cross-Source Attack Chain Graph

A custom Microsoft Sentinel graph notebook that traces a multi-stage attack across **6 data sources** — linking users, devices, IPs, cloud accounts, and email threats through shared entities to reveal the complete kill chain.

## Data Sources

| Source | Table | Content |
|--------|-------|---------|
| CrowdStrike | `CrowdStrikeDetections` | Endpoint alerts with MITRE ATT&CK tactics |
| CrowdStrike | `CrowdStrikeHosts` | Device inventory (hostname, OS, IP) |
| Palo Alto | `CommonSecurityLog` | Firewall traffic — scans, allow, deny, exfil |
| AWS | `AWSCloudTrail` | Cloud API activity (S3, EC2, IAM) |
| GCP | `GCPAuditLogs` | Cloud infrastructure events |
| Okta | `OktaV2_CL` | Identity events — logins, MFA, failures |
| MailGuard | `MailGuard365_Threats_CL` | Phishing emails with threat verdicts |

## Graph Schema

### Nodes (6 types)

| Type | Key | Description |
|------|-----|-------------|
| **User** | UPN | Unique user identities from all sources |
| **Device** | Hostname | Endpoint devices from CrowdStrike |
| **IPAddress** | IP | External IP addresses from all sources |
| **AttackStage** | Tactic | MITRE ATT&CK tactics and cloud attack categories |
| **CloudAccount** | User@Cloud | AWS and GCP cloud identities |
| **EmailThreat** | SubjectHash | Phishing email subjects with threat verdicts |

### Edges (8 types)

| Type | Source → Target | Description |
|------|-----------------|-------------|
| **TriggeredAlert** | Device → AttackStage | Endpoint detection linked to MITRE tactic |
| **LoggedInFrom** | User → IPAddress | Okta sign-in with geo context |
| **NetworkActivity** | IPAddress → IPAddress | Firewall traffic between IPs |
| **PerformedAction** | CloudAccount → AttackStage | Cloud API call (AWS/GCP) |
| **ReceivedEmail** | User → EmailThreat | Phishing email delivered to user |
| **UsedIP** | User → IPAddress | User associated with an IP address |
| **OwnedDevice** | User → Device | User-to-device mapping |
| **CloudIdentity** | User → CloudAccount | Maps on-prem user to cloud identity |

## Prerequisites

- Microsoft Sentinel workspace with the **data lake** enabled
- Lab data ingested (all 6 data sources populated)
- VS Code with the **Microsoft Sentinel** extension installed
- At least **Security Reader** permissions on the workspace

## Usage

1. Open `cross_source_attack_chain_graph.ipynb` in VS Code
2. Update the `WORKSPACE_NAME` variable in cell 3 to match your Sentinel workspace
3. Connect a Spark kernel (Medium pool recommended)
4. Run all cells in order
5. After the graph builds, query it with GQL or materialize it as a scheduled graph job

## Materialization

After building the graph interactively, you can schedule it as a recurring job:

1. In the Defender portal, go to **Microsoft Sentinel → Graphs**
2. Click **Create Scheduled Job** → **Create a Graph Job**
3. Set the notebook path and choose **On demand** or **Scheduled** frequency
4. On-demand graphs have a 30-day retention by default
