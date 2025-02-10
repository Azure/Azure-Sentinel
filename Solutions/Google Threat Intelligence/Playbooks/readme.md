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

## Deployment

### Custom Connector

#### Pre-requisites

To use this integration, you need:

A GTI account: Follow the steps on https://developers.virustotal.com/v3.0/reference#getting-started to get your API key.

#### Deploy

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnectors%2FGTICustomConnector%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnectors%2FGTICustomConnector%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

Once you have deployed your Google Threat Intelligence Custom Connector, you can configure your API Connection with the API key previously mentioned.

### Playbooks

#### Pre-requisites

To use this integration, you need:

A GTI account: Follow the steps on https://developers.virustotal.com/v3.0/reference#getting-started to get your API key.

To install and authorize playbooks in Microsoft Sentinel, you need specific permissions on the resource group. While the **Microsoft Sentinel Contributor** and **Logic App Contributor** roles grant access to Sentinel features, they don't provide the necessary resource group level permissions.

For playbook authorization, Microsoft recommends using managed identity. This method requires the user performing the installation to have either the Owner or Role Based Access Control Administrator role on the resource group. This approach enhances security by allowing playbooks to run without relying on user credentials.

After installing a playbook or logic app in Microsoft Sentinel, you'll need to authorize its connectors. Here's how:

1. Open all nodes: Open the logic app and expand all the collapsed nodes to see the full workflow.
2. Look for warning signs: Identify any blocks with a sign. These indicate connectors that require authorization.
3. Setup connections: Open each warning block and follow the prompts to authorize the connection.

This ensures that your playbook has all the necessary permissions to access data and perform actions.

#### Deploy

To install the Google Threat Intelligence playbooks, we recommend using the Content Hub and the templates provided.

## Automate

Automation process could be found [here](https://learn.microsoft.com/en-us/azure/sentinel/automation/run-playbooks?tabs=after-onboarding%2Cincidents%2Cazure%2Cincident-details-new)