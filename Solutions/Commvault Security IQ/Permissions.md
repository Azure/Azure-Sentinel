# Permissions Configuration

This document provides detailed steps to configure the required permissions for the Logic Apps:  
`logic-app-disable-data-aging`, `logic-app-disable-saml-provider`, and `logic-app-disable-saml-provider`.

---

## 1. Grant Automation Job Operator Permission on the Automation Account

### Steps:
1. Navigate to the **Azure Portal**.
2. Search for and open the **Automation Account** named `Commvault-Automation-Account`.
3. Go to the **Access Control (IAM)** section.
4. Click on **Add Role Assignment**.
5. In the **Role** dropdown, select **Automation Job Operator**.
6. In the **Assign Access To** dropdown, select **Azure AD User, Group, or Service Principal**.
7. Search for the **Managed Identity** of each Logic App:
   - `logic-app-disable-data-aging`
   - `logic-app-disable-saml-provider`
   - `logic-app-disable-user`
8. Select the Logic App's managed identity and click **Save**.
9. Repeat the above steps for all three Logic Apps.

---

## 2. Grant Key Vault Secrets User Permission on the Key Vault

### Steps:
1. Navigate to the **Azure Portal**.
2. Search for and open the **Key Vault** used to set up the Commvault Sentinel Data Connector.
3. If **Access Policies** are enabled:
   - Go to the **Access Policies** section.
   - Click **Add Access Policy**.
   - In the **Permissions** dropdown, select **Get**,**Set**,**List**,**Delete** and **Purge** for secrets.
   - In the **Principal** field, search for the **Managed Identity** of each Logic App:
     - `logic-app-disable-data-aging`
     - `logic-app-disable-saml-provider`
     - `logic-app-disable-user`
   - Click **Add** and then **Save**.
4. If **RBAC (Role-Based Access Control)** is enabled:
   - Go to the **Access Control (IAM)** section.
   - Click on **Add Role Assignment**.
   - In the **Role** dropdown, select **Key Vault Secrets Officer**.
   - In the **Assign Access To** dropdown, select **Azure AD User, Group, or Service Principal**.
   - Search for the **Managed Identity** of each Logic App:
     - `logic-app-disable-data-aging`
     - `logic-app-disable-saml-provider`
     - `logic-app-disable-user`
   - Select the Logic App's managed identity and click **Save**.
   - Repeat the above steps for all three Logic Apps.

---

By following these steps, the required permissions will be granted to the Logic Apps for both the Automation Account and the Key Vault.
