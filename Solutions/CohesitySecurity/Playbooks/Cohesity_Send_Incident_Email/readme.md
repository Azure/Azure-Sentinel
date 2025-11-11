# Cohesity Incident Email Playbook
## Summary
This playbook sends an email to the recipient with the incident details..

## Prerequisites
1. Create a distribution list (email) that will be used for sending out incident notifications.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Send_Incident_Email%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name__: Playbook display name.
* __Email ID__: Email (preferably a distribution list) for sending out incident notifications

## Post-Deployment instructions
1. Make sure the user that runs the playbook has the role _Microsoft Sentinel Playbook Operator_ assigned. To assign the role,
* Under the _Subscriptions_ tab from the _Home_ page, choose your subscription name.
* Choose the _Access Control (IAM)_ option from the left pane.
* Click on _Add > Add Role Assignment_ and add _Microsoft Sentinel Playbook Operator_ to the user.

2. To enable this playbook, you need authorize Outlook connection ([details](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/understanding-api-connections-for-your-microsoft-sentinel/ba-p/2593973))
* Go to _Logic Apps_ and choose your playbook.
* Choose _Development Tools\API Connections_.
* Select a connection you'd like to authorize.
* Click on _General\Edit API Connection_.
* Press the _Authorize_ button.

Alternatively, you can follow these steps to achieve the same goal. This would be especially useful if the previous steps didn’t work for you.
* Go to _Logic Apps_.
* Click on the playbook and press _Edit_.
* Choose _Send email (V2)_ block.
* Click on _Change Connection_.
* Click on the "!" icon to authorize the connection or choose a different, previously authorized, connection.
* Press _Save_ button to save changes in your playbook.
* If it doesn't work, repeat the steps but either choose a different connection or fix possible authorization errors for the chosen one.

## Troubleshooting
To change the email address in the playbook:
* In your Microsoft Sentinel workspace, go to the _Automation_ under the _Configuration_ pane.
* Under _Active Playbooks_, select the playbook and click on _Edit_.
* On the _Logic App Designer_ page, select _Initialize variable 2_.
* Under the value section, enter the email address for the incident notifications.
* Click _Save_.
If the playbook fails to execute, go to your playbook _Overview_ pane that has status of all runs. By looking at the details, you can get more ideas on what went wrong.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
