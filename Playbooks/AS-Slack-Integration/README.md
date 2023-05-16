# AS-Slack-Integration

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

This playbook is intended to be run from a Microsoft Sentinel incident. It will create a Slack post with the related Microsoft Sentinel incident information including parsed entity information.

![Slack_Demo](Images/Slack_Demo.png)


#
### Requirements

The following items are required under the template settings during deployment:
                                                                                                                                     
* A Slack App Token
* The Slack Channel Id to post Microsoft Sentinel incident information to
 
For this playbook, you will need to create a Slack Bot app to securely post to your Slack Workspace.                                                                                    

# 
### Setup

To create a Slack App and obtain a Bot Token:
                                                                                                                                     
From your Slack Workspace, navigate to https://api.slack.com/apps/ and click the "**Create a new Slack app**" button.

![Slack_App_1](Images/Slack_App_1.png)


Select the "**From Scratch**" option.

![Slack_App_1.5](Images/Slack_App_1.5.png)


Enter in "**Microsoft Sentinel**" for the app name and then select a workspace.  
Finally, click "**Create App**" .

![Slack_App_2](Images/Slack_App_2.png)


Now we need to add permissions to the app in order for it to post messages in channels. 
From the "**Basic Information**" section of your newly created app, click "**Permissions**".

![Slack_App_3](Images/Slack_App_3.png)


Scroll down to the "**Scopes**" section and click the "**Add an OAuth Scope**" button under "**Bot Token Scopes**".
Select the "**chat:write**" option.

![Slack_App_4](Images/Slack_App_4.png)


Scroll back up to the top of the page and click the "**Install to Workspace**" button, which should now be green.

![Slack_App_5](Images/Slack_App_5.png)


Click "**Allow**" and then copy the entire value in the "**Bot User OAuth Token**" field. 

![Slack_App_6](Images/Slack_App_6.png)


If you would like, you can also add the Microsoft Sentinel Logo under "**Display Information**". This section is located under the "**Basic Information**" menu option.

![Slack_App_7](Images/Slack_App_7.png)


Your Slack app is now configured. However, before it can post messages, it needs to be invited to the desired channel.
Type "**/invite**" in the desired channel, then select the "**Add apps to this channel**" option.

![Slack_App_8](Images/Slack_App_8.png)


Find your Microsoft Sentinel app and click "**Add**".

![Slack_App_9](Images/Slack_App_9.png)


Lastly, you will need to take note of your channel id for the playbook deployment.
This can be found by running the browser version of slack and looking at the url of the desired channel, like so:

https://app.slack.com/client/{workspace-id}/{**channel-id**}}


#
### Deployment   

To configure and deploy this playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Slack-Integration%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Slack-Integration%2Fazuredeploy.json)                                                    

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as “AS-Slack-Integration” or you may change it.  

* **OAuth Token**: Enter the value of the Slack OAuth Token created from the first section.

* **Channel Id**: Enter the value of the Slack channel id noted from the first section.

***Note***: Although the **OAuth Token** parameter is of type secure string, it will still be visible in plain text in the deployed playbook. If this poses an internal security risk, it is advised utilize the key-vault instead.

Towards the bottom, click on “**Review + create**”. 

![Slack_Deploy_1](Images/Slack_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Slack_Deploy_2](Images/Slack_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![Slack_Deploy_3](Images/Slack_Deploy_3.png)

Click on the “**Edit**” button. This will bring us into the Logic Apps Designer.

![Slack_Deploy_4](Images/Slack_Deploy_4.png)

The first step labeled "**Connections**" uses a connection created during the deployment of this playbook. Before the playbook can be run, this connection will either need to be authorized in this step, or an existing authorized connection may be alternatively selected.  

![Slack_Deploy_5](Images/Slack_Deploy_5.png)

To validate the connection created for this playbook connection, expand the "**Connections**" step and click the exclamation point icon next to the name matching the playbook.
                                                                                                
![Slack_Deploy_6](Images/Slack_Deploy_6.png)

When prompted, sign in to validate the connection.


![Slack_Deploy_7](Images/Slack_Deploy_7.png)


#
### Running the Playbook

To run this playbook automatically on incidents in Microsoft Sentinel, navigate to "**Automation**" under "**Configuration**" in the left-hand menu.

Click the "**Create**" button and select "**Automation Rule**" option from the dropdown.

![Nav_1](Images/Nav_1.png)


**1)** Enter a name for the automation rule. 

**2)** Then stipulate the conditions for which you would like a Microsoft Sentinel Incident to be sent to Slack. In the example below, criteria are set so that only incidents with medium or high severity will be posted in Slack. 

**3)** Select the "**Run Playbook**" option under the "**Actions**" section. 

**4)** Then select the name of the playbook that was just deployed from this page. 

**5)** Review the default values under the "**Rule expiration**" and "**Order**" section, then click Apply.

![Nav_2](Images/Nav_2.png)

Once this saves, your new integration should run automatically.
