# Cohesity Restore From Last Snapshot Playbook
## Summary
This playbook restores the latest good Helios snapshot. It’s recommended for running by Backup Admins _only_ after they make sure that the existing data is compromised and rollback to the previous snapshot, even at the expense of data loss, is _really required_.

## Prerequisites
1. Create the _DataHawk API_ key:
* Go to the Cohesity Helios [login](https://helios.cohesity.com/#/login) page.
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_.
2. Create your Azure KeyVault with the name **Cohesity-Vault** (see [instructions](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)).
* Create the _ApiKey_ secret and assign the _API Key_ value from the previous step to it. Now your API key is securely saved in the Azure KeyVault.

**Note:** If you already did these steps for [another playbook](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/Cohesity_Close_Helios_Incident/readme.md), then you can skip them and reuse the same _ApiKey_ secret for this one.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Restore_From_Last_Snapshot%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

## Post-Deployment instructions
1. (_Recommendation_) Limit access rights to this playbook to only Backup Admins because this playbook rolls back customer data that can result in a loss of important data if used without a good reason.
* From the Microsoft Sentinel navigation menu, select _Settings_.
* In the _Settings_ blade, select the _Settings_ tab and expand _Playbook Permissions_.
* Select _Configure Permissions_ to open the _Manage Permissions_ panel.
* Select the required resource group and click _Apply_.
* Select _Done_.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
