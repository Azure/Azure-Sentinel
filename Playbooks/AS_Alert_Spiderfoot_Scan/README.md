# AS_Alert_Spiderfoot_Scan

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com

This playbook is intended to be run from an Azure Sentinel alert. It will pull email addresses from the account entities in an alert and use them as targets in a Spiderfoot scan. By default, the scan is created using the HaveIBeenPwned module. The resulting report of that scan will be emailed to a recipient specified upon deployment.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS_Alert_Spiderfoot_Scan%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/AS_Alert_Spiderfoot_Scan/azuredeploy.json" target="_blank"><img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/></a>

#

You will need the following items to enter into the template settings during deployment:

* The URL of your Spiderfoot account.
* Your Spiderfoot API key.
* The email address you would like to have the completed Spiderfoot report link sent to.

 #
 To obtain your Spiderfoot API key:

 Log into your Spiderfoot account and in the top right-hand corner under your name, click the "API Key" option.

![API Key](Images/APIKey.png)

 #
To configure and deploy this playbook:

Click the “Deploy to Azure” button and this will bring you to the Custom Deployment Template.

In the first section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.

In the **Parameters** section:

* **Playbook Name**: This can be left as “AS_Alert_Spiderfoot_Scan” or you may change it.

* **Spiderfoot URL**: Once you have logged into your Spiderfoot account, paste the URL of your homepage here. Your unique subdomain is needed to make API calls. This should replace "example" in "example.hx.spiderfoot.net". Nothing else needs to be changed; do not include "https://".

* **Spiderfoot API Key**: Enter your Spiderfoot API key.

* **Email Addresses**:  Enter the desired email addresses here. If entering more than one, separate with a semicolon.

Towards the bottom, click on “Review + create”.

![Template](Images/template1.png)

Once the resources have validated, click on "Create".

![Template](Images/template2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "Deployment details" section to view them.
Click the one corresponding to the Logic App.

![Success](Images/success.png)

Click on the “Edit” button. This will bring us into the Logic Apps Designer.

![Edit](Images/logicappedit.png)

Click on the bar labeled “Connections”.

Here you can select an existing connection or create a new one. You will need to do this twice.

![Logicapp1](Images/logicapp1.png)

Click the save button.

#
To run this playbook on an alert in Azure Sentinel, navigate to "Incidents" under "Threat Management" in the left-hand menu.

![Nav1](Images/nav1.png)

From there you can select an incident that has one or more account entities.

![Nav2](Images/nav2.png)

Click the "View full details" button in the bottom right-hand corner.

In the middle window, scroll to the right and click "View playbooks".

![Nav3](Images/nav3.png)

Find the AS_Alert_Spiderfoot_Scan playbook and click run.

![Nav4](Images/nav4.png)

The playbook will run until the Spiderfoot scan it initiates is completed. Once the scan is finished, an email will be sent to the addresses specified in the deployment parameters. The email will contain the account entities pulled from the alert, the modules used in the Spiderfoot scan, and a link to the completed Spiderfoot report.
