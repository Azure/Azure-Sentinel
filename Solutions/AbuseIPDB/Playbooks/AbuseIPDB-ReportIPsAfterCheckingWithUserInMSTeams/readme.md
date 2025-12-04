# AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

1. Sends an adaptive card to the Teams channel where the analyst can choose an action to be taken.

<img src="./teams_screenshot.png" width="50%"/><br>

2. Assigns attack category. At least one category is required, but you may add additional [categories]("https://www.abuseipdb.com/categories")
3. Adds comment with relative information about the attack.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, AbuseIPDB Connector needs to be deployed under the same subscription.
2. Obtain AbuseIPDB API credentials.
3. Obtain Teams group id and channel id.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAbuseIPDB%2FPlaybooks%2FAbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAbuseIPDB%2FPlaybooks%2FAbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Open playbook which has been deployed
2. Click API connection on left side blade
3. Click the Microsoft Sentinel connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections

#### b. Configurations in Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. An incident should have the *IPAddress* custom entity that contains IP address. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents.
2. Configure the automation rules to trigger the playbook.