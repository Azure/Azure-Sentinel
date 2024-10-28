# Google Threat Intelligence Playbooks

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/GoogleThreatIntelligence.svg" alt="Google Threat Intelligence" style="width:150px; height:150px"/>

## Playbooks

Google Threat Intelligence solution provides the following playbooks.

### Google Threat Intelligence Enrichment

* **Entity trigger**: Add a comment to the the incident associated with the corresponding entity.
  * **Domain** - GoogleThreatIntelligence-IOCEnrichmentDomain
  * **URL** - GoogleThreatIntelligence-IOCEnrichmentURL
  * **IP** - GoogleThreatIntelligence-IOCEnrichmentIP
  * **Filehash** - GoogleThreatIntelligence-IOCEnrichmentFile

* **Alert trigger - GoogleThreatIntelligence-IOCEnrichmentAlert:** Iterate over all entities associated with the alert, adding enrichment comments to the associated incident.
  
* **Incident trigger - GoogleThreatIntelligence-IOCEnrichmentIncident**: Iterate over all entities associated with the incident, adding enrichment comments to the incident.


## Automate

Automation process could be found [here](https://learn.microsoft.com/en-us/azure/sentinel/automation/run-playbooks?tabs=after-onboarding%2Cincidents%2Cazure%2Cincident-details-new)