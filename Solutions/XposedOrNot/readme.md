# XposedOrNot Breach Intelligence Solution for Microsoft Sentinel

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/XposedOrNot.svg" alt="XposedOrNot Logo" width="75" height="75">

## Overview

The XposedOrNot solution for Microsoft Sentinel ingests breach exposure data for your verified domains and raises incidents when new exposures appear.

[XposedOrNot](https://xposedornot.com) tracks exposed records across verified data breaches. Any domain you verify in your XposedOrNot account is monitored automatically on the next poll.

## Solution Contents

| Content Type | Name | Description |
|--------------|------|-------------|
| **Data Connector** | XposedOrNot Breach Intelligence | Codeless Connector Framework (CCF) connector that polls the XposedOrNot API on the schedule you choose |
| **Parser** | XposedOrNotBreachExposures | Joins exposed email addresses with breach details and returns one row per email and breach |
| **Analytic Rule** | XposedOrNot - New Breach Exposure Detected | Creates an incident for each new breach affecting a monitored domain |
| **Workbook** | XposedOrNot Breach Intelligence | Exposure analytics, risk breakdown and timeline views |

## Prerequisites

- Microsoft Sentinel-enabled Log Analytics workspace
- XposedOrNot API key:
  - **Community (free)**: [XposedOrNot dashboard](https://xposedornot.com/dashboard)
  - **Enterprise**: [plus.xposedornot.com](https://plus.xposedornot.com)
  - Help: [how to get an API key for domain breach data](https://xposedornot.com/faq#collapse102)
- At least one domain verified in your XposedOrNot account

## Setup

1. In **Microsoft Sentinel** > **Content hub**, search for "XposedOrNot" and select **Install**.
2. Open **Data connectors** > **XposedOrNot Breach Intelligence** > **Open connector page**.
3. Enter your API key, choose a refresh schedule (every hour, 6 hours, 12 hours or day) and select **Connect**.
4. In **Analytics** > **Rule templates**, create a rule from **XposedOrNot - New Breach Exposure Detected**. The rule is installed as a template and raises no incidents until you create it.
5. In **Workbooks** > **Templates**, save **XposedOrNot Breach Intelligence** to view the dashboard.

The first data can take up to 30 minutes to appear after you connect. Exposures are refreshed on the schedule you choose; the breach catalog is refreshed once a day.

To change the API key or the refresh schedule, disconnect and connect again.

## How alerting works

- The first sync of each domain is a baseline and raises no incidents.
- After that, every breach that newly affects a monitored domain raises one alert listing the number of exposed email addresses.
- Breaches added to XposedOrNot in the last 7 days are always reported, including on the first sync.
- Severity is High when the breach exposed plaintext or easy to crack passwords, otherwise Medium.

## Data Schema

**Table:** `XposedOrNotExposures_CL`

| Column | Type | Description |
|--------|------|-------------|
| TimeGenerated | datetime | Ingestion timestamp |
| Email | string | Exposed email address |
| EmailDomain | string | Domain part of the email address |
| Domain | string | Monitored domain |
| BreachName | string | XposedOrNot breach identifier |

**Table:** `XposedOrNotBreachCatalog_CL`

| Column | Type | Description |
|--------|------|-------------|
| TimeGenerated | datetime | Ingestion timestamp |
| BreachName | string | XposedOrNot breach identifier |
| BreachedDate | datetime | When the breach occurred |
| AddedDate | datetime | When the breach was added to XposedOrNot |
| BreachDomain | string | Domain of the breached organization |
| Industry | string | Industry of the breached organization |
| BreachType | string | Type of breach |
| PasswordRisk | string | plaintext, easytocrack, hardtocrack or unknown |
| ExposedData | dynamic | Data types exposed in the breach |
| ExposedRecords | long | Number of records in the breach |
| BreachDescription | string | Description of the breach |
| IsSearchable | boolean | Whether the breach is searchable |
| IsSensitive | boolean | Whether the breach is flagged as sensitive |
| IsVerified | boolean | Whether the breach is verified |
| ReferenceUrl | string | Reference link |
| LogoUrl | string | Logo of the breached organization |

Both tables receive a full snapshot on every poll. Use the `XposedOrNotBreachExposures` parser for a de-duplicated view.

## Sample Queries

**High-risk password exposures:**
```kusto
XposedOrNotBreachExposures
| where PasswordRisk in ('plaintext', 'easytocrack')
| summarize Breaches = make_set(BreachName) by Email, Domain
```

**Exposures by domain:**
```kusto
XposedOrNotBreachExposures
| summarize ExposedEmails = dcount(Email), Breaches = dcount(BreachName) by Domain
| order by ExposedEmails desc
```

## Support

- **Documentation**: [XposedOrNot API Docs](https://api.xposedornot.com/docs)
- **Contact**: [plus.xposedornot.com/contact](https://plus.xposedornot.com/contact)
- **Email**: help@xposedornot.com

## Version History

See [ReleaseNotes.md](ReleaseNotes.md) for detailed version history.
