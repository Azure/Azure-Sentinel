# PC Matic Super Shield BlockAllowProcess Playbook
 ## Summary
 Trigger this playbook from the Incident Overview workbook to block or allow a process.

 ## IMPORTANT NOTE
 The following instructions apply only to the Logic Apps. For comprehensive, detailed instructions, please use the documentation at  - [PC Matic Sentinel Solution support documentation](https://www.pcmatic.com/)

### Prerequisites 
1. API credentials. To get API credentials, login into the PC Matic portal and navigate to Account Settings --> User Management. Click the 'Add User' button and create a new user with the 'API Credentials' user role.
3. [Important step]Store the API username and password as a secret in Key vault. Format the secret as a colon-separated pair, e.g. username@example.com:passw0rd.Provide the name of the stored secret during deployment.

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPCMatic SuperShield%2FPlaybooks%2FBlockAllowProcess%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPCMatic SuperShield%2FPlaybooks%2FBlockAllowProcess%2Fazuredeploy.json)

2. Fill in the required parameters:
    * Keyvault name : Enter the key vault name where secret key is stored .
    * PC Matic API Credentials Secret name : Your Key name for the stored api secret .

### Post-Deployment instructions 
#### a. Authorize connections (Perform this action if needed)
Once deployment is complete, you will need to authorize each connection.
1.  Go into BlockAllowProcess logic app
2.  Click Edit
3.	Click first element
4.  Click “Add New”
5.  Sign in
6.  Click on second element
7.  Click “Add New”
8.  Enter key vault name
9.  Sign in
10. Scroll to bottom of LogicApp
11. Click on last item
12. Select unchecked connection
13. Click “Save”

14.	Repeat steps for RemoveProcess

#### b. 12. Configure Logic App Permissions
1.  In Sentinel, go to Settings (bottom of the left navigation)
2.  Click on Settings tab
3.  Open up Playbook Permissions
4.  Click “Configure Permissions”
5.  Check Resource Group created in Step 1
6.  Click “Apply”

7.  Search for Key Vaults in main search field at top of page
8.  Click on “Key Vaults”
9.  Click on Key Vault created in Step 8
10. Click “Access Policies”
11. Click “Create”
12. Select “Get” and “List” under Secret Permissions
13. Click “Next”
14. Select all users who manage the PC Matic Sentinel solution
15. Click “Next”
16. Click “Next”
17. Click “Create”


#  References
 - [PC Matic Sentinel Solution support documentation](https://www.pcmatic.com/)