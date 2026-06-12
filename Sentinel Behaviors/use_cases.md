# UEBA Behaviors Use Cases

The Behaviors layer enhances the daily workflows of SOC analysts, threat hunters, and detection engineers by providing a unified, contextual view of security activity across diverse data sources.

---

## SOC Analyst Use Cases

SOC analysts can investigate incidents faster by querying behaviors tied to the entities involved in an incident.

### Query Behaviors by User Entity

Instead of reviewing dozens of separate API calls, query behaviors for a specific user:

```kql
let targetUser = "user@contoso.com";

let behaviorInfoFiltered =
    BehaviorInfo
    | where TimeGenerated > ago(1d)
    | project BehaviorId, Title, Categories, AttackTechniques;

BehaviorEntities
| where TimeGenerated > ago(1d)
| where AccountUpn == targetUser
| join kind=inner (behaviorInfoFiltered) on BehaviorId
| project TimeGenerated, Title, Categories, AttackTechniques
```

### Query Behaviors by MITRE ATT&CK Technique

Filter behaviors by specific MITRE techniques:

```kql
let targetTechniques = dynamic(["T1530", "T1078.004"]);

let behaviorInfoFiltered =
    BehaviorInfo
    | where TimeGenerated > ago(1d)
    | where AttackTechniques has_any (targetTechniques)
    | project BehaviorId, Title, AttackTechniques;

BehaviorEntities
| where TimeGenerated > ago(1d)
| join kind=inner (behaviorInfoFiltered) on BehaviorId
| summarize Count = count() by Title, AttackTechniques
```

### Query Behaviors by IP Address

Investigate all behaviors originating from a suspicious IP:

```kql
let suspiciousIP = "192.168.1.100";

let behaviorInfoFiltered =
    BehaviorInfo
    | where TimeGenerated > ago(7d)
    | project BehaviorId, Title, Categories, Severity;

BehaviorEntities
| where TimeGenerated > ago(7d)
| where EntityType == "Ip" and EntityValue == suspiciousIP
| join kind=inner (behaviorInfoFiltered) on BehaviorId
| project TimeGenerated, Title, Categories, Severity
| order by TimeGenerated desc
```

---

## Threat Hunter Use Cases

Threat hunters benefit from the ability to proactively search for behaviors mapped to MITRE tactics or specific patterns.

### Hunt for Persistence and Discovery Tactics

```kql
let behaviorInfo =
    BehaviorInfo
    | where TimeGenerated > ago(12h)
    | where Categories has "Persistence" or Categories has "Discovery"
    | project BehaviorId, Categories, Title, TimeGenerated;

BehaviorEntities
| where TimeGenerated > ago(12h)
| extend EntityName = coalesce(AccountUpn, DeviceName, CloudResourceId)
| join kind=inner (behaviorInfo) on BehaviorId
| summarize
    BehaviorTypes = make_set(Title),
    AffectedEntities = dcount(EntityName)
    by bin(TimeGenerated, 5m)
| where AffectedEntities > 5
```

### Find Rare Behaviors

Identify the least common behaviors that may indicate novel attack techniques:

```kql
BehaviorInfo
| where TimeGenerated > ago(5d)
| summarize
    Occurrences = dcount(BehaviorId),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
    by Title
| order by Occurrences asc
| take 20
```

### Hunt for Credential Access Patterns

```kql
BehaviorInfo
| where TimeGenerated > ago(24h)
| where Categories has "CredentialAccess" or AttackTechniques has "T1110"
| join kind=inner (
    BehaviorEntities
    | where TimeGenerated > ago(24h)
    | where EntityType == "Account"
) on BehaviorId
| summarize
    BehaviorCount = count(),
    UniqueAccounts = dcount(EntityValue)
    by Title
| order by BehaviorCount desc
```

---

## Detection Engineer Use Cases

Detection engineers can build simpler, more explainable rules using normalized, high-fidelity behaviors as building blocks.

### Create Alert from Behavior Pattern

Correlate access key creation with privilege escalation:

```kql
let keyCreationBehaviors =
    BehaviorInfo
    | where TimeGenerated > ago(1h)
    | where Title has "Access Key" and Title has "Creation"
    | project BehaviorId, KeyCreationTime = TimeGenerated;

let privilegeEscalationBehaviors =
    BehaviorInfo
    | where TimeGenerated > ago(1h)
    | where Categories has "PrivilegeEscalation"
    | project BehaviorId, EscalationTime = TimeGenerated;

BehaviorEntities
| where TimeGenerated > ago(1h)
| join kind=inner (keyCreationBehaviors) on BehaviorId
| join kind=inner (
    BehaviorEntities
    | where TimeGenerated > ago(1h)
    | join kind=inner (privilegeEscalationBehaviors) on BehaviorId
) on EntityValue
| where EscalationTime > KeyCreationTime
| where datetime_diff('minute', EscalationTime, KeyCreationTime) < 30
```

### Monitor High-Value Assets

Join behaviors with your organization's high-value asset list:

```kql
let highValueAssets = dynamic(["prod-database", "key-vault-001", "admin-account"]);

BehaviorEntities
| where TimeGenerated > ago(24h)
| where EntityValue has_any (highValueAssets)
| join kind=inner (
    BehaviorInfo
    | where TimeGenerated > ago(24h)
    | project BehaviorId, Title, Categories, Severity
) on BehaviorId
| summarize
    BehaviorCount = count(),
    BehaviorTypes = make_set(Title)
    by EntityValue
| order by BehaviorCount desc
```

### Build Behavior-Based Watchlist

Track entities with multiple suspicious behaviors:

```kql
BehaviorEntities
| where TimeGenerated > ago(7d)
| where EntityType == "Account"
| join kind=inner (
    BehaviorInfo
    | where TimeGenerated > ago(7d)
    | where Severity in ("Medium", "High")
    | project BehaviorId, Title, Severity
) on BehaviorId
| summarize
    TotalBehaviors = count(),
    UniqueBehaviorTypes = dcount(Title),
    BehaviorList = make_set(Title)
    by EntityValue
| where TotalBehaviors > 10
| order by TotalBehaviors desc
```

---

## Data Source Specific Queries

### AWS CloudTrail Behaviors

```kql
BehaviorInfo
| where TimeGenerated > ago(24h)
| where DataSources has "AWSCloudTrail"
| summarize Count = count() by Title, Categories
| order by Count desc
```

### CommonSecurityLog Behaviors (CyberArk, Palo Alto)

```kql
BehaviorInfo
| where TimeGenerated > ago(24h)
| where DataSources has "CommonSecurityLog"
| summarize Count = count() by Title, Categories
| order by Count desc
```

### GCP Audit Logs Behaviors

```kql
BehaviorInfo
| where TimeGenerated > ago(24h)
| where DataSources has "GCPAuditLogs"
| summarize Count = count() by Title, Categories
| order by Count desc
```

---

## Tips for Using Behaviors

1. **Start with entities** - Query behaviors tied to entities in your incidents
2. **Use MITRE mapping** - Filter by tactics/techniques relevant to your threat model
3. **Combine with other signals** - Join behaviors with alerts and anomalies
4. **Track rare behaviors** - Unusual behaviors often indicate novel attacks
5. **Build detection rules** - Use behaviors as building blocks for analytics rules
