# Troubleshooting

Most problems fall into a handful of buckets. Find your symptom below; each fix explains *why* it works so you learn the system, not just the workaround.

> 🩺 **First, the 90% fixes.** Before anything else, check these two — they cause the large majority of issues:
> 1. **Wrong region.** The Trend region you picked must match your tenant. ([Regions](04-using-the-connector.md#regions-and-api-endpoints))
> 2. **The `Bearer ` prefix.** Connector page wants `Bearer <token>`; the deploy-time field wants the raw token with **no** prefix. ([Prefix gotcha](02-permissions.md#the-bearer--prefix-gotcha))

---

## No data after 10 minutes

Symptom: connector deployed and connected, but the verification query returns nothing.

Work through these in order:

1. **Did you actually connect?** If you left the API token blank at deploy time, the poller doesn't exist yet. Go to Sentinel → Data connectors → your connector → **Open connector page** → enter the token (with `Bearer `) → **Connect**.
2. **Right region?** Wrong region authenticates but sees no findings — silent emptiness. Confirm against your Trend Vision One Console URL.
3. **Token role?** The token needs the **SIEM** role (or **Workbench** for the Workbench connector). A token with the wrong role can't read the feed.
4. **Is there anything to pull?** If you set a tight filter (e.g. `(severity ge 'high')`) and there simply are no high-severity items in the window, the table is legitimately empty. Loosen the filter to test.
5. **Give it time.** First data can take **5–10 minutes**. The poll window is a few minutes wide.
6. **Check connector health:** Sentinel → Data connectors → your connector → look at *"Data received"* and *"Last data received."*

```kql
// Quick "is anything landing?" check
TrendMicro_XDR_WORKBENCH_CL   // or TrendMicro_XDR_OAT_CL
| where TimeGenerated > ago(2h)
| summarize Rows = count(), Latest = max(TimeGenerated)
```

---

## "Connection failed" when I click Connect

- **Missing `Bearer ` prefix** on the connector page → add it. This is the most common cause.
- **Expired or revoked token** → generate a fresh one in Trend Vision One and reconnect.
- **Wrong region** → the token can't authenticate against a region it doesn't belong to.
- **Copy/paste whitespace** → re-copy the token; a stray leading/trailing space breaks it.

To replace the token cleanly: **Disconnect**, paste the new `Bearer <token>`, **Connect**. ([Rotating tokens](04-using-the-connector.md#rotating-or-replacing-the-api-token))

---

## Deployment itself failed

- **Permission denied / authorization errors** → you're missing rights on the resource group or workspace. See [Permissions](02-permissions.md). You typically need **Contributor** on the resource group **and** **Microsoft Sentinel Contributor** on the workspace.
- **Workspace dropdown is empty** → the form filters workspaces by the selected **resource group**. Pick the resource group that actually contains your Sentinel workspace.
- **"Resource provider not registered"** → register the providers listed in [permissions](02-permissions.md#option-b--least-privilege-for-locked-down-environments) on the subscription (an admin task), then redeploy.
- **A nested template URL 404s** → the component templates are fetched from GitHub raw URLs at deploy time. If the repo/branch moved, the `baseUrl` in `mainTemplate.json` is stale. (Internal/test deploys use a blob mirror — see [internal notes](internal/test-deploy.md).)

---

## Data is flowing but my IOC columns are empty (Workbench)

The raw table keeps indicators/entities inside nested fields. Use the **parser function**, which flattens them:

```kql
TrendMicroWorkbench_Complete()
| where isnotempty(FileHashValue_s)
| project TimeGenerated, workbenchName_s, FileName_s, FileHashValue_s, IPAddress
```

If the parser function doesn't exist, the Workbench deployment's parser step didn't run — redeploy the Workbench template (it installs `TrendMicroWorkbench_Complete()`).

---

## No incidents are being created (Workbench)

Incidents come from the **analytic rule**, which ships **disabled**. Enable it: Sentinel → Analytics → *"Trend Vision One - Create Incident for Workbench Alerts"* → **Edit → Enable → Save**. ([Details](04-using-the-connector.md#step-4-turn-on-the-analytic-rule-workbench))

OAT ships no rule — you create your own scheduled rule for OAT.

---

## I'm getting duplicate incidents

Usually means **two analytic rules are enabled** for the same data — commonly the old connector's rule plus the new one during a migration. Keep exactly **one** enabled. See [migration → avoid double incidents](05-migration.md#avoid-double-incidents).

---

## My bill went up

- **OAT is high-volume** by design. If you turned it on without a filter, you're ingesting everything. Add a [filter](04-using-the-connector.md#filtering-what-gets-ingested) (`oatFilter`) and/or keep `excludeThirdPartyOat=true`.
- **Running old + new connectors in parallel** ingests data twice. Finish the [migration](05-migration.md) and retire the old one.

---

## Migration-specific issues

See the [migration FAQ](05-migration.md#faq) for: rollback, `au`/`in` regions, RCA tables, and historical-data questions.

---

## Still stuck? Where to get help

- **Trend Vision One API / token / region questions** → [Trend Micro Support](https://www.trendmicro.com/support)
- **Microsoft Sentinel / Azure / DCR questions** → [Microsoft Sentinel docs](https://learn.microsoft.com/azure/sentinel)
- **A bug in these templates or docs** → [open a GitHub issue](https://github.com/trendmicro/trendai-sentinel-ccf-data-connector/issues)

When filing an issue, include: which connector (Workbench/OAT), your region, whether you connected at deploy-time or via the portal, the exact error text, and the output of the "is anything landing?" query above (with sensitive values redacted).
