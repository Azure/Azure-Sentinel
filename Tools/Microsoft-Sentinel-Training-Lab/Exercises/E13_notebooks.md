# Exercise 13 — Data Lake Notebooks

In this exercise you will use **Jupyter notebooks** to perform an interactive security investigation against the Microsoft Sentinel data lake. Notebooks combine code, visualisations, and narrative in a single document — making them ideal for deep-dive threat hunting, repeatable analysis, and sharing findings with your SOC team.

The lab includes a ready-made notebook (**Lab_Notebook.ipynb**) that analyses Palo Alto firewall logs from the `CommonSecurityLog` table. You will open it in VS Code, connect to the Sentinel Spark engine, and run each analysis cell to investigate the PoCaaS attack scenario data.

---

## Prerequisites

Before running notebooks you need:

1. **Data lake enabled** — the Sentinel data lake must be onboarded on your workspace.
2. **VS Code with the Microsoft Sentinel extension** — install it from the Extensions Marketplace (search for *Microsoft Sentinel*).
3. **GitHub Copilot extension** (optional) — provides code completion and suggestions inside notebook cells.
4. **Permissions** — your account needs at least **Security Reader** on the workspace. To write custom tables back to the analytics tier, the data lake managed identity also needs **Log Analytics Contributor**.

> **Full setup guide:** [Run notebooks on the Microsoft Sentinel data lake — Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/datalake/notebooks)

---

## Step 1 — Open the Notebook

1. In VS Code, open the file **Notebook/Lab_Notebook.ipynb** from this training repo.
2. Click the **Microsoft Sentinel** shield icon in the left toolbar and sign in when prompted.
3. Once signed in, the extension shows your data lake **tables** and **jobs** in the sidebar.

---

## Step 2 — Update the Workspace Name

In cell 5 (the parameters cell), update the `workspace_name` variable to match your Sentinel workspace:

```python
workspace_name = "<YOUR_WORKSPACE_NAME>"
```

Replace `<YOUR_WORKSPACE_NAME>` with the name of your Sentinel workspace (e.g. the one you created during onboarding).

---

## Step 3 — Select a Runtime Pool

When you run the first code cell, VS Code asks you to choose a runtime:

| Pool | Best For |
|------|----------|
| **Small** | Lightweight exploration, testing, cost-efficient |
| **Medium** | Joins, aggregations, ML model training |
| **Large** | Deep learning, large joins, time-critical workloads |

> **Note:** The first session start takes **3–5 minutes** while Spark provisions. Subsequent cells run much faster within the same session.

For this exercise, **Medium** is recommended.

---

## Step 4 — Run the Analysis

The notebook walks you through a complete Palo Alto firewall investigation in 12 steps. Run each cell in order — the markdown cells explain what each analysis does, and the code cells produce the results.

### What the Notebook Covers

| # | Section | What It Does | Output |
|---|---------|-------------|--------|
| 1 | **Setup & Connection** | Initialises `MicrosoftSentinelProvider` and lists available workspaces | Text — workspace list |
| 2 | **Configure Parameters** | Sets time window, workspace name, input/output tables, vendor filter | Text — config summary |
| 3 | **Load & Prepare Data** | Reads `CommonSecurityLog`, filters to Palo Alto, enriches with `TotalBytes` and `IsExternal` | Text — schema + event counts (TRAFFIC vs THREAT) |
| 4 | **Traffic Overview** | Event distribution by class and action; volume over time in 15-minute bins | **Sunburst chart** + **area chart** |
| 5 | **Top Talkers** | Busiest source → destination pairs by sessions and bytes transferred | **Dual bar chart** (top 15 pairs) |
| 6 | **Protocol & Port Heatmap** | Destination port usage grouped by protocol | **Treemap** (top 30 ports) |
| 7 | **Beaconing Detection** | Computes inter-arrival jitter per IP pair — low jitter = C2 beaconing | **Scatter plot** (jitter vs interval) |
| 8 | **DNS Tunnelling Analysis** | Flags sources with anomalously large DNS payloads (> 512 bytes) | **Bar chart** with 512-byte threshold line |
| 9 | **Data Exfiltration** | Large outbound transfers to external IPs; sent/received ratio analysis | **Scatter plot** (MB sent vs ratio) |
| 10 | **Threat Breakdown** | IDS/IPS threat categories (spyware, URL filtering, exploits) by action | **Stacked bar chart** |
| 11 | **Attack Timeline** | All suspicious and threat events plotted chronologically by destination port | **Timeline scatter** (size = bytes) |
| 12 | **Save Results** | Persists enriched DataFrame to `PaloAlto_Investigation_SPRK` in the data lake | Text — confirmation + row count |

### Key Concepts Demonstrated

- **`MicrosoftSentinelProvider`** — the Python class that connects Spark to Sentinel. It reads tables, lists databases, and writes results back.
- **PySpark DataFrames** — all analysis runs on Spark, so it scales to billions of rows without loading everything into memory.
- **Plotly visualisations** — interactive charts rendered directly in the notebook output cells.
- **Data lake write-back** — results saved with `_SPRK` suffix go to the data lake tier; `_SPRK_CL` suffix promotes them to the analytics tier (queryable in KQL).

---

## Step 5 — Explore the Results

After running the notebook, review the visualisations:

- **Beaconing scatter:** look for dots in the bottom-left (low jitter + short intervals) — these are the strongest C2 candidates.
- **Exfiltration scatter:** dots in the top-right (high MB + high send/receive ratio) indicate potential data theft.
- **Attack timeline:** correlate threat events and blocked traffic with the kill chain — do you see reconnaissance → exploitation → C2 → exfiltration?
- **Threat breakdown:** check whether threats are being **blocked** or just **alerted** — are your firewall policies effective?

---

## Step 6 — Clean Up (Optional)

The notebook saves results to `PaloAlto_Investigation_SPRK` in the data lake. If you want to remove this table after the exercise:

```python
data_provider.delete_table("PaloAlto_Investigation_SPRK", "System tables")
print("🗑️ Table deleted")
```

> **Note:** Custom tables in the analytics tier (`_SPRK_CL`) cannot be deleted from notebooks — use Log Analytics in the Azure portal instead.

---

## Key Takeaways

- **Notebooks = interactive investigation** — combine code, charts, and narrative for deep-dive hunting that goes beyond what portal queries can do.
- **Spark at scale** — PySpark processes data across distributed compute, handling the volume of a real SOC environment.
- **Reusable templates** — swap `CommonSecurityLog` for any other table (CrowdStrike, Okta, AWS) to investigate different data sources with the same patterns.
- **Write-back** — persist investigation results to the data lake for dashboards, sharing, and follow-up queries.
- **Scheduling** — notebooks can be scheduled as [recurring jobs](https://learn.microsoft.com/en-us/azure/sentinel/datalake/notebook-jobs) for automated analysis.

---

## References

- [Run notebooks on the Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/notebooks) — full setup and usage guide
- [Sample notebooks for Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/notebook-examples) — additional examples
- [Microsoft Sentinel Provider class reference](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-provider-class-reference) — complete API docs
- [Create and manage notebook jobs](https://learn.microsoft.com/en-us/azure/sentinel/datalake/notebook-jobs) — scheduling and automation
