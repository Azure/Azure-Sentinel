# Exercise 2 — Threat Intelligence: Microsoft Defender Threat Intelligence

**Topic:** Enable the MDTI data connector and query the `ThreatIntelIndicators` table  
**Difficulty:** Beginner  
**Prerequisites:** None

---

## Objective

Enable the **Microsoft Defender Threat Intelligence (MDTI)** data connector in Microsoft Sentinel to ingest threat intelligence indicators, then use the `ThreatIntelIndicators` table to match IOCs against your environment's telemetry.

### Background

Microsoft Defender Threat Intelligence (MDTI) is Microsoft's curated threat intelligence platform. It provides high-fidelity indicators of compromise (IOCs) — IP addresses, domains, URLs, and file hashes — derived from Microsoft's global threat monitoring infrastructure.

When you enable the MDTI data connector, indicators are automatically ingested into the **`ThreatIntelIndicators`** table in your Sentinel workspace. This table replaces the legacy `ThreatIntelligenceIndicator` table and provides a richer, more structured schema.

> **Important:** The table name is **`ThreatIntelIndicators`** (not `ThreatIntelligenceIndicator`). This is the current table used by the MDTI connector.

#### Why MDTI?

| Benefit | Description |
|---|---|
| **Curated by Microsoft** | Indicators come from Microsoft's threat research teams, not raw open-source feeds |
| **Automatically enriched** | Each indicator includes context — threat actor, campaign, confidence, and associated articles |
| **Integrated with Sentinel** | Works natively with analytics rules, workbooks, and hunting queries |
| **No additional licence required** | MDTI (standard tier) is included with Microsoft Sentinel |

> **Reference:** [Microsoft Defender Threat Intelligence in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence#microsoft-defender-threat-intelligence)

---

### Steps

#### Step 1 — Install the Threat Intelligence Solution and Enable the MDTI Data Connector

1. Open the **Microsoft Defender portal** (https://security.microsoft.com)
2. Navigate to **Microsoft Sentinel** → **Content management** → **Content hub**
3. Search for **Threat Intelligence** and select the **Threat Intelligence (NEW)** solution (marked as **Featured**)
4. Click **Install/Update** to deploy the solution — this includes the MDTI data connector, analytics rules, workbooks, and hunting queries

<p align="center">
<img src="../Images/OnboardingImage24.png?raw=true" alt="Threat Intelligence (NEW) solution in the Content Hub" width="800">
</p>

5. After installation, navigate to **Microsoft Sentinel** → **Configuration** → **Data connectors**
6. Search for **Microsoft Defender Threat Intelligence**
7. Select the connector and click **Open connector page**
8. Under **Configuration**, select **Connect** to enable the connector

<p align="center">
<img src="../Images/OnboardingImage23.png?raw=true" alt="MDTI data connector configuration page" width="800">
</p>

9. Once connected, the **Status** changes to **Connected**. Indicators will begin ingesting within a few minutes.

> **Note:** It can take up to **15 minutes** for the first indicators to appear in the `ThreatIntelIndicators` table. The connector ingests indicators continuously after that.

#### Step 2 — Verify Indicator Ingestion

Once the connector is enabled, verify that indicators are flowing into your workspace:

```kusto
ThreatIntelIndicators
| summarize IndicatorCount = count() by ObservableKey
| sort by IndicatorCount desc
```

You should see observable types like `ipv4-addr`, `domain-name`, `url`, and file hash patterns.

Explore the most recent indicators:

```kusto
ThreatIntelIndicators
| where TimeGenerated > ago(24h)
| project
    TimeGenerated,
    ObservableKey,
    ObservableValue,
    Confidence,
    IsActive,
    ValidFrom,
    ValidUntil
| sort by TimeGenerated desc
| take 20
```

#### Step 3 — Understand the ThreatIntelIndicators Schema

The `ThreatIntelIndicators` table stores STIX-formatted threat intelligence indicators:

| Column | Description | Example |
|---|---|---|
| `ObservableKey` | Type of IOC (from the STIX pattern) | `ipv4-addr`, `domain-name`, `file:hashes.'SHA-256'` |
| `ObservableValue` | The actual IOC value | `198.51.100.42`, `evil-c2-server.xyz` |
| `Pattern` | Full STIX detection pattern | `[ipv4-addr:value = '198.51.100.42']` |
| `Confidence` | Indicator confidence (0-100) | `85` |
| `Data` | Full STIX object as dynamic JSON (contains additional context like threat type, description, labels) | `{"type":"indicator",...}` |
| `ValidFrom` / `ValidUntil` | Indicator validity time window | Datetime values |
| `IsActive` | Whether the indicator is currently active | `true` |
| `Created` / `Modified` | When the indicator was created/updated | Datetime values |
| `Tags` | Sentinel-defined tags | Labels and categories |

> **Tip:** Use the `Data` column to extract additional context like threat type and description: `| extend ThreatType = tostring(Data.indicator_types[0])`

#### Step 4 — Match Indicators Against Your Telemetry

The real power of TI is correlating indicators against your environment's data. Use `join` to find matches between MDTI indicators and your firewall logs:

```kusto
let ti_ips = ThreatIntelIndicators
| where IsActive == true
| where ObservableKey == "ipv4-addr"
| where Confidence > 50
| project ObservableValue, Confidence;
CommonSecurityLog
| where DeviceVendor == "Palo Alto Networks"
| join kind=inner ti_ips on $left.DestinationIP == $right.ObservableValue
| project
    TimeGenerated,
    SourceIP,
    DestinationIP,
    DeviceAction,
    TI_Confidence = Confidence
| sort by TimeGenerated desc
```

Try the same for AWS CloudTrail:

```kusto
let ti_ips = ThreatIntelIndicators
| where IsActive == true
| where ObservableKey == "ipv4-addr"
| where Confidence > 50
| project ObservableValue, Confidence;
AWSCloudTrail
| join kind=inner ti_ips on $left.SourceIpAddress == $right.ObservableValue
| project
    TimeGenerated,
    UserIdentityUserName,
    EventName,
    SourceIpAddress,
    TI_Confidence = Confidence
| sort by TimeGenerated desc
```

> **Note:** These queries may return **empty results** in the lab environment -- this is expected. The lab's pre-ingested telemetry uses synthetic IP addresses that are unlikely to appear in Microsoft's real-world threat intelligence feed. In a production environment with live traffic, these joins are how you detect connections to known-malicious infrastructure.
>
> **What to take away:** The query *pattern* is what matters -- `join kind=inner` between a TI indicator table and your telemetry. You can apply this same pattern to any data source (firewall logs, cloud trails, identity events) in your production workspace where real traffic will match real indicators.

#### Step 5 — Explore Indicator Statistics

Get an overview of your threat intelligence coverage:

```kusto
ThreatIntelIndicators
| where IsActive == true
| summarize
    TotalIndicators = count(),
    AvgConfidence = avg(Confidence)
    by ObservableKey
| sort by TotalIndicators desc
```

Check the age distribution of your indicators — stale indicators should be reviewed:

```kusto
ThreatIntelIndicators
| where IsActive == true
| extend AgeInDays = datetime_diff('day', now(), ValidFrom)
| summarize count() by AgeCategory = case(
    AgeInDays <= 7, "Last 7 days",
    AgeInDays <= 30, "Last 30 days",
    AgeInDays <= 90, "Last 90 days",
    "Older than 90 days"
)
```

#### Step 6 — Review the Threat Intelligence Blade

Microsoft Sentinel provides a dedicated UI for managing threat intelligence:

1. Navigate to **Microsoft Sentinel** → **Threat management** → **Threat intelligence**
2. Review the indicators that have been ingested
3. Use the filters to search by indicator type, source, or confidence level
4. Select an indicator to view its full details, including associated threat actors and campaigns

<p align="center">
<img src="../Images/OnboardingImage25.png?raw=true" alt="ThreatIntelIndicators query results in Advanced Hunting" width="800">
</p>

> **Tip:** You can also manually add indicators from this blade, upload STIX files, or connect additional TI feeds (e.g., TAXII servers, open-source feeds).

---

### Key Takeaways

- The **MDTI data connector** provides curated, high-confidence threat intelligence from Microsoft at no additional cost
- Indicators are ingested into the **`ThreatIntelIndicators`** table — use this table (not the legacy `ThreatIntelligenceIndicator`)
- Use `join kind=inner` to correlate TI indicators against your environment's logs
- Filter on `IsActive == true` and `Confidence > 50` to focus on actionable indicators
- The **Threat intelligence blade** in Sentinel provides a UI for browsing, filtering, and managing indicators
- TI matching works across all data sources — firewall logs, cloud trails, identity events, and more

### Microsoft Learn References

- [Microsoft Defender Threat Intelligence in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence)
- [Connect Microsoft Defender Threat Intelligence data connector](https://learn.microsoft.com/en-us/azure/sentinel/connect-mdti-data-connector)
- [Work with threat indicators in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/work-with-threat-indicators)
- [ThreatIntelIndicators table schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/threatintelindicators)

---

## Next Steps

Continue to **[Exercise 3 — MITRE ATT&CK Coverage](./E03_mitre_attack_coverage.md)**
