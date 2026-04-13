# Exercise 10 — Table Management: Tiers & Retention

**Topic:** Configure table tiers, retention settings, and understand cost implications  
**Difficulty:** Beginner  
**Prerequisites:** Microsoft Sentinel workspace onboarded to the Defender portal (see [Onboarding](./Onboarding.md))

---

## Objective

Learn how to view and manage table settings in the Microsoft Defender portal. You will explore the **Tables** management screen, understand the difference between **Analytics** and **Data lake** tiers, change retention settings, and switch a table between tiers — all from the Defender portal.

## Background

### Where Does Your Data Live?

Data collected into Microsoft Sentinel is stored in **tables**. Each table can be configured independently with its own storage tier and retention period. This gives you fine-grained control over cost and performance.

Microsoft Sentinel supports two storage tiers:

| Tier | Description | Best For |
|---|---|---|
| **Analytics** | High-performance "hot" storage. Data is fully available for real-time analytics, hunting, alerting, workbooks, and all Sentinel features. | Active detections, threat hunting, incident investigation |
| **Data lake** | Low-cost "cold" storage. Data is not available for real-time analytics but can be accessed via KQL jobs, Spark jobs, and notebooks. | Compliance logging, historical trend analysis, forensics, low-touch data |

### Retention Periods

Within the analytics tier, there are two retention concepts:

| Setting | Range | Description |
|---|---|---|
| **Analytics retention** | 30 days – 2 years | How long data stays in the "hot" analytics tier for real-time querying |
| **Total retention** | Up to 12 years | Total data lifespan including analytics + data lake.|

> **Free storage:** Microsoft Sentinel solution tables (like `CommonSecurityLog`, `SecurityEvent`) get **90 days** of analytics retention for free. XDR tables get **30 days** included in the XDR license.

### Cost Implications

| Action | Cost Impact |
|---|---|
| Extending analytics retention beyond 90 days | Prorated monthly long-term retention charge |
| Extending total retention beyond analytics retention | Low-cost data lake storage charge for the additional duration |
| Moving a table from Analytics → Data lake tier | Eliminates analytics tier ingestion cost, but data loses real-time features |
| Moving a table from Data lake → Analytics tier | Re-enables real-time analytics, but incurs analytics tier ingestion cost |

**Example:** Setting analytics retention to 6 months and total retention to 1 year means data is "hot" for 6 months, then stored in the data lake for 6 additional months. You only pay data lake storage for those extra 6 months.

---

## Tables in This Lab

The Lab environment ingests data into the following tables. Understanding which tier each belongs to helps you decide where to optimise:

### Built-in / Sentinel Tables

| Table | Data Source | Tier |
|---|---|---|
| `CommonSecurityLog` | Palo Alto Networks firewall | Analytics |
| `AWSCloudTrail` | AWS CloudTrail | Analytics |
| `GCPAuditLogs` | Google Cloud audit logs | Analytics |
| `SecurityEvent` | Windows security events | Analytics |

### Custom Tables

| Table | Data Source | Tier |
|---|---|---|
| `OktaV2_CL` | Okta identity events | Analytics |
| `MailGuard365_Threats_CL` | MailGuard email threat data | Analytics |
| `OfficeActivity_CL` | Office 365 activity | Analytics |
| `PaloAlto_ThreatSummary_KQL_CL` | KQL job output (Exercise 11) | Analytics |

> **Key insight:** Not all tables need to stay in the analytics tier. For example, if `OfficeActivity_CL` is primarily used for compliance auditing rather than real-time detections, moving it to the data lake tier could reduce costs significantly.

---

## Steps

### Step 1 — Navigate to Table Management

1. Open the **Microsoft Defender portal** (https://security.microsoft.com)
2. In the left navigation, expand **Microsoft Sentinel**
3. Select **Configuration** → **Tables**
4. The Tables screen lists all tables in your workspace with their current tier and retention settings

<p align="center">
<img src="../Images/OnboardingImage16.png?raw=true">
</p>


> **Switching workspaces:** If you have multiple Sentinel workspaces, select the workspace name at the top left corner of the screen to switch between them.

---

### Step 2 — View Table Details

1. On the **Tables** screen, find `CommonSecurityLog` in the list
2. Select the table name to open the **table details side panel**
3. Review the information displayed:
   - **Table description** — what data the table contains
   - **Current tier** — Analytics or Data lake
   - **Analytics retention** — how long data stays in the hot tier
   - **Total retention** — total data lifespan including data lake

<p align="center">
<img src="../Images/OnboardingImage17.png?raw=true">
</p>

Questions to consider:
- What is the current analytics retention for `CommonSecurityLog`?
- Is the total retention different from the analytics retention?
- What workspace is the table stored in?

---

### Step 3 — Modify Retention Settings

In this step, you will extend the analytics retention for a custom table.

1. On the **Tables** screen, find `OktaV2_CL`
2. Select the table to open the details panel
3. Select **Manage table**
4. On the **Manage table** screen, you will see the current retention configuration
5. Change the **Analytics retention** to **180 days**
6. Note that the **Total retention** automatically adjusts — by default it matches the analytics retention
7. Optionally, set the **Total retention** to **1 year** to keep data in the data lake for an additional 185 days beyond the analytics retention
8. Review the warning messages — they explain the cost implications of your changes
9. Select **Save**

<p align="center">
<img src="../Images/OnboardingImage18.png?raw=true">
</p>


> **What happens behind the scenes:** When you reduce analytics retention, data beyond the new retention window moves to the data lake tier. When you increase it, existing data in the data lake that falls within the new retention window becomes available in the analytics tier. Changes take effect immediately.

---

### Step 4 — Change a Table's Tier to Data Lake

Moving a table to the data lake tier is useful for tables with high ingestion volume that you don't need for real-time detections. In this step, you will move `OfficeActivity_CL` to the data lake tier.

> **Warning:** Changing a table from Analytics to Data lake disables real-time features for that table, including:
> - Analytics rules and custom detection rules
> - Advanced hunting queries
> - Workbooks and alerting
>
> Only move tables that you are certain don't need real-time analytics.

1. On the **Tables** screen, find `OfficeActivity_CL`
2. Select the table, then select **Manage table**
3. Under **Tier**, change from **Analytics** to **Data lake**
4. Set the **Retention** (30 days to 12 years)
5. Review the warning message about features that will stop working
6. Select **Save**

<p align="center">
<img src="../Images/OnboardingImage19.png?raw=true">
</p>


---

### Step 5 — Change a Table's Tier Back to Analytics

Now reverse the change to restore real-time capabilities:

1. On the **Tables** screen, find `OfficeActivity_CL` (it should now show as Data lake tier)
2. Select the table, then select **Manage table**
3. Under **Tier**, change from **Data lake** back to **Analytics**
4. Set the **Analytics retention** and **Total retention** as desired
5. Select **Save**

<p align="center">
<img src="../Images/OnboardingImage20.png?raw=true">
</p>


---

### Step 6 — Understand the Impact on Detections

The tier a table lives in directly affects which detection rules can query it. Review the following to understand the relationship:

| Feature | Analytics Tier | Data Lake Tier |
|---|---|---|
| Custom detection rules | Yes | No |
| Analytics rules | Yes | No |
| Advanced Hunting | Yes | No |
| KQL jobs (Exercise 11) | Yes | Yes |
| Summary rules | Yes | Yes |
| Notebooks | Yes | Yes |
| Workbooks | Yes | No |

**Practical example from this Lab:**

- The `CommonSecurityLog` table **must** stay in the analytics tier because detection rules like `Lab Stage 3.5 Internal Port Scan` and `Lab Stage 6 Large Data Exfiltration` query it in real time
- The `PaloAlto_ThreatSummary_KQL_CL` table **must** stay in the analytics tier because the `[S8]` detection rule queries it
- However, `OfficeActivity_CL` could potentially be moved to the data lake tier if no active detection rules reference it, and you could use a KQL job (Exercise 11) to promote relevant data when needed

---

## Key Takeaways

- The **Tables** screen in the Defender portal gives you a centralised view of all tables and their settings
- **Analytics tier** = hot storage with full real-time capabilities; **Data lake tier** = cold storage at lower cost
- **Analytics retention** controls how long data stays hot (30 days – 2 years); **Total retention** extends data lifespan in the data lake (up to 12 years)
- Always review active detection rules before changing a table's tier to avoid breaking detections
- A copy of the data in the Analytics tier is **automatically available in the data lake tier at no extra cost**, ensuring a unified copy of security data for both tiers.

## Microsoft Learn References

- [Configure table settings in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/manage-table-tiers-retention)
- [Manage data tiers and retention in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/manage-data-overview)
- [Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview)
- [Understand the full billing model for Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/billing)
