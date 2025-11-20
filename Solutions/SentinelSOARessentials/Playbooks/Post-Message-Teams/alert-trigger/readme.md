# Post-Message-Teams (Alert Trigger)

## Summary
This playbook posts a message in a Microsoft Teams channel when an alert is created in Microsoft Sentinel. The message includes key alert details such as severity, title, status, number, creation time, URL, and entities.

## Prerequisites
- A Microsoft Teams account with permission to post messages to the target channel.
- Teams Group ID and Channel ID (can be found in the Teams web URL).

## Deployment instructions

1. To deploy the playbook, click the Deploy to Azure button below. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Playbook Name
    - Teams Group ID
    - Teams Channel ID

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FPost-Message-Teams%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FPost-Message-Teams%2Falert-trigger%2Fazuredeploy.json)
<br><br>

## Post-deployment Instructions

### a. Authorize connections
Once deployment is complete, authorize each connection.

1. Open the Logic App in the Azure portal.
2. Click the Teams connector resource.
3. Click Edit API connection.
4. Click Authorize.
5. Sign in.
6. Click Save.
7. Repeat steps for other connections as needed.

> Note: The message will be sent from the user who creates the connection.

### b. Assign Playbook Log Analytic Reader Role
To allow the playbook to read from the Log Analytics workspace, assign the **Log Analytics Reader** role to the playbook's managed identity:

1. In the Azure portal, go to your Log Analytics workspace.
2. Select **Access control (IAM)** from the left menu.
3. Click **Add > Add role assignment**.
4. In the **Role** dropdown, select **Log Analytics Reader**.
5. In the **Assign access to** dropdown, select **Managed identity**.
6. Click **Select members**, search for and select the Logic App (playbook) name/managed identity.
7. Click **Review + assign** to complete the process.

> Note: It may take a few minutes for the permissions to propagate.

### c. Attach the playbook
1. In Microsoft Sentinel, configure an automation rule to trigger this playbook when an alert is created.
   - [Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)
> Note: Enable the playbook if it is disabled before assigning it to the automation rule.

## Screenshots

**Playbook**<br>
![Playbook](./images/designerAlertLight.png)

**Teams Message Example**<br>
![Teams Message Light](../images/TeamsLight.png)
![Teams Message Dark](../images/TeamsDark.png)
