## Review and Manage Data Table Retention
**Author : Sreedhar Ande**

## Download and run the PowerShell script

1. Download the script 
  
   [![Download](/Tools/Archive-Log-Tool/images/Download.png)](https://aka.ms/Archive-Logs-Tool)

2. Extract the folder and open "Configure-Long-Term-Retention.ps1" either in Visual Studio Code/PowerShell

   ***Note***  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  
3. Script prompts you to enter your **Azure Tenant Id**

4. **Supports both Azure Commercial and Azure Gov Tenants**  
5. You are prompted to authenticate with credentials, once the user is authenticated, you will be prompted to choose 
	- Subscription
	- Log Analytics Workspace
	- Table Plan
	- Archive Days

6.	Provide archiveRetention value - The value beyond two years is restricted to full years. Allowed values are: [4-730], 1095, 1460, 1826, 2191, 2556 days.  
	Note: Archive retention is calculated by using archiveRetention = totalRetentionInDays - retentionInDays.
