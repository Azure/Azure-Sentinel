
Configure Data Connector - Step-by-Step Guide
=============================================

This guide provides instructions to configure the **Commvault Cloud Data Connector** after installing the Commvault Cloud Sentinel solution.

---

### Steps to Configure the Data Connector

#### 1. Open the Data Connector Page
1. Navigate to the **Microsoft Sentinel** workspace in the Azure Portal.
2. Go to the **Data Connectors** section.
3. Search for **CommvaultSecurityIQ** in the list of connectors.
4. Click on the **CommvaultSecurityIQ** connector to open its configuration page.

---

#### 2. Copy Workspace Details
1. On the connector details page, locate the **Workspace ID** and **Primary Key**.
2. Copy these values as they will be required during the deployment process.

---

#### 3. Deploy the Connector to Azure
1. Click the **Deploy to Azure** button on the connector page.
2. This will redirect you to the Azure Resource Manager (ARM) template deployment page.

---

#### 4. Fill in Deployment Details
1. Select the appropriate **Subscription** and **Resource Group** where the connector will be deployed.
2. Provide the following required parameters:
   - **Key Vault Name**: Enter the name of the KeyVault where the required secrets are stored.
   - **App Insights Workspace Resource ID**: Select the Log Analytics Workspace associated with your Sentinel instance, and copy ResourceId from the properties tab.
   - **Workspace ID**: Paste the Workspace ID copied earlier.
   - **Primary Key**: Paste the Primary Key copied earlier.

---

#### 5. Review and Deploy
1. Review the deployment details to ensure all parameters are correct.
2. Click **Review + Create** to validate the configuration.
3. Once validation is complete, click **Create** to deploy the connector.

---

#### 6. Post-Deployment Steps
 - After the Function App is deployed, note down the **name of the Function App**.
 - Navigate to the **Key Vault** in the Azure Portal.

*If Access Policies are Enabled:*

 - Go to the **Access Policies** section of the Key Vault. 
 - Add a new access policy:
	 - Select the **Function App** as the principal.
	 - Grant the Function App permissions to **Get**,**Set**,**List**,**Delete** and **Purge** secrets.
	 - Save the changes to apply the access policy.

*If RBAC is Enabled:*

 - Go to the **Access Control (IAM)** section of the Key Vault.
 - Click **Add Role Assignment**.
	 - In the **Role** dropdown, select **Key Vault Secrets Officer**.
	 - In the **Assign Access To** dropdown, select **Azure AD User, Group, or Service Principal**.
	 - Search for the **Function App's managed identity** (it will have the same name as the Function App).
	 - Select the Function App and click **Save**.

---

By following these steps, you will successfully configure the Commvault Cloud Data Connector for Microsoft Sentinel and ensure the Function App has the necessary permissions to access the Key Vault.
