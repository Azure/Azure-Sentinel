# Recorded Future Automated Threat Hunting

Information about Recorded Future Intelligence Solution for Microsoft Sentinel can be found in the main [readme](../readme.md).

## Recorded Future Automated Threat Hunt
Threat hunting is the proactive and iterative process of searching for and detecting cyber threats that have evaded traditional security measures, such as firewalls, antivirus software, and intrusion detection systems. It involves using a combination of manual and automated techniques to identify and investigate potential security breaches and intrusions within an organization's network.

- <a href="https://support.recordedfuture.com/hc/en-us/articles/20849290045203-Automated-Threat-Hunting-with-Recorded-Future" target="_blank">More about Automated threat hunt</a> (requires Recorded Future login)

# Playbooks

## RecordedFuture-ThreatMap-Importer
Type: **Threat Hunt**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires [**/RecordedFuture-CustomConnector**](../Connectors/RecordedFuture-CustomConnector/readme.md) and API keys as described in the [Connector authorization](../readme.md#connector-authorization) section. \
Connectors used: ***RecordedFuture-CustomConnector*** see [Connector authorization](../readme.md#connector-authorization) for guidance.


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ThreatMap-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ThreatMap-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

Import Recorded Future Actor Threat Map data and stores it in a custom table. Display the report in the workbook imported from the Recorded Future Threat Intelligence Solution. The Workbook shows Threat Actors from Recorded Future, their intent towards your company, and their opportunity.

## RecordedFuture-ThreatMapMalware-Importer
Type: **Threat Hunt**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires [**/RecordedFuture-CustomConnector**](../Connectors/RecordedFuture-CustomConnector/readme.md) and API keys as described in the [Connector authorization](../readme.md#connectors-authorization) section.\
Connectors used: ***RecordedFuture-CustomConnector*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ThreatMapMalware-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ThreatMapMalware-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>


Import Recorded Future Malware Threat Map data and stores it in a custom table. Display the report in the workbook imported from the Recorded Future Threat Intelligence Solution. The Workbook shows Malware Threat from Recorded Future, their intent towards your company, and their opportunity.


## Threat Map table schema (V1 → V2)
> [!IMPORTANT]
> **Breaking change in 3.2.22.** The Threat Map playbooks now write through the Logs Ingestion API (DCE/DCR) to the `RecordedFutureThreatMap_V2_CL` and `RecordedFutureThreatMapMalware_V2_CL` tables. The old `RecordedFutureThreatMap_CL` and `RecordedFutureThreatMapMalware_CL` tables do not receive new data.

The row layout is different:

| | V1 (`*_CL`, legacy HTTP Data Collector API) | V2 (`*_V2_CL`, DCE/DCR) |
|---|---|---|
| Rows | One row per threat actor or malware | One row per playbook run |
| Columns | Flattened, typed columns (`id_s`, `name_s`, `intent_d`, `opportunity_d`, `prevalence_d`, `categories_s`, `log_entries_s`, `alias_s`, ...) | `TimeGenerated`, plus `data` (dynamic): an array with every entity on the threat map |

The bundled workbooks already read the V2 layout. To get one row per entity with the same column names as V1, put `mv-expand` on `data` in your own queries, hunting queries and analytic rules.

**Actor Threat Map**
```kusto
RecordedFutureThreatMap_V2_CL
| mv-expand actor = todynamic(data)
| extend id_s = tostring(actor.id),
         name_s = tostring(actor.name),
         intent_d = toreal(actor.intent),
         opportunity_d = toreal(actor.opportunity),
         categories_s = tostring(actor.categories),
         log_entries_s = tostring(actor.log_entries),
         alias_s = tostring(actor.alias)
| project-away data, actor
```

**Malware Threat Map**
```kusto
RecordedFutureThreatMapMalware_V2_CL
| mv-expand malware = todynamic(data)
| extend id_s = tostring(malware.id),
         name_s = tostring(malware.name),
         prevalence_d = toreal(malware.prevalence),
         opportunity_d = toreal(malware.opportunity),
         categories_s = tostring(malware.categories),
         log_entries_s = tostring(malware.log_entries),
         alias_s = tostring(malware.alias)
| project-away data, malware
```

Each run stores a full snapshot of the threat map. To get only the latest snapshot, add `| where TimeGenerated == toscalar(<table> | summarize max(TimeGenerated))` before the `mv-expand`, replacing `<table>` with the table name. Tip: save either query as a [Log Analytics function](https://learn.microsoft.com/azure/azure-monitor/logs/functions) (for example `RecordedFutureThreatMap`) and use that function in place of the table name.

## RecordedFuture-ActorThreatHunt-IndicatorImport
Type: **Threat Hunt**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires [**/RecordedFuture-CustomConnector**](../Connectors/RecordedFuture-CustomConnector/readme.md) and API keys as described in the [Connector authorization](../readme.md#connectors-authorization) section. \
Connectors used: ***RecordedFuture-CustomConnector*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ActorThreatHunt-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-ActorThreatHunt-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

Fetch indicators linked to threat actors from the threat actor map. The logic app will run on a schedule and check threat actor related to the client’s Recorded Future threat map. It is possible to set a risk score threshold, so that if a threat actor score exceeds the score. The logic app will query Recorded Future for all relevant links indicators (IPs, Hashes, Domains, and URLs) tied to threat actors and store them in the ThreatIntelIndicators table.

If recurrence is changed from default (24h), also change `valid_until_delta_hours` to avoid duplicates in ThreatIntelIndicators table leading to multiple incidents created.

After successful installation, automate incidents creation by setup Analytic Rules shipped in the Solution to correlate this data with your infrastructure, described [here](../readme.md#analytic-rules). Automate triage of incidents by install and configure [Recorded Future Enrichment](../Enrichment/readme.md#recordedfuture-ioc_enrichment).

![](Images/2023-10-26-19-50-43.png)


## RecordedFuture-MalwareThreatHunt-IndicatorImport
Type: **Threat Hunt**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires [**/RecordedFuture-CustomConnector**](../Connectors/RecordedFuture-CustomConnector/readme.md) and API keys as described in the [Connector authorization](../readme.md#connectors-authorization) section. \
Connectors used: ***RecordedFuture-CustomConnector*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-MalwareThreatHunt-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FThreatHunting%2FRecordedFuture-MalwareThreatHunt-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

Fetch malware threat information from the malware threat map. The logic app will run on a schedule  to check malware threat data related to the client’s Recorded Future malware threat map. It is possible to set a risk score threshold, so that if a malware score exceeds the score. The logic app will query Recorded Future for all relevant links indicators (IPs, Hashes, Domains, and URLs) tied to the malware and store them in the ThreatIntelIndicators table.

If recurrence is changed from default (24h), also change `valid_until_delta_hours` to avoid duplicates in ThreatIntelIndicators table leading to multiple incidents created.

After successful installation, automate incidents creation by setup Analytic Rules shipped in the Solution to correlate this data with your infrastructure, described [here](../readme.md#analytic-rules). Automate triage of incidents by install and configure [Recorded Future Enrichment](../Enrichment/readme.md#recordedfuture-ioc_enrichment).

## Configure Threat Map Import Playbooks
Malware and actor threat map import playbooks are configured with defaults that will retrieve the maps presented in Recorded Future Portal without any modifications.


<img src="Images/ThreatMapConfig.png" alt="Threat Map Config" width="80%"/>
<br/>
<br/>
<details>
<summary>Expand Advanced parameters</summary>
It's possible to restrict hunts by actor or malware.

![alt text](Images/AdvancedParameters.png)

Find individual Ids the treat map workbook once it setup by open `Open Generic Details`.

![alt text](Images/GenericDetails.png)
</details>

## Configure Threat Indicator Import Playbooks
Malware and actor indicator import playbooks are configured with defaults that will retrive url, ip, domain and hash -indicators linked to entities on the threat map.

Risk scores can be modified to restrict number of indicators returned from the API.

If recurrence is changed from default (24h), also change `valid_until_delta_hours` to avoid duplicates in ThreatIntelIndicators table leading to multiple incidents created.

<img src="Images/ActorIndicators.png" alt="Threat Indicator Import Config" width="80%"/>

<br/>
<br/>
<details>
<summary>Expand Advanced parameters</summary>
It's possible to restrict indicators downloaded by actor or malware. If several downloads are running use the `Threat Hunt description` field to keep them apart.

![alt text](Images/advanceindicatorconfig.png)

Find individual Ids the treat map workbook once it setup by open `Open Generic Details`.

![alt text](Images/GenericDetails.png)
</details>

## Threat hunting for multi-orgs

If your Recorded Future Enterprise is using [multi-org](https://support.recordedfuture.com/hc/articles/4402787600787-Multi-Org-for-Modules), then which threat map you see depends on which API key is used.

- If the API key is tied to one specific organisation, then you will see that organisation's threat map.
- If the API key is tied to multiple organisations (not recommended), then you will see the first threat map available, which could belong to any of your organisations.