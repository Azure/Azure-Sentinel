# Exercise 2 — Threat Intelligence: Microsoft Defender Threat Intelligence

**Topic:** Enable the MDTI data connector and query the `ThreatIntelIndicators` table
**Difficulty:** Beginner

---

### Objective

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

#### Step 1 — Enable the MDTI Data Connector

1. Open the **Microsoft Defender portal** (https://security.microsoft.com)
2. Navigate to **Microsoft Sentinel** → **Configuration** → **Data connectors**
3. Search for **Microsoft Defender Threat Intelligence**
4. Select the connector and click **Open connector page**

<p align="center">
<img src="../Images/OnboardingImage24.png?raw=true">
</p>

5. On the connector page, review the **Prerequisites** section:
   - Your workspace must have Microsoft Sentinel enabled
   - You need at least **Security Reader** permissions

6. Under **Configuration**, select **Connect** to enable the connector

<p align="center">
<img src="../Images/OnboardingImage23.png?raw=true">
</p>

7. Once connected, the **Status** changes to **Connected**. Indicators will begin ingesting within a few minutes.

> **Note:** It can take up to **15 minutes** for the first indicators to appear in the `ThreatIntelIndicators` table. The connector ingests indicators continuously after that.

#### Step 2 — Verify Indicator Ingestion

Once the connector is enabled, verify that indicators are flowing into your workspace:

```kusto
ThreatIntelIndicators
| summarize IndicatorCount = count() by IndicatorType
| sort by IndicatorCount desc
```

You should see indicators of type `ipv4-addr`, `domain-name`, `url`, and `file` (with hash sub-types).

Explore the most recent indicators:

```kusto
ThreatIntelIndicators
| where TimeGenerated > ago(24h)
| project
    TimeGenerated,
    IndicatorType,
    IndicatorValue = coalesce(NetworkIP, DomainName, Url, FileHashValue),
    Confidence,
    ThreatType,
    Description,
    Source
| sort by TimeGenerated desc
| take 20
```

#### Step 3 — Understand the ThreatIntelIndicators Schema

The `ThreatIntelIndicators` table has a rich schema designed for correlation:

| Column | Description | Example |
|---|---|---|
| `IndicatorType` | Type of IOC | `ipv4-addr`, `domain-name`, `file` |
| `NetworkIP` | Malicious IP address | `198.51.100.42` |
| `DomainName` | Malicious domain | `evil-c2-server.xyz` |
| `Url` | Malicious URL | `https://phishing-site.com/login` |
| `FileHashValue` | Malicious file hash | `e3b0c44298fc1c14...` |
| `FileHashType` | Hash algorithm | `SHA256`, `SHA1`, `MD5` |
| `Confidence` | Indicator confidence (0-100) | `85` |
| `ThreatType` | Threat classification | `C2`, `Botnet`, `Phishing` |
| `Description` | Human-readable description | `Known APT28 C2 infrastructure` |
| `Source` | Intelligence provider | `Microsoft Threat Intelligence` |
| `ValidFrom` / `ValidUntil` | Indicator validity time window | Datetime values |
| `Action` | Recommended action | `alert`, `block` |
| `IsActive` | Whether the indicator is currently active | `true` |

#### Step 4 — Match Indicators Against Your Telemetry

The real power of TI is correlating indicators against your environment's data. Use `join` to find matches between MDTI indicators and your firewall logs:

```kusto
let ti_ips = ThreatIntelIndicators
| where IsActive == true
| where IndicatorType == "ipv4-addr"
| where Confidence > 50
| project NetworkIP, Confidence, ThreatType, Description, Source;
CommonSecurityLog
| where DeviceVendor == "Palo Alto Networks"
| join kind=inner ti_ips on $left.DestinationIP == $right.NetworkIP
| project
    TimeGenerated,
    SourceIP,
    DestinationIP,
    DeviceAction,
    TI_Confidence = Confidence,
    TI_ThreatType = ThreatType,
    TI_Description = Description,
    TI_Source = Source
| sort by TimeGenerated desc
```

Try the same for AWS CloudTrail:

```kusto
let ti_ips = ThreatIntelIndicators
| where IsActive == true
| where IndicatorType == "ipv4-addr"
| where Confidence > 50
| project NetworkIP, Confidence, ThreatType;
AWSCloudTrail
| join kind=inner ti_ips on $left.SourceIpAddress == $right.NetworkIP
| project
    TimeGenerated,
    UserIdentityUserName,
    EventName,
    SourceIpAddress,
    TI_Confidence = Confidence,
    TI_ThreatType = ThreatType
| sort by TimeGenerated desc
```

#### Step 5 — Explore Indicator Statistics

Get an overview of your threat intelligence coverage:

```kusto
ThreatIntelIndicators
| where IsActive == true
| summarize
    TotalIndicators = count(),
    AvgConfidence = avg(Confidence),
    Sources = make_set(Source)
    by IndicatorType
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
<img src="../Images/OnboardingImage25.png?raw=true">
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
