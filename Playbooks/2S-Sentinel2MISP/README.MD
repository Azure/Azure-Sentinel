# MISP to Sentinel

This is a short introduction to the MISP to Sentinel project. Keep in mind, this is a proof of concept and would require modification for production use. The solution consist of two parts, a forwarder called `MISP-Forwarder` and an orchestrator called `MISP-Orchestrator`. The purpose of having two parts is to allow you to deploy the forwarder to multiple Microsoft Sentinel workspaces to feed more data into MISP. When it comes to the fidelity of the data, for this PoC we only support filenames and hashes.

## Design

The design is pretty straightforward, we filter on malware was prevented (highly likely that it's a known bad entity)

```mermaid
flowchart LR
    A[Microsoft 365 Defender] -->|Malware alert| B[Microsoft Sentinel]
    B --> INC[Incident]
    INC --> |If alert contains 'Malware was prevented'| AR[Automation Rule]
    AR --> PB[MISP-Forwarder]
    PB --> |Send entities, incident URI and id|PB2[MISP-Orchestrator]
    PB2 --> MISP[MISP Server]
```

## Setup

### Deploy MISP Orchestrator

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.storage%2Fstorage-account-create%2Fazuredeploy.json)

1. Deploy the `MISP-Orchestrator` 
2. Fill out the information needed:
    * `MISP Key` (this is the MISP API key)
    * `MISP Uri` (this is the URI for the MISP-server)
    * `MISP Org` (Name of your MISP organization)
3. Update the `Create new event MISP` step with the correct `event_creator_mail` 
    * **NOTE**: This should be the same user that you created the MISP key for and not an admin role
4. Make a note of the `HTTP POST URL` from the 'When a HTTP request is received' step
5. Current setup is fine for testing/development purposes
    * Highly recommend deploying a key vault and use that for authorization in production

### Deploy MISP Forwarder

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.storage%2Fstorage-account-create%2Fazuredeploy.json)

1. Deploy the `MISP-Forwarder`
    * Add the `HTTP POST URL` to the `OrchestratorUri` parameter
    * Give the Managed Identity for this playbook the `Microsoft Sentinel Reader` role
2. Create an automation rule called `FWD-MISP`
    * Trigger
        * 'When incident is created'
    * Conditions
        * If Incident provider Equals Microsoft 365 Defender 
        * AND Title Contains malware was prevented
        * AND Tag Does not contain FWD-MISP
    * Actions
        * Run playbook `MISP-Forwarder`
        * And then Add tags FWD-MISP


### Add keyvault for MISPKEY secret

1. Create new keyvault
2. Give the managed identity of the `MISP-Orchestrator` read access on the KV, and add it to `Get, List` on the access policies
3. Add a new secret `MISPKEY` and add your MISPKEY to it
4. Add a new `Get Secret` step and configure it to retrieve your secret
5. Swap all the `MISPKEY`-variable references in HTTP Auth headers for the value of the KV secret

## Known issues

### Public IP requirement

This configuration requires you to have a public IP on your MISP server. 
We did this by exposing it behind a Application Gateway and configuring a WAF with an allowlist. This allows us to deploy this the Orchestrator-playbook as a premium logic app with a static IP and can let that IP through.

### Tags 

For some tests the internal tags were numbered differently, but this is as easy as changing out the numbers in the HTTP steps for the number of the tag in your MISP instance. You can also add more, both global and local tags. 

# Contributing

If you want to contribute - feel free to do so. Adding new entity types, or support for private IPs in Azure are both things that would be nice.

## Creators

This 'solution' was originally created by Sopra Steria Nordics Security Operation Center. 

![](https://www.soprasteria.no/images/librariesprovider2/sopra-steria-no-images/now-sine-bilder/soc-visuell-profil.jpg?sfvrsn=ce3122dc_1)

To learn more about us [click here.](https://azuremarketplace.microsoft.com/en-us/marketplace/consulting-services/soprasteria-fr.cyber-soc-sentinel)
