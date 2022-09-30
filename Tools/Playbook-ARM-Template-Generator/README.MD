## Playbook ARM Template Generator
**Author : Sreedhar Ande, Itai Yankelevsky**  
Export Microsoft Sentinel Playbooks (Azure LogicApps) in the quickest amount of time by sanitizing the JSON contains organizational information such as tenant ID, subscription information, connection strings, and other items that makes sharing a Playbook(Azure LogicApps) a daunting technical challenge.  

This PowerShell utility first evaluates your Azure logic app and any API connections that the logic app uses then generates template resources with the necessary parameters for deployment.  

You can use this ARM template for your own business scenarios or customize the template to meet your requirements.  

You can share it safely knowing that your organization’s information is stripped from the JSON and that it will work correctly in the recipient environment.  
> Blog: https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/export-microsoft-sentinel-playbooks-or-azure-logic-apps-with/ba-p/3275898  

> Demo: https://www.youtube.com/watch?v=scTtVHVzrQw

## Download and run the PowerShell script

1. Download the script 
  
   [![Download](./images/Download.png)](https://aka.ms/Playbook-ARM-Template-Generator)
   
   > Note: Linux Users, added required dll's

2. Extract the folder and open "Playbook_ARM_Template_Generator.ps1" either in Visual Studio Code/Windows PowerShell/PowerShell Core

   **Note**  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  
3. Script prompts you to enter your Azure Tenant Id

4. You are prompted to authenticate with credentials, once the user is authenticated, you will be prompted to choose 
	- Subscription	
	- Playbooks

5. After selecting playbooks, script prompts to select location on your local drive to save ARM Template  
   > Note: Tool converts microsoftsentinel connections to MSI during export
