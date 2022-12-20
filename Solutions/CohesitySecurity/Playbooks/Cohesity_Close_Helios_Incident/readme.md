# Cohesity Close Helios Incident Playbook
## Summary
This playbook closes the corresponding Helios ticket.

## Prerequisites
1. Create the _DataHawk API_ key:
* Go to the Cohesity DataHawk [login](https://helios.cohesity.com/#/login) page.
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_.
2. Create your Azure key vault with the name **Cohesity-Vault** (see [instructions](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)).
* Create the _ApiKey_ secret and assign the _API Key_ value from the previous step to it. Now your API key is securely saved in the Azure KeyVault.
**Note:** If you already did these steps for [another playbook](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/Cohesity_Restore_From_Last_Snapshot#readme), then you can skip them and reuse the same _ApiKey_ secret for this one.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Restore_From_Last_Snapshot%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

#  References
- [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
