# Permissions you need (and why)

This page lists **every permission** required to deploy and run the connector — on both the Azure side and the Trend Vision One side — and explains *why* each one is needed.

Why spell out the "why"? Because in most organizations you don't grant your own access — you ask an admin. Walking in with *"I need Contributor on the resource group because the deploy creates a DCR and a custom table, and the connector needs to write to the workspace"* gets you unblocked far faster than *"the docs said I need Contributor."*

> 🧭 **Golden rule:** ask for the **least** access that gets the job done, on the **smallest** scope (a single resource group, not the whole subscription). Every section below tells you the smallest scope that works.

---

## TL;DR — the shortest path

If you just want the request to send to your admin, here it is:

**On the Azure side**

| You need | On what scope | So you can… |
|----------|---------------|-------------|
| **Contributor** (or the granular set below) | The **resource group** you'll deploy into | Create the table, DCE, DCR, connector, etc. |
| **Microsoft Sentinel Contributor** | The Sentinel **workspace** | Create the connector and (optionally) the analytic rule |

**On the Trend Vision One side**

| You need | Where | So you can… |
|----------|-------|-------------|
| An **API key** with the **SIEM** role (Workbench role also works for Workbench) | Trend Vision One Console → API Keys | Let the connector read your findings |

That's the whole story. The rest of this page explains each item and offers a more granular ("least-privilege") alternative for security-conscious environments.

---

## Part 1 — Azure permissions (to *deploy* the connector)

Deploying creates Azure resources, so the person clicking "Deploy to Azure" needs permission to create those resources **in the target resource group**.

### Option A — the simple one (most teams use this)

**Role:** `Contributor`
**Scope:** the resource group you deploy into (ideally a dedicated one, e.g. `rg-sentinel-trend`).

Contributor lets you create and manage any resource in that resource group, but **not** hand out access to others (that's `Owner`). For a deployment, Contributor is enough and is the recommended default.

> Why not subscription-level Owner? Because you don't need it. Scoping to one resource group means a mistake (or a compromised account) can't touch the rest of your cloud.

### Option B — least privilege (for locked-down environments)

If your security team won't grant blanket Contributor, here are the *specific* resource providers the deployment touches and why. Grant Contributor-equivalent rights on **just these**, scoped to the resource group:

| Azure resource provider | What gets created | Why it's needed |
|-------------------------|-------------------|-----------------|
| `Microsoft.OperationalInsights/workspaces` | Custom table, saved function (parser) | The data has to land *somewhere*, and the parser is a saved query in the workspace |
| `Microsoft.Insights/dataCollectionEndpoints` | The DCE ("mailbox") | The fixed address data is delivered to |
| `Microsoft.Insights/dataCollectionRules` | The DCR ("sorter") | Reshapes/filters data before storage |
| `Microsoft.SecurityInsights` | Connector definition, analytic rule | Registers the connector in Sentinel and (optionally) the alert rule |
| `Microsoft.OperationsManagement/solutions` | The Sentinel solution | Ensures Sentinel is enabled on the workspace |
| `Microsoft.Insights/workbooks` | The dashboard (Workbench only) | The monitoring workbook |

The two built-in roles that together cover almost all of the above:

- **Microsoft Sentinel Contributor** — for the connector definition, analytic rule, and Sentinel itself.
- **Monitoring Contributor** — for the DCE and DCR.

> ℹ️ The Azure Portal's deployment screen also shows a permissions note saying **"Read and Write permissions are required"** on the workspace. That's this same requirement, surfaced at click-time.

### Do I need an existing Sentinel workspace?

You need a **Log Analytics workspace**. The deployment will enable Microsoft Sentinel on it if it isn't already (that's the `sentinel-solution` step). If you don't have a workspace at all, create one first (or ask your admin to) — that's a one-time, separate task.

---

## Part 2 — Azure permissions (for the connector to *run*)

Once deployed, the connector needs to **write** the data it pulls into the custom table. With the codeless platform this is handled by the DCR and the connector's managed plumbing — **you do not provide any Azure key or secret for this.**

This is a real improvement over the old Function App connector, which needed your **Log Analytics workspace key** (a powerful shared secret) stored in the function's settings. The codeless connector removes that secret entirely. See the [Migration guide](05-migration.md#whats-different-about-secrets) for why that matters.

The connector definition itself declares the workspace permissions it uses:

> **Read and Write permissions are required** on the `Microsoft.OperationalInsights/workspaces` (Workspace) scope — read, write, and delete.

You don't grant these by hand; they're part of installing the connector into the workspace.

---

## Part 3 — Trend Vision One permissions (the API token)

The connector logs into Trend Vision One the way an app would — with an **API key** (also called an API token). This is the only secret *you* supply.

### What role does the token need?

| Connector | Required role on the API key |
|-----------|------------------------------|
| Workbench | **SIEM** *or* **Workbench** |
| OAT | **SIEM** |

When in doubt, use **SIEM** — it covers both connectors and is the intended role for feeding a SIEM like Sentinel.

### Why does it need this role and not more?

The **SIEM** role is **read-only access to the findings feed**. It can pull alerts and detections; it **cannot** change anything in Trend Vision One. That's exactly what you want for a one-way data copy — if the token ever leaked, the worst an attacker could do is *read* your alerts, not disable your protection.

> 🔐 **Least privilege again:** don't reuse a full-admin API key here. Make a dedicated key with only the SIEM role, used only by this connector. If it's ever compromised, you revoke that one key and nothing else breaks.

### How to create the token (step by step)

1. Log in to the **Trend Vision One Console**.
2. Go to **Administration → API Keys**. *(On some tenants this is under "API access management.")*
3. Click **Add API Key** / **Generate New API Key**.
4. Give it a clear name, e.g. `microsoft-sentinel-connector`, so future-you knows what it's for.
5. Assign the role: **SIEM** (or **Workbench** for the Workbench connector).
6. Save, then **copy the token immediately** — you usually can't see it again later.
7. Store it somewhere safe (a password manager / Azure Key Vault) until you paste it into the connector.

> 📍 **Region matters.** Your token only works against *your* Trend Vision One region's API endpoint (US, UK, SG, CA, or JP). You'll pick the matching region during deployment. See [Using the connector → Regions](04-using-the-connector.md#regions-and-api-endpoints).

### The `Bearer ` prefix gotcha

This is the #1 cause of "connection failed." Two places ask for the token and they want it **differently**:

| Where you enter it | Include `Bearer ` prefix? | Example |
|--------------------|:------------------------:|---------|
| **Deploy-time field** in the Azure Portal form ("Trend Vision One API Token") | ❌ **No** — paste the raw token only | `eyJhbGciOi...` |
| **Connector page** in Sentinel ("API Token") after deployment | ✅ **Yes** — include it | `Bearer eyJhbGciOi...` |

If a connection fails, this mismatch is the first thing to check.

---

## Who grants what — a quick map

| You need… | Ask… |
|-----------|------|
| Contributor on the resource group | Your **Azure subscription admin** or whoever owns the resource group |
| Microsoft Sentinel Contributor | Your **SOC / security platform team** (they usually own Sentinel) |
| A Trend Vision One SIEM API key | Your **Trend Vision One administrator** |

If those are three different people, send all three requests at once — they don't depend on each other.

---

## Permissions checklist

Before you start the [deployment](03-deployment.md), confirm:

- [ ] I can deploy into a resource group (Contributor, or the granular providers above)
- [ ] Microsoft Sentinel is (or will be) enabled on the target workspace
- [ ] I have **Microsoft Sentinel Contributor** on that workspace
- [ ] I created a dedicated Trend Vision One API key with the **SIEM** role
- [ ] I saved the token somewhere safe
- [ ] I know which **region** my Trend Vision One tenant is in

All checked? → [On to deployment.](03-deployment.md)
