## Playbook ARM Template Generator
**Author : Sreedhar Ande, Itai Yankelevsky**  
To automate deployment of Microsoft Sentinel Playbooks (Azure LogicApps), this PowerShell script helps to create an Azure Resource Manager (ARM) template.  

## Download and run the PowerShell script

1. Download the script 
  
   [![Download](./images/Download.png)](https://aka.ms/Playbook-ARM-Template-Generator)

2. Extract the folder and open "Playbook_ARM_Template_Generator.ps1" either in Visual Studio Code/PowerShell(Admin)

   **Note**  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  
3. Script prompts you to enter your Azure Tenant Id

4. You are prompted to authenticate with credentials, once the user is authenticated, you will be prompted to choose 
	- Subscription
	- Log Analytics Workspace
	- Playbooks

5.	After selecting playbooks, script prompts to select location on your local drive to save ARM Template