# Exercise 7 — Okta MFA Factor Manipulation

**Rule:** `[E3] [Okta] MFA Factor Manipulation` _(the `[E3]` prefix is the deployed rule tag)_
**Deployed in:** `Artifacts/DetectionRules/rules.json`
**MITRE ATT&CK:** T1556.006 (Modify Authentication Process: Multi-Factor Authentication)
**Difficulty:** Intermediate

---

## Objective

Detect when an attacker manipulates MFA factors in Okta after compromising an account. Learn about identity-centric detection logic and how to enrich alerts with geolocation context.

## Background

After gaining access to an account (e.g., via phishing — Stage 1 of the Lab attack), adversaries often disable or reset MFA factors to maintain persistent access. This is a critical step in the attack chain because:

1. It removes the secondary authentication barrier
2. It allows the attacker to re-enrol their own MFA device
3. It may go unnoticed if the SOC isn't monitoring MFA lifecycle events

In the Lab scenario, the attacker compromises an Okta account via credential theft (S4) and then deactivates the victim's MFA factor to ensure continued access.

### Relevant Okta Event Types

| Event Type | Description |
|---|---|
| `user.mfa.factor.deactivate` | MFA factor removed from user |
| `user.mfa.factor.reset_all` | All MFA factors reset |
| `user.mfa.factor.update` | MFA factor configuration changed |

## Techniques Covered

### Filtering Identity Events

```kusto
OktaV2_CL
| where EventOriginalType in ("user.mfa.factor.deactivate",
    "user.mfa.factor.reset_all", "user.mfa.factor.update")
| where OriginalOutcomeResult == "SUCCESS"
```

Key points:
- The `in` operator matches against multiple event types
- Filtering on `SUCCESS` eliminates failed attempts (which are less actionable)
- `OktaV2_CL` is the ASIM-normalised Okta table in Sentinel

### Geolocation Enrichment

Okta pre-populates geolocation fields that add critical context:

| Column | Example | Use |
|---|---|---|
| `SrcGeoCountry` | `RU` | Flag foreign-origin MFA changes |
| `SrcGeoCity` | `Moscow` | Pinpoint source location |
| `SrcIpAddr` | `198.51.100.42` | Correlate with TI feeds |

### Entity Mapping

| Column | Entity Type | Mapping |
|---|---|---|
| `AccountUpn` (← `ActorUsername`) | User | Impacted Asset |
| `RemoteIP` (← `SrcIpAddr`) | IP | Related Evidence |

## Steps

### Step 1 — Verify Data Availability

> **Note:** This exercise requires **re-ingestion** of attack data. The original data load may not include MFA manipulation events. Run:
> ```
> .\Scripts\IngestCSV.ps1
> ```

Verify the events exist:

```kusto
OktaV2_CL
| where TimeGenerated > ago(4h)
| where EventOriginalType has "mfa"
| project TimeGenerated, ActorUsername, EventOriginalType, EventMessage, SrcIpAddr, SrcGeoCountry
```

### Step 2 — Review the Detection Query

Open the rule `[E3] [Okta] MFA Factor Manipulation` in Advanced Hunting and examine the query. Notice:

- It filters for three MFA-related event types
- It only alerts on successful operations
- It maps `ActorUsername` → `AccountUpn` for entity correlation

### Step 3 — Add Correlation with S4 (Challenge)

The MFA manipulation often happens **after** the account takeover detected by S4. Try adding a time-based correlation:

```kusto
let mfa_events = OktaV2_CL
| where TimeGenerated > ago(4h)
| where EventOriginalType in ("user.mfa.factor.deactivate",
    "user.mfa.factor.reset_all", "user.mfa.factor.update")
| where OriginalOutcomeResult == "SUCCESS"
| project MfaTime = TimeGenerated, ActorUsername, SrcIpAddr, EventOriginalType;
let foreign_logins = OktaV2_CL
| where TimeGenerated > ago(4h)
| where EventOriginalType == "user.session.start"
| where OriginalOutcomeResult == "SUCCESS"
| where SrcGeoCountry != "AU"
| project LoginTime = TimeGenerated, ActorUsername, SrcIpAddr, SrcGeoCountry;
mfa_events
| join kind=inner foreign_logins on ActorUsername, SrcIpAddr
| where MfaTime between (LoginTime .. LoginTime + 30m)
| project
    LoginTime,
    MfaTime,
    ActorUsername,
    SrcIpAddr,
    SrcGeoCountry,
    MfaAction = EventOriginalType
| extend
    TimeGenerated = LoginTime,
    AccountUpn = ActorUsername,
    RemoteIP = SrcIpAddr,
    ReportId = tostring(hash_sha256(strcat(ActorUsername, tostring(MfaTime))))
```

This correlates a foreign login with a subsequent MFA change within 30 minutes — much higher fidelity than standalone MFA alerts.

### Step 4 — Enable and Verify

1. Save the query (simple or correlated version)
2. Enable the rule
3. Verify the alert fires with the correct entity mapping

## Key Takeaways

- MFA lifecycle events are critical for detecting post-compromise activity
- Geolocation context (`SrcGeoCountry`) adds significant signal strength
- Correlating identity events across time windows (`between`) links reconnaissance to privilege escalation
- Always filter on `SUCCESS` for MFA changes — failed attempts are noise in this context

## Microsoft Learn References

- [Advanced hunting identity tables](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-identitylogonevents-table)
- [MITRE T1556.006 — Modify Authentication Process: MFA](https://attack.mitre.org/techniques/T1556/006/)
- [Custom detection rules](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules)
