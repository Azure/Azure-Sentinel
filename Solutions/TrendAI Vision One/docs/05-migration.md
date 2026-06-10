# Migrating from the old connector

If you already pull Trend Vision One data into Sentinel using the **old Azure Function based connector**, this guide moves you onto the new **codeless** connector — safely, in plain steps, without losing your historical data or breaking your existing queries.

Read the whole page once before you start. It's written to remove every "wait, what about…?" before you touch anything.

---

## Are you actually on the old connector? (How to tell)

You're on the old one if **any** of these is true in your Azure environment:

- There's an **Azure Function App** with a name like `TrendMicroXDR…` (Sentinel → Data connectors, or just search "Function App" in the portal).
- You see the data connector titled simply **"Trend Vision One"** (connector id `TrendMicroXDR`) — *not* "Trend Vision One - Workbench Alerts" / "- OAT".
- Your resource group has a **Storage Account** + **App Service Plan** that exist only to run that function.

If none of that exists and you've never deployed a Trend connector before, you don't need this page — go straight to [Deployment](03-deployment.md).

---

## The big picture (why this is low-risk)

Here's the single most reassuring fact:

> **The old connector and the new connector write to the *same tables*, with the *same column names*.**

| | Old (Azure Function) | New (Codeless) |
|---|----------------------|----------------|
| Workbench table | `TrendMicro_XDR_WORKBENCH_CL` | `TrendMicro_XDR_WORKBENCH_CL` ✅ same |
| OAT table | `TrendMicro_XDR_OAT_CL` | `TrendMicro_XDR_OAT_CL` ✅ same |
| Column names | `detail_*_s`, `endpoint_ips_s`, `severity_s`, … | **deliberately identical** ✅ |

The new connector was **purpose-built to be drop-in compatible**: the OAT connector preserves the exact legacy column shapes (`detail_*_s` prefix, `endpoint_ips_s` / `endpoint_name_s` / `endpoint_guid_g` expansion, lowercase `xdrCustomerId_g`) and even keeps the full raw payload in a `RawData` column as a fallback. **Both** connectors ship a **universal parser** — `TrendMicroWorkbench_Complete()` and `TrendMicroOAT_Complete()` — that reads old and new rows alike and returns one stable schema, so queries that call the parser span your entire history seamlessly.

**What this means for you:**

- ✅ Your **historical data stays** — same table, nothing deleted.
- ✅ Your **existing KQL queries keep working** — same column names.
- ✅ Your **analytic rules and workbooks keep working** — they reference the same columns.
- ✅ New data simply continues landing in the same table, just delivered by a different (better) courier.

So the migration is really just: **stand up the new courier, confirm it's delivering, then retire the old courier.** The data store underneath never changes.

---

## What's genuinely different

Three real differences to be aware of before you start.

### 1. The infrastructure disappears

The old connector ran a whole little app stack. The new one runs inside Sentinel. After migrating, you get to **delete** all of this:

| Old resource | Why it existed | After migration |
|--------------|----------------|-----------------|
| Azure Function App | Ran the Python poller | ❌ Delete |
| App Service Plan | Hosting/compute for the function | ❌ Delete |
| Storage Account | Function state / checkpoints | ❌ Delete (if dedicated to it) |
| Application Insights | Function logging | ❌ Delete (if dedicated to it) |

Result: less to patch, less to pay for, less to secure.

### 2. What's different about secrets

The old connector needed **two** secrets in the function's app settings:

- your Trend Vision One **API token**, and
- your **Log Analytics workspace key** (a powerful shared secret that can write anything into your workspace).

The new connector needs **only the Trend API token**. The workspace key is gone entirely — the codeless platform handles ingestion through the DCR without a shared key. That's one fewer high-value secret to store, rotate, and worry about.

### 3. Region codes changed format

The old function used lowercase region codes; the new connector uses the official short codes:

| Old function region code | New connector region value |
|--------------------------|----------------------------|
| `us` | `US` |
| `eu` | `UK` *(EU is served by the UK endpoint)* |
| `sg` | `SG` |
| `jp` | `JP` |
| — | `CA` *(new)* |
| `au`, `in` | ⚠️ **not currently offered** by this connector |

> ⚠️ **If your old connector used `au` or `in`:** the new connector currently supports US, UK, SG, CA, JP only. **Stop and contact Trend Micro support** before migrating, so you don't end up unable to point at your region. Don't decommission the old connector until you've confirmed coverage.

### Also worth knowing: the RCA tables

The old connector could also populate two root-cause-analysis tables: `TrendMicro_XDR_RCA_Task_CL` and `TrendMicro_XDR_RCA_Result_CL`. The new Workbench/OAT connectors **do not** produce these. If you actively use RCA data, note that:

- Your historical RCA data stays (tables aren't deleted).
- No *new* RCA rows will arrive after you retire the old connector.
- If RCA is important to your workflow, raise it with Trend support before fully decommissioning.

---

## The migration plan (overview)

```
1. Prep        →  2. Deploy new (parallel)  →  3. Verify  →  4. Stop the old  →  5. Decommission  →  6. Cleanup
   gather info     new connector alongside       data is       disable old        delete old           remove old
                   the old one                   flowing       poller/rule        function stack       analytic rule
```

The key idea: **run both in parallel just long enough to confirm the new one works, then cut over.** We never delete first.

> ⏱️ **Plan for a short overlap window** (an hour is plenty). During overlap both connectors write to the same table — see [avoiding duplicates](#avoid-double-incidents) for how to handle that cleanly.

---

## Step-by-step

### Step 1 — Prep: gather your facts

Before changing anything, write down:

- [ ] Your **Trend region** (translate the old code using the [table above](#3-region-codes-changed-format)).
- [ ] Which connectors you need: **Workbench, OAT, or both**.
- [ ] Whether the old connector used `au`/`in` (if so, [stop and contact support](#3-region-codes-changed-format)).
- [ ] Whether you rely on the **RCA tables** (if so, flag with support).
- [ ] A **fresh Trend Vision One API token** with the **SIEM** role ([how-to](02-permissions.md#how-to-create-the-token-step-by-step)). Make a *new* one rather than reusing the function's — you'll revoke the old one at the end.
- [ ] Note your current old-connector analytic rules and which are **enabled**, so you can recreate/replace them.

### Step 2 — Deploy the new connector alongside the old one

Deploy the new connector following the [deployment guide](03-deployment.md). **Leave the old connector running for now.**

Because both write to the same table, the new connector will start adding rows next to the old connector's rows — that's expected and fine for a short window.

> 💡 You can deploy **without** the API token first (infra only), then connect when you're ready to start the overlap window. That gives you control over exactly when dual-ingestion begins.

### Step 3 — Verify the new connector is delivering

Confirm new data is arriving via the new path. Run (Workbench shown; adjust table for OAT):

```kql
TrendMicro_XDR_WORKBENCH_CL
| where TimeGenerated > ago(30m)
| summarize Rows = count(), Latest = max(TimeGenerated)
```

You want a recent `Latest` timestamp and a non-zero count. Also check **Sentinel → Data connectors →** *"Trend Vision One - Workbench Alerts"* shows a healthy *"Last data received."*

Spot-check that your existing queries still return what you expect — they should, since columns are unchanged:

```kql
TrendMicroWorkbench_Complete()
| where TimeGenerated > ago(30m)
| project TimeGenerated, severity_s, FileName_s, FileHashValue_s, HostHostName_s
| take 20
```

✅ Only proceed once you're satisfied the new connector is healthy.

### Step 4 — Stop the old connector (but don't delete yet)

Now turn **off** the old courier so only the new one is ingesting:

1. Find the old **Function App** (e.g. `TrendMicroXDR…`).
2. **Stop** it: Function App → **Overview → Stop**. (Stopping, not deleting, lets you roll back instantly if needed.)
3. If the old connector installed its own **analytic rule(s)**, **disable** them now so you don't get duplicate incidents (see below).

> 🔁 **Rollback if something's wrong:** if the new connector misbehaves, just **Start** the old Function App again. Because nothing was deleted, you're instantly back to the old path. This is why we stop before we delete.

### Step 5 — Avoid double incidents

<a id="avoid-double-incidents"></a>

During the brief overlap, both connectors wrote rows to the same table. Two things to handle:

- **Duplicate rows for the overlap window.** Harmless for most uses; they're just two copies of the same finding for that hour. If you care, filter them in queries, or simply ignore — they age out with your retention.
- **Duplicate incidents.** If *both* the old and new analytic rules are enabled, each finding could create two incidents. Fix: keep **only one** rule enabled. Recommended: enable the **new** Workbench rule ([usage guide](04-using-the-connector.md#step-4-turn-on-the-analytic-rule-workbench)) and **disable the old** one in Step 4.

### Step 6 — Decommission the old infrastructure

Once the new connector has run cleanly on its own for a comfortable period (a day or two is a safe default), delete the old stack. Delete only resources that exist **solely** for the old connector:

1. Delete the **Function App**.
2. Delete its **App Service Plan**.
3. Delete its dedicated **Storage Account** and **Application Insights** (only if nothing else uses them).
4. **Remove the old data connector** entry: Sentinel → Data connectors → "Trend Vision One" (`TrendMicroXDR`) → disconnect/remove.
5. **Delete the old analytic rule(s)** you disabled in Step 4 (if you've replaced them with the new ones).
6. **Revoke the old API token** in Trend Vision One (the one the function used). The new connector has its own token, so the old one is now dead weight — revoking it shrinks your exposure.

> 🧹 **Do not delete the tables** (`TrendMicro_XDR_*_CL`). The new connector uses them and they hold your history.

### Step 7 — Final verification

- [ ] New connector shows recent *"Last data received."*
- [ ] Your dashboards/queries still populate.
- [ ] Exactly **one** analytic rule per data type is enabled.
- [ ] Old Function App and its stack are gone.
- [ ] Old API token revoked.
- [ ] No unexpected Azure charges from leftover old resources.

🎉 You're migrated.

---

## FAQ

**Will I lose my historical data?**
No. Same tables, never deleted. Old rows stay queryable forever (subject to your normal retention settings).

**Will my existing KQL / rules / workbooks break?**
No — column names are intentionally identical. The Workbench parser even handles old *and* new rows automatically.

**Can I run both connectors permanently?**
You *can*, but you shouldn't — you'd pay to ingest everything twice and risk duplicate incidents. The whole point is to retire the old one.

**What if I'm mid-migration and need to roll back?**
Before Step 6, rollback is trivial: **Start** the old Function App, disable the new poller. Nothing's been deleted.

**My region was `au` or `in`.**
The new connector doesn't currently offer those. [Contact Trend support](#3-region-codes-changed-format) before decommissioning the old connector.

**I rely on the RCA tables.**
The new connector doesn't produce them. Your historical RCA data stays, but no new RCA rows arrive after cutover. Flag this with Trend support before fully decommissioning.

---

Stuck during migration? → [Troubleshooting](06-troubleshooting.md)
