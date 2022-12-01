# Rapid7InsightVM-RunScan

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

1. Obtains IPs from the incident.
2. Searches asset ids by the IPs.
3. Obtains a list of scan engines.
4. Sends an adaptive card to the Teams channel where the user can choose an action to be taken.

<img src="./teams_screenshot.png" width="50%"/><br>

5. Runs scans for selected IPs using chosen scan engines.
6. Add inforamtions about launched scans as a comment to the incident.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, [Rapid7 InsightVM API Connector](../../Rapid7InsightVMCloudAPIConnector/) needs to be deployed under the same subscription.
2. Obtain Rapid7 InsightVM API credentials. Refer to [Rapid7 InsightVM API Connector](../../Rapid7InsightVMCloudAPIConnector/) documentation.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Connector Name: Enter the Rapid7 InsightVM Logic App connector name here
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted.
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FPlaybooks%2FRapid7InsightVM-RunScan%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FPlaybooks%2FRapid7InsightVM-RunScan%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps 1-5 for Teams connection resource
7. Click the Rapid7 connection resource
8. Click edit API connection
9. Provide API key
10. Click Save

#### b. Configurations in Sentinel

1. In Microsoft sentinel, analytical rules should be configured to trigger an incident that contains IPs. In the *Entity maping* section of the analytics rule creation workflow, IP should be mapped to **Address** identitfier of the **IP** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook. Check the [documentation](https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook) to learn more about automation rules.
