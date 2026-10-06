# WhoisFreaks Microsoft Sentinel Solution

This solution ingests WhoisFreaks threat intelligence and newly registered domain (NRD) feeds using the Microsoft Sentinel Codeless Connector Framework (CCF). Threat API fields are retained in `WhoisFreaksThreat_CL` (including `threat_type`); WHOIS NRD API fields are retained in `WhoisFreaksNRD_CL`; headerless no-WHOIS rows are written to `WhoisFreaksNRDNoWhois_CL` with the payload column `domain_name`. Both NRD tables include an `nrd_type` column (`gtld` or `cctld`) set by the DCR transform so gTLD and ccTLD rows can be distinguished without parsing the domain. `TimeGenerated` is the Log Analytics system ingestion timestamp. The connector UI lets users select feeds enabled by their subscription. The solution also includes four scheduled analytic rules.

## Prerequisites

- Azure CLI logged in to the target subscription (`az login`).
- A staging Microsoft Sentinel workspace for integration tests. Validate production changes in staging before deploying them to production.
- A WhoisFreaks API key entitled to each feed you enable.
- The workspace resource group, workspace name, workspace region, DCE URL, and DCR immutable ID. The values in `Infra/connect-pollers.json` are examples/defaults; verify them against the target environment.
- `jq`, `unzip`, and `zip` for local checks and package inspection.

Do not commit API keys, generated parameter files containing secrets, or deployment outputs with secrets. Supply the key through a protected shell variable or a secret manager.

## Pre-PR Validation

Run from this solution directory. These checks verify JSON syntax, require all seven nested feed requests to use a page size of 10000, and verify the package contains a valid template:

```bash
set -euo pipefail

jq empty Infra/connect-pollers.json
jq empty Package/mainTemplate.json
jq empty 'Data Connectors/WhoisFreaks_CCF/WhoisFreaks_PollingConfig.json'

for file in Infra/connect-pollers.json Package/mainTemplate.json 'Data Connectors/WhoisFreaks_CCF/WhoisFreaks_PollingConfig.json'; do
  test "$(jq '[.. | objects | .pageSize? // empty] | length' "$file")" -eq 7
  jq -e '[.. | objects | .pageSize? // empty] | all(. == 10000)' "$file" >/dev/null
done

unzip -p Package/3.0.0.zip mainTemplate.json | jq empty
unzip -p Package/3.0.0.zip mainTemplate.json | jq -e '[.. | objects | .pageSize? // empty] | length == 7 and all(. == 10000)' >/dev/null
```

If you change templates, rebuild `Package/3.0.0.zip` from the package contents after validating the source files. Confirm that the package contains the same `mainTemplate.json` you intend to release.

Update the existing package archive from its source files with:

```bash
(cd Package && zip -u 3.0.0.zip mainTemplate.json createUiDefinition.json)
unzip -t Package/3.0.0.zip
```

Set deployment values for a staging workspace. The API key is read without echoing it or placing it literally in shell history:

```bash
export RESOURCE_GROUP='your-staging-resource-group'
export WORKSPACE='your-staging-workspace'
export LOCATION='your-workspace-region'
export DCE_URL='https://your-dce.ingest.monitor.azure.com'
export DCR_IMMUTABLE_ID='dcr-your-immutable-id'
read -rsp 'WhoisFreaks API key: ' WHOISFREAKS_API_KEY; printf '\n'
```

Validate and preview the poller deployment. These commands check the ARM deployment and planned resource changes; they do not prove that every external feed is accessible or that the full poll succeeds:

```bash
az deployment group validate \
  --resource-group "$RESOURCE_GROUP" \
  --template-file Infra/connect-pollers.json \
  --parameters workspace="$WORKSPACE" location="$LOCATION" \
    dataCollectionEndpoint="$DCE_URL" \
    dataCollectionRuleImmutableId="$DCR_IMMUTABLE_ID" \
    apiKey="$WHOISFREAKS_API_KEY"

az deployment group what-if \
  --resource-group "$RESOURCE_GROUP" \
  --template-file Infra/connect-pollers.json \
  --parameters workspace="$WORKSPACE" location="$LOCATION" \
    dataCollectionEndpoint="$DCE_URL" \
    dataCollectionRuleImmutableId="$DCR_IMMUTABLE_ID" \
    apiKey="$WHOISFREAKS_API_KEY"
```

The Sentinel connector UI offers a multi-select feed list, with all seven selected by default. Select only feeds included in the API subscription. `Infra/connect-pollers.json` is a direct-deployment/test template and exposes one boolean per feed. A real deployment performs CCF connectivity checks and can start ingestion, so test in staging first:

```bash
az deployment group create \
  --name "whoisfreaks-smoke-$(date -u +%Y%m%dT%H%M%SZ)" \
  --resource-group "$RESOURCE_GROUP" \
  --template-file Infra/connect-pollers.json \
  --parameters workspace="$WORKSPACE" location="$LOCATION" \
    dataCollectionEndpoint="$DCE_URL" \
    dataCollectionRuleImmutableId="$DCR_IMMUTABLE_ID" \
    apiKey="$WHOISFREAKS_API_KEY" \
    enableThreatMalware=true enableThreatPhishing=false enableThreatSpam=false \
    enableNrdGtldWhois=false enableNrdGtldNoWhois=false \
    enableNrdCctldWhois=false enableNrdCctldNoWhois=false
```

After a successful smoke test, deploy the other entitled feeds in staging, check ingestion and rule behavior, then repeat the reviewed deployment in production. Use the DCE and DCR values belonging to the same target workspace.

## Analytic Rule Testing

The four templates are in `Analytic Rules/`. Before deploying a rule:

1. Open Microsoft Sentinel **Logs** in the staging workspace.
2. Copy the `query` value from the rule JSON and run it as KQL. The query must compile; zero matches is valid when the data does not meet the detection condition.
3. Check whether the returned columns support the rule's entity mappings and intended alert details.
4. Validate the ARM template and deploy it to staging. Confirm the rule exists, is enabled as intended, and has the expected frequency, period, severity, tactics, and techniques.
5. Generate a controlled matching event in staging only if you need to test alert creation end to end. Do not create artificial production incidents just to test a rule.

Example validation for all rule templates:

```bash
for file in 'Analytic Rules'/*.json; do
  jq empty "$file"
  az deployment group validate \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$file" \
    --parameters workspace="$WORKSPACE" workspace-location="$LOCATION"
done
```

After validation, deploy the rules to the staging workspace:

```bash
for file in 'Analytic Rules'/*.json; do
  rule_name=$(basename "$file" .json)
  az deployment group create \
    --name "${rule_name}-$(date -u +%Y%m%dT%H%M%SZ)" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$file" \
    --parameters workspace="$WORKSPACE" workspace-location="$LOCATION"
done
```

For each KQL query, use the Logs experience to validate and inspect results before deploying. ARM validation checks the resource template, not KQL execution or alert generation.

## Data Verification

Check recent threat arrivals:

```kusto
WhoisFreaksThreat_CL
| where TimeGenerated > ago(7d)
| summarize Rows=count(), Latest=max(TimeGenerated) by threat_type
| order by threat_type asc
```

Check recent WHOIS NRD arrivals:

```kusto
WhoisFreaksNRD_CL
| where TimeGenerated > ago(7d)
| summarize Rows=count(), Latest=max(TimeGenerated) by nrd_type
| order by nrd_type asc
```

Check no-WHOIS NRD arrivals separately:

```kusto
WhoisFreaksNRDNoWhois_CL
| where TimeGenerated > ago(7d)
| summarize Rows=count(), EmptyDomainRows=countif(isempty(domain_name)), Latest=max(TimeGenerated) by nrd_type
| order by nrd_type asc
```

The WHOIS NRD table contains the API's WHOIS fields using their original lowercase names, plus `nrd_type` (`gtld` or `cctld`). The no-WHOIS table has `domain_name`, `nrd_type`, and the Log Analytics system timestamp `TimeGenerated`.

`TimeGenerated` is assigned by the DCR transformation at ingestion time. It indicates when Sentinel processed the row, not the WhoisFreaks domain creation time or the Azure deployment time.

To inspect repeated WHOIS NRD domain entries, choose a time range. Repeated rows can be expected when a feed is polled again or the same domain occurs in multiple snapshots; they are not automatically ingestion defects:

```kusto
WhoisFreaksNRD_CL
| where TimeGenerated > ago(7d)
| summarize Copies=count(), FirstIngested=min(TimeGenerated), LastIngested=max(TimeGenerated)
    by domain_name
| where Copies > 1
| order by Copies desc
```

For no-WHOIS NRD duplicates, use its separate table:

```kusto
WhoisFreaksNRDNoWhois_CL
| where TimeGenerated > ago(7d)
| summarize Copies=count(), FirstIngested=min(TimeGenerated), LastIngested=max(TimeGenerated)
    by domain_name
| where Copies > 1
| order by Copies desc
```

For threat events, inspect repeats using the relevant indicator fields:

```kusto
WhoisFreaksThreat_CL
| where TimeGenerated > ago(7d)
| summarize Copies=count(), FirstIngested=min(TimeGenerated), LastIngested=max(TimeGenerated)
    by domain, threat_type
| where Copies > 1
| order by Copies desc
```

These queries identify repeated keys, not necessarily erroneous duplicate ingestion. Compare the time range and feed semantics before treating repeats as a defect. For a deduplicated WHOIS NRD view, use the newest ingested row per domain:

```kusto
WhoisFreaksNRD_CL
| summarize arg_max(TimeGenerated, *) by domain_name
```

## Polling, Pages, and Deployment History

All seven feed requests use `pageSize: 10000` with `limit` and offset paging. Each connector first reads its matching `last_update` from the status response, then requests the dated feed: NRD uses `newly.gtld`/`newly.cctld`, and threat feeds use `threat_feed.malware`/`phishing`/`spam`. The status request itself is not paged. CCF advances `offset` for successive pages.

The configured page size in the source does not prove what is currently deployed. Inspect the live connector resources in the target subscription and workspace:

```bash
az rest --method get \
  --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.OperationalInsights/workspaces/$WORKSPACE/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01-preview" \
  --query "value[?kind=='RestApiPoller'].{name:name,properties:properties}" \
  --output json
```

Check each resource's `properties.paging.pageSize`; for NRD, also check `properties.stepCollectorConfigs.*.paging.pageSize`. If the deployed resource still shows an older value, redeploy the intended template and inspect again.

To review retained resource-group deployment records:

```bash
az deployment group list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[].{name:name,state:properties.provisioningState,timestamp:properties.timestamp}" \
  --output table
```

Deployment history is not a reliable count of every CLI attempt if the same deployment name was reused or older history was removed. The Sentinel event tables do not record CCF poll-run IDs, HTTP request counts, offsets, or page sizes. Therefore they cannot establish the exact number of polling iterations or the page size used by each historical request. The current configured page size is 10000 for all feeds; determine past values from retained deployment/resource history or external API/CCF diagnostics if those were enabled and retained.

## Included Analytic Rules

| Rule | Severity | Purpose |
|---|---|---|
| `WhoisFreaks-HighConfidenceThreat` | High | High-confidence threat domains |
| `WhoisFreaks-NRD-Also-Threat` | High | NRD domains also present in threat feeds |
| `WhoisFreaks-ParkedThreatDomain` | Medium | Threat-listed parked domains |
| `WhoisFreaks-FreshNRD-Burst` | Low | High-volume NRD bursts |
