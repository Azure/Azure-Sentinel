# Integrating Guardicore Incidents into Azure Sentinel 

Author: Arbala Security

For any technical questions, please contact info@arbalasystems.com.

This playbook will give Azure Sentinel the ability to query your Guardicore Centra Cloud instance API to retrieve established incidents. The API query will be sent every 10 minutes. Incidents that have had their data copied to Sentinel logs will be marked with the “Sentinel” tag in Guardicore. 


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FArbala-Security%2FGuardicore-Import-Incidents%2Fmaster%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FArbala-Security%2FGuardicore-Import-Incidents%2Fmaster%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
                                                  
                                                 
#

You will need the following items to enter in the playbook settings during deployment: 

* URL for your Guardicore instance. 

* A Username/Password that is a Local Administrator in your Guardicore environment. 

* The Azure Sentinel Workspace ID where you want the incidents logged. 

* The Primary or Secondary Key to your workspace. 

Open your browser and ensure you are logged into your Azure Sentinel workspace. In separate tab, open the link to our playbook on the Arbala Security GitHub Repository:

https://github.com/Arbala-Security/Guardicore-Import-Incidents

From there, click the “Deploy to Azure” button at the bottom and it will bring you to the Custom Deployment Template.

![Deploy](Images/GitDeploy.png)

In the **BASICS** section:  

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **SETTINGS** section:   

* **Playbook Name**: This can be left as “Guardicore-Import-Incidents” or you may change it.  

* **GCURL**: Enter your Guardicore tenant URL here. You can replace <guardicore_instance_url> with cus-0000.cloud.guardicore, where 0000 is your 4 digit customer number or copy and paste the URL from your Guardicore instance. It must look exactly like - https://cus-0000.cloud.guardicore.com  Also, ensure there is no / after the .com. 

![GCURL](Images/GCURL.png)

* **GC Username**: Replace text with username of the Guardicore Admin account you want to use. 

* **GC Password**: Replace text with password of the Guardicore Admin account you want to use. 

Towards the bottom ensure you check the box accepting the terms and conditions and then click on “Purchase”. 

![template](Images/template.png)

The playbook should take less than a minute to deploy. Return to your Azure Sentinel workspace and click on “Playbooks.” Next, click on your newly deployed playbook. Don’t be alarmed to see that the status of the playbook shows failed. We still need to edit the playbook to enter the Azure Sentinel Workspace ID and Key.  

![playbookclick](Images/playbookclick.png)

Click on the “Edit” button. This will bring us into the Logic Apps Designer.

![editbutton](Images/editbutton.png)

Click on the bottom bar labeled “For each Guardicore incident”. 

![Logicapp1](Images/Logicapp1.png)

Click on the bar labeled “If no Sentinel tag was found”. 

![Logicapp2](Images/Logicapp2.png)

Click on “Connections”.  

![Logicapp3](Images/Logicapp3.png)

Click on the circled exclamation point under the word "Invalid". 

![Logicapp4](Images/Logicapp4.png)

In the **Connection Name** put GCIncidents. The next fields are **Workspace Key** (Primary or Secondary Key) and **Workspace ID**. Follow the instructions at the bottom of this page to find those values. Once you have them, copy and paste them into their respective fields. Now click the update button.  

![Logicapp5](Images/Logicapp5.png)

You should see the that the “Send Data” box has updated and displays “Connected to GCIncidents.” Click the X to close the Logic App Designer. There is no need to click a save button.  

![Logicapp6](Images/Logicapp6.png)

Depending on how many and how frequently you have incidents created in Guardicore, it could take a few minutes or several hours for the logs to show up Sentinel. You can view the incident logs by returning to your Azure Sentinel workspace and clicking on “Logs.” You should have a new custom log called “GCIncidents_CL” – type that into your query window and click run. Adjust the time range, as necessary. Each line returned contains the details for each individual incident returned from the Guardicore API. 

![final](Images/final.png)

## Finding your Azure Sentinel Workspace ID and Primary/Secondary Key 

To find your Workspace ID and Primary/Secondary key, start by clicking on “Settings” from the Azure Sentinel workspace you want the incidents sent to. Then click on “Workspace Settings” under the Azure Search Bar. 

![settings1](Images/settings1.png)

Click on “Advanced Settings”. 

![settings2](Images/settings2.png)


Next, click on “Connected Sources” and then “Windows Servers” to display your Workspace ID and either Primary or Secondary key. 

![settings3](Images/settings3.png)

For any technical questions, please contact info@arbalasystems.com.
