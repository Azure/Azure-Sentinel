# AS-IAM-Entra-ID-Master-Playbook

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Entra-ID-Master-Playbook%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Entra-ID-Master-Playbook%2Fazuredeploy.json)       

This playbook is intended to be run from a Microsoft Sentinel Incident. It will take the IP and account entities and run two separate playbooks to indicate compromise and revoke access to Microsoft Entra ID. The playbooks that will be run are as follows:

* **AS-IP-Blocklist-HTTP**: This will add the IP address from the Microsoft Sentinel incident to a Microsoft Azure Conditional Access Named Locations list, indicating a compromised IP

* **AS-Microsoft-Entra-ID-Revoke-User-Sessions-HTTP**: This will revoke the Microsoft Entra ID user sessions from the Microsoft Sentinel incident account entities
                                                                                                                               
![MasterPlaybook_Demo_1](Images/MasterPlaybook_Demo_1.png)

![MasterPlaybook_Demo_2](Images/MasterPlaybook_Demo_2.png)
 
                                                                                                                                     
#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

* Both of the playbooks included in this repository must first be deployed


#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-IAM-Entra-ID-Master-Playbook/tree/main/AS-IAM-Entra-ID-Master-Playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Entra-ID-Master-Playbook%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-IAM-Entra-ID-Master-Playbook%2Fazuredeploy.json)                                             

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as "**AS-IAM-Entra-ID-Master-Playbook**" or you may change it

* **FirstNestedPlaybook**: Enter the name of the first playbook deployed, or leave it as the default value, "**AS-IP-Blocklist-HTTP**", if this was not changed

* **SecondNestedPlaybook**: Enter the name of the second playbook deployed, or leave it as the default value, "**AS-Microsoft-Entra-ID-Revoke-User-Sessions-HTTP**", if this was not changed

Towards the bottom, click on “**Review + create**”. 

![MasterPlaybook_Deploy_1](Images/MasterPlaybook_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![MasterPlaybook_Deploy_2](Images/MasterPlaybook_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "Deployment details" section to view them. To view the deployed Logic App, click the resource that corresponds to it.

![MasterPlaybook_Deploy_3](Images/MasterPlaybook_Deploy_3.png)
