# Spur.us
link: [https://spur.us](https://spur.us/) <br/>

## Spur.us database
[Spur.us](https://spur.us/) is a database that helps you identify VPN/proxy/TOR-related IP addresses on the internet and provides you additional information about these IPs. <br/>
During my recent investigations, the tools and services I used were not reliable enough, they misidentified a bunch of VPN-related IP addresses. While searching for a better service I stumbled into Spur. This service gave me the most precise and up-to-date results, so I decided to automate my lookups to be able to quickly identify IPs involved in VPN communications.

This repo contains the Spur.us-based IP lookup logic implemented as an **Azure Playbook**.<br/>

## Design considerations

The connections in the Playbook are implemented by using Managed Identities. This connection type is still in 'Preview' but it is a convenient way to handle connections, so I decided to go this way. I'm going to explain later on how to change the connection type if you want to use something else.

The Playbook comes in two flavors. There is a Playbook with an 'Incident' trigger and one with 'Alert' trigger.

Azure limits the comment size in 3000 characters, which is a pretty heavy limitation when we are talking about HTML code. Because of this, each IP in an incident creates a separate comment. Also, one of the fields (SimilarIPs) is going to be shortened if it is too long. If any of the other fields are two long, then the comment function won't be successful, however, based on my experience, this won't be a problem.

Spur provides a lot of information, but I'm only using a small subset of these fields. The following fields are used (the explanations are copied from the spur API documentation):
- **anonymous**: Whether this IP address has provided some type of anonymity service. This could include a VPN service or a residential proxy.
- **GeoLite**: GeoLite location information.
- **ProxiedTraffic**: Proxy services that are actively routing traffic through this IP address.
- **VPNOperators**: The VPNs that operate this IP address.
- **DeviceBehaviors**: Behaviors associated with devices on this IP address
- **WiFi**: Information about WiFi associated with this IP address
- **SimilarIPs**: These are IP addresses that have very similar attributes or behavior. These IPs are often used by the same devices.


The Playbook modifies an Incident in two ways:
1. A comment is added to the incident about the collected information per entity (IP).
1. A tag (label) is added to the incident in the following format per entity (IP): Spur:{IP}=[Clean|Anonymizer]. This format mimics the taxonomies in TheHive. At this point in Azure Sentinel it is not possible to tag individual entities, all of the tags are related to the incident itself, so I decided to use the following tagging format in my Playbooks (until a better option): {PlaybookName}:{Entity}={Conclusion}. See an example below:


## Installation and Configuration

**Deployment**:
1. Open the template deployment portal in Azure (https://portal.azure.com/#create/Microsoft.Template).
1. Click on the "Build your own template in the editor" button.
1. Copy the chosen template (azuredeploy.json) into the text field.
1. Click save and provide the requested information:
	1. Subscription
	1. Resource group
	1. Region
	1. Playbook Name
	1. Key Vault Name: The Key Vault in which the API key is stored.
	1. Secret Name: Name of the secret that stores the Spur API key.
1. Deploy the code.

**Configuration**:
1. After deployment the managed identity is turned on for the resource (Playbook) and the API Connections are created, but you have to give permissions to the Managed Identity.
1. Open the Playbook.
1. Click on the Identity button in the Settings section.
1. Click on the Azure Role Assignment button.
1. Provide the following roles to your Managed Identity:
	Key Vault Secret User to your key vault (only works if your Key Vault is configured to use Azure role-based access control)
	Azure Sentinel Responder
1. Wait a few minutes for the roles to propagate.
1. Everything should work fine now.

**Created Resources:**

1. {Plabook Name}: Logic App
1. sen-{Playbook Name}: API Connection - to connect to Sentinel
1. kva-{Playbook Name}: API Connection - to connect to the KeyVault

If you don't want to use Managed Identity, then after deployment you can modify every block with connection requirement to use another method. <br/>
The API connections are deployed to be used by Managed Identities, so if you don't utilize Managed Identity you can remove these API connections from the resource group. Also, if you don't want to use KeyVault, you can delete the second API connection <br/>

**Deploy with Alert trigger:**<br/>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSpur-Enrichment%2FAlertTrigger%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSpur-Enrichment%2FAlertTrigger%2Fazuredeploy.json)



**Deploy with Incident trigger:**<br/>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSpur-Enrichment%2FIncidentTrigger%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSpur-Enrichment%2FIncidentTrigger%2Fazuredeploy.json)