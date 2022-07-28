# AS-PagerDuty-Integration

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

This playbook is intended to be run from a Microsoft Sentinel incident. It will create a PagerDuty event with the related Microsoft Sentinel incident and entity information.
                                                                                                                                     
![PagerDuty_Demo](Images/PagerDuty_Demo.png)
 
                                                                                                                                     
#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* A PagerDuty integration key
                                                                                                                                    
# 
### Setup
                                                                                                                                     
To Create a PagerDuty Integration Key:
 
Log into your PagerDuty account at https://app.pagerduty.com/. Under the "**Services**" menu option, select "**Service Directory**". From the page, click the "**New Service**" button.
 
![PagerDuty_Create_Integration_Key_1](Images/PagerDuty_Create_Integration_Key_1.png)

                                                                                                       
Add a Name and optional Description like the following:

![PagerDuty_Create_Integration_Key_2](Images/PagerDuty_Create_Integration_Key_2.png)              
                                                                                       
                                                                                         
Select an escalation policy for your service. In this example, the default is used.

![PagerDuty_Create_Integration_Key_3](Images/PagerDuty_Create_Integration_Key_3.png)


Select a noise reduction option for your service. The "**Intelligent**" option is reccomended.

![PagerDuty_Create_Integration_Key_3.5](Images/PagerDuty_Create_Integration_Key_3.5.png)

                                                                                           
Finally, select the Microsoft Azure option under the Integrations section, then click "**Create Service**".

![PagerDuty_Create_Integration_Key_4](Images/PagerDuty_Create_Integration_Key_4.png)

                                                                                                  
You will be redirected to the service you have created. Under the Integrations tab view, you will find your integration key. This will be needed for the deployment of this playbook.
                                                                                                  
![PagerDuty_Create_Integration_Key_5](Images/PagerDuty_Create_Integration_Key_5.png)
                                                                                           
                                                                                                 
#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-PagerDuty-Integration%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-PagerDuty-Integration%2Fazuredeploy.json)                                             

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as “AS-PagerDuty-Integration” or you may change it.  

* **Integration Key**: Enter the value of the PagerDuty integration key created from the first section.

***Note***: Although the **Integration Key** parameter is of type secure string, it will still be visible in plain text in the deployed playbook. If this poses an internal security risk, it is advised utilize the key-vault instead.

Towards the bottom, click on “**Review + create**”. 

![PagerDuty_Deploy_1](Images/PagerDuty_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![PagerDuty_Deploy_2](Images/PagerDuty_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![PagerDuty_Deploy_3](Images/PagerDuty_Deploy_3.png)

Click on the “**Edit**” button. This will bring us into the Logic Apps Designer.

![PagerDuty_Deploy_4](Images/PagerDuty_Deploy_4.png)

The first step labeled "**Connections**" uses a connection created during the deployment of this playbook. Before the playbook can be run, this connection will either need to be authorized in this step, or an existing authorized connection may be alternatively selected.  

![PagerDuty_Deploy_5](Images/PagerDuty_Deploy_5.png)

To validate the connection created for this playbook connection, expand the "**Connections**" step and click the exclamation point icon next to the name matching the playbook.
                                                                                                
![PagerDuty_Deploy_6](Images/PagerDuty_Deploy_6.png)

When prompted, sign in to validate the connection.                                                                                                
                                                                                                
![PagerDuty_Deploy_7](Images/PagerDuty_Deploy_7.png)                                                                                                                             
                                                                                                                             
Once the connection step has been updated, click the "**Save**" button.

![PagerDuty_Deploy_8](Images/PagerDuty_Deploy_8.png)  

#
### Running the Playbook
To run this playbook automatically on incidents in Microsoft Sentinel, navigate to "**Automation**" under "**Configuration**" in the left-hand menu.

Click the "**Create**" button and select "**Automation Rule**" option from the dropdown.

![Nav_1](Images/Nav_1.png)


**1)** Enter a name for the automation rule. 

**2)** Then stipulate the conditions for which you would like a Microsoft Sentinel Incident to be sent to PagerDuty. In the example below, criteria are set so that only incidents with high severity will be sent to PagerDuty. 

**3)** Select the "**Run Playbook**" option under the "**Actions**" section. 

**4)** Then select the name of the playbook that was just deployed from this page. 

**5)** Review the default values under the "**Rule expiration**" and "**Order**" section, then click Apply.

![Nav_2](Images/Nav_2.png)

Once this saves, your new integration should run automatically.
