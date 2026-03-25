# AS-Checkmarx-SAST-Ingestion

Author: Accelerynt

For any technical questions, please contact [info@accelerynt.com](mailto:info@accelerynt.com)

This playbook will create a unidirectional integration with Microsoft Sentinel. It will pull Checkmarx SAST (Static Application Security Testing) scan findings into a Microsoft Sentinel custom log table where they can be tracked, queried, and correlated with other security data. This uses Data Collection Rules (DCR), Data Collection Endpoints (DCE), and custom log tables.

![Checkmarx_SAST_Integration_Demo_1](Images/Checkmarx_SAST_Integration_Demo_1.png)

> [!NOTE]
> Estimated Time to Complete: 45 minutes

> [!TIP]
> Required deployment variables are noted throughout. Reviewing the deployment page and filling out fields as you proceed is recommended.

> [!NOTE]
> This playbook handles **SAST findings only**. For audit event ingestion, see the [AS-Checkmarx-Audit-Ingestion](https://github.com/Accelerynt-Security/AS-Checkmarx-Audit-Ingestion) playbook. Note that only a single DCE and a single Key Vault secret need to be created for both playbooks.

#

### Requirements

The following items are required under the template settings during deployment:

* **Checkmarx Client Secret or Refresh Token** - a client secret (recommended) or refresh token with permissions to query SAST results from your Checkmarx One instance. [Documentation link](#checkmarx-api-permissions)
* **Checkmarx IAM Base URL** - the base URL for Checkmarx IAM authentication based on your region (e.g., `https://us.iam.checkmarx.net`). [Documentation link](#checkmarx-api-permissions)
* **Checkmarx AST Base URL** - the base URL for Checkmarx AST API calls based on your region (e.g., `https://us.ast.checkmarx.net`). [Documentation link](#checkmarx-api-permissions)
* **Checkmarx Tenant** - your Checkmarx tenant/realm name used in the authentication URL. [Documentation link](#checkmarx-api-permissions)
* **Azure Key Vault Secret** - this will be used to store your Checkmarx client secret or refresh token. [Documentation link](#create-an-azure-key-vault-secret)
* **Log Analytics Workspace** - the name, location, subscription ID, resource group, and resource ID of the Log Analytics workspace that the Checkmarx data will be sent to. [Documentation link](#log-analytics-workspace)

#

### Checkmarx API Permissions

The Checkmarx API client requires the following permissions:

| Scope | Permission |
| --- | --- |
| ast-api | **Read** |

This playbook supports two OAuth grant types for authentication. Select the method that matches your Checkmarx One configuration:

#### Option A: Client Credentials (Recommended)

The `client_credentials` grant type is recommended for production deployments. It uses a client ID and client secret for authentication.

1. Navigate to your Checkmarx One tenant
2. Go to **IAM** > **OAuth Clients**
3. Create a new OAuth client or use an existing one with the required scopes
4. Copy the **Client ID** and **Client Secret** - the secret will be stored in Azure Key Vault
5. During deployment, set the **Grant Type** parameter to `client_credentials`

#### Option B: Refresh Token

The `refresh_token` grant type uses a refresh token obtained from an interactive login or API key flow.

1. Navigate to your Checkmarx One tenant
2. Go to **IAM** > **API Keys** or use the authentication endpoint
3. Create an API key or OAuth client with appropriate scopes
4. Generate a refresh token for the `ast-app` client
5. Copy the refresh token - this will be stored in Azure Key Vault
6. During deployment, set the **Grant Type** parameter to `refresh_token`

Select the base URLs for your region using the table below:

| Region | IAM Base URL | AST Base URL |
| --- | --- | --- |
| US | `https://us.iam.checkmarx.net` | `https://us.ast.checkmarx.net` |
| EU | `https://eu.iam.checkmarx.net` | `https://eu.ast.checkmarx.net` |
| DEU | `https://deu.iam.checkmarx.net` | `https://deu.ast.checkmarx.net` |
| ANZ | `https://anz.iam.checkmarx.net` | `https://anz.ast.checkmarx.net` |
| IND | `https://ind.iam.checkmarx.net` | `https://ind.ast.checkmarx.net` |

Note the URLs you selected, as they will be needed for the deployment step.

#

### Setup

#### Create an Azure Key Vault Secret

> [!NOTE]
> If you have already created the **checkmarx-integration-secret** secret, you may skip this step.

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![Checkmarx_SAST_Key_Vault_1](Images/Checkmarx_SAST_Key_Vault_1.png)

Choose a name for the secret, such as "**checkmarx-integration-secret**", and enter your Checkmarx client secret or refresh token in the "**Value**" field. All other settings can be left as is. Click "**Create**".

![Checkmarx_SAST_Key_Vault_2](Images/Checkmarx_SAST_Key_Vault_2.png)

#### Log Analytics Workspace

Navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the workspace that the Checkmarx data will be sent to, and take note of the following values:

![Checkmarx_SAST_Log_Analytics_Workspace_1](Images/Checkmarx_SAST_Log_Analytics_Workspace_1.png)

From the left menu blade, click **Overview** and take note of the **Name** and **Location** field values. These will be needed for the DCE deployment.

![Checkmarx_SAST_Log_Analytics_Workspace_2](Images/Checkmarx_SAST_Log_Analytics_Workspace_2.png)

From the left menu blade, click **Overview** and take note of the **Subscription**, **Resource group**, and **Resource ID** shown in the JSON View. These will be needed for the DCR and Logic App deployments.

![Checkmarx_SAST_Log_Analytics_Workspace_3](Images/Checkmarx_SAST_Log_Analytics_Workspace_3.png)

#

### Deployment

#### Deploy the SAST Findings Custom Table

The custom table **CheckmarxSASTFindings_CL** must be created before deploying the DCR.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeploySASTTable.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeploySASTTable.json)

Click the "**Deploy to Azure**" button and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.

In the **Instance details** section:

* **Workspace Name**: Enter the **Name** of your Log Analytics workspace referenced in [Log Analytics Workspace](#log-analytics-workspace).

Towards the bottom, click on "**Review + create**".

![Checkmarx_SAST_Deploy_Table_1](Images/Checkmarx_SAST_Deploy_Table_1.png)

Once the resources have validated, click on "**Create**".

#### Deploy the Data Collection Endpoint (DCE)

The DCE provides the ingestion endpoint URL for the Logic App.

> [!NOTE]
> If you have already deployed the **AS-Checkmarx-Audit-Ingestion** playbook, a DCE already exists in your workspace. You may skip this step and use the existing DCE's Logs Ingestion Endpoint URL and Resource ID for the DCR deployment below. Navigate to your existing DCE resource to find these values.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeployDCE.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeployDCE.json)

Click the "**Deploy to Azure**" button and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.

In the **Instance details** section:

* **Data Collection Endpoint Name**: This can be left as "**dce-checkmarx-log-ingestion**" or you may change it.
* **Location**: Enter the **Location** of your Log Analytics workspace referenced in [Log Analytics Workspace](#log-analytics-workspace). Note that this may differ from the Region field, which is automatically populated based on the selected Resource group.

Towards the bottom, click on "**Review + create**".

![Checkmarx_SAST_Deploy_DCE_1](Images/Checkmarx_SAST_Deploy_DCE_1.png)

Once the resources have validated, click on "**Create**".

After deployment, navigate to the "**Outputs**" section and take note of the values listed, as these will be needed for subsequent deployment steps.

![Checkmarx_SAST_Deploy_DCE_2](Images/Checkmarx_SAST_Deploy_DCE_2.png)

#### Deploy the SAST Findings Data Collection Rule (DCR)

The DCR defines the schema and destination for the ingested SAST findings data.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeploySASTDCR.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2FAzureDeploySASTDCR.json)

Click the "**Deploy to Azure**" button and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.

In the **Instance details** section:

* **Data Collection Rule Name**: This can be left as "**dcr-checkmarx-sast-log-ingestion**" or you may change it.
* **Location**: Enter the location listed on your Log Analytics workspace.
* **Workspace Resource Id**: Enter the full resource ID of your Log Analytics workspace referenced in [Log Analytics Workspace](#log-analytics-workspace).
* **Data Collection Endpoint Resource Id**: Enter the full resource ID of the DCE created in the previous step.

Towards the bottom, click on "**Review + create**".

![Checkmarx_SAST_Deploy_DCR_1](Images/Checkmarx_SAST_Deploy_DCR_1.png)

Once the resources have validated, click on "**Create**".

After deployment, navigate to the "**Outputs**" section and take note of the **dcrImmutableId** value, as this will be needed for the Logic App deployment.

![Checkmarx_SAST_Deploy_DCR_2](Images/Checkmarx_SAST_Deploy_DCR_2.png)

#### Deploy the Logic App Playbook

The Logic App performs the daily ingestion of Checkmarx SAST scan findings.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-SAST-Ingestion%2Fazuredeploy.json)

Click the "**Deploy to Azure**" button and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.

In the **Instance details** section:

* **Playbook Name**: This can be left as "**AS-Checkmarx-SAST-Ingestion**" or you may change it.
* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](#create-an-azure-key-vault-secret).
* **Key Vault Secret Name**: Enter the name of the Key Vault secret created in [Create an Azure Key Vault Secret](#create-an-azure-key-vault-secret).
* **Grant Type**: Enter the OAuth grant type for Checkmarx authentication. Use `client_credentials` (default) for client ID and secret, or `refresh_token` for refresh token authentication. See [Checkmarx API Permissions](#checkmarx-api-permissions) for details.
* **Checkmarx IAM Base Url**: Enter the IAM base URL for your Checkmarx region referenced in [Checkmarx API Permissions](#checkmarx-api-permissions).
* **Checkmarx AST Base Url**: Enter the AST base URL for your Checkmarx region referenced in [Checkmarx API Permissions](#checkmarx-api-permissions).
* **Checkmarx Tenant**: Enter your Checkmarx tenant/realm name (this appears in your Checkmarx URL and authentication settings).
* **Checkmarx Client Id**: Enter your Checkmarx OAuth Client ID (e.g., "**ast-app**").
* **DCE Logs Ingestion Endpoint**: Enter the Logs Ingestion Endpoint URL from the DCE created previously.
* **DCR Immutable Id**: Enter the Immutable ID from the SAST DCR created previously.
* **Batch Size**: Enter the number of SAST results to send per request to the DCR ingestion endpoint. The DCR API enforces a 1 MB maximum payload size; this parameter controls how results are chunked to stay under that limit. A value of **200** is recommended for most environments.

Towards the bottom, click on "**Review + create**".

![Checkmarx_SAST_Deploy_1](Images/Checkmarx_SAST_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Checkmarx_SAST_Deploy_2](Images/Checkmarx_SAST_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![Checkmarx_SAST_Deploy_3](Images/Checkmarx_SAST_Deploy_3.png)

#

### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the playbook must be granted access to the Key Vault storing your Checkmarx secret.

From the Key Vault page menu, click the "**Access configuration**" menu option under the "**Settings**" section.

![Checkmarx_SAST_Key_Vault_Access_1](Images/Checkmarx_SAST_Key_Vault_Access_1.png)

> [!NOTE]
> Azure Key Vault supports two permission models for granting data plane access: **Azure role-based access control (Azure RBAC)** and **Vault access policy**. Azure RBAC is the **recommended** authorization system, as indicated in the Azure portal. Vault access policy is considered **legacy** by Microsoft. Both methods are documented below; choose the option that matches your Key Vault's configuration.

#

#### Option 1: Azure Role-Based Access Control (Recommended)

From the Key Vault "**Access control (IAM)**" page, click "**Add role assignment**".

![Checkmarx_SAST_Key_Vault_Access_2](Images/Checkmarx_SAST_Key_Vault_Access_2.png)

Select the "**Key Vault Secrets User**" role, then click "**Next**".

![Checkmarx_SAST_Key_Vault_Access_3](Images/Checkmarx_SAST_Key_Vault_Access_3.png)

Select "**Managed identity**" and click "**Select members**". Search for "**AS-Checkmarx-SAST-Ingestion**" (or the playbook name you used) and click the option that appears. Click "**Select**", then "**Next**" towards the bottom of the page.

![Checkmarx_SAST_Key_Vault_Access_4](Images/Checkmarx_SAST_Key_Vault_Access_4.png)

Navigate to the "**Review + assign**" section and click "**Review + assign**".

![Checkmarx_SAST_Key_Vault_Access_5](Images/Checkmarx_SAST_Key_Vault_Access_5.png)

#

#### Option 2: Vault Access Policy (Legacy)

If your Key Vault is configured to use "**Vault access policy**", access must be granted through the "**Access policies**" page.

Navigate to the "**Access policies**" menu option, found under the "**Settings**" section on the Key Vault page menu.

Click "**Create**".

![Checkmarx_SAST_Key_Vault_Access_6](Images/Checkmarx_SAST_Key_Vault_Access_6.png)

In the "**Permissions**" tab, select the "**Get**" checkbox under the "**Secret permissions**" section. Click "**Next**".

![Checkmarx_SAST_Key_Vault_Access_7](Images/Checkmarx_SAST_Key_Vault_Access_7.png)

In the "**Principal**" tab, paste "**AS-Checkmarx-SAST-Ingestion**" (or the playbook name you used) into the search box and select the option that appears. Click "**Next**".

![Checkmarx_SAST_Key_Vault_Access_8](Images/Checkmarx_SAST_Key_Vault_Access_8.png)

Navigate to the "**Review + create**" tab and click "**Create**".

#

### Granting Access to the Data Collection Rule

The playbook must be granted access to the SAST Data Collection Rule to publish metrics.

From the SAST DCR "**Access control (IAM)**" page, click "**Add role assignment**".

![Checkmarx_SAST_DCR_Access_1](Images/Checkmarx_SAST_DCR_Access_1.png)

Select the "**Monitoring Metrics Publisher**" role, then click "**Next**".

![Checkmarx_SAST_DCR_Access_2](Images/Checkmarx_SAST_DCR_Access_2.png)

Select "**Managed identity**" and click "**Select members**". Search for "**AS-Checkmarx-SAST-Ingestion**" (or the playbook name you used) and click the option that appears. Click "**Select**", then "**Next**" towards the bottom of the page.

![Checkmarx_SAST_DCR_Access_3](Images/Checkmarx_SAST_DCR_Access_3.png)

Navigate to the "**Review + assign**" section and click "**Review + assign**".

![Checkmarx_SAST_DCR_Access_4](Images/Checkmarx_SAST_DCR_Access_4.png)

> [!IMPORTANT]
> The role assignment may take some time to propagate. If your Logic App is not running successfully immediately after the role assignment, please allow up to 10 minutes before retrying.

#

### Initial Run

This playbook runs once daily, collecting completed Checkmarx SAST scan findings from the previous 24 hours and ingesting them into Microsoft Sentinel.

This playbook is deployed in a **Disabled** state. After completing all role assignments, navigate to the Logic App overview page and click "**Enable**" to activate the playbook. Then click "**Run**" > "**Run**" to execute the initial run.

![Checkmarx_SAST_Initial_Run_1](Images/Checkmarx_SAST_Initial_Run_1.png)

Click on the run to view the execution details. Verify that all steps completed successfully, particularly the "**HTTP - Send SAST Results to DCR**" step.

![Checkmarx_SAST_Initial_Run_2](Images/Checkmarx_SAST_Initial_Run_2.png)

#

### Viewing Custom Logs

After the initial run has been completed, navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

From there, select the workspace your deployed logic app references and click "**Logs**" in the left-hand menu blade. Expand "**Custom Logs**". Here, you should see the **CheckmarxSASTFindings_CL** table.

> [!NOTE]
> It may take several minutes for the table to appear and data to be visible after the initial run. If the logs are not yet visible, try querying them periodically.

![Checkmarx_SAST_Custom_Logs_1](Images/Checkmarx_SAST_Custom_Logs_1.png)

#### Sample KQL Queries

**View all SAST findings:**
```kql
CheckmarxSASTFindings_CL
| project TimeGenerated, QueryName, Severity, LanguageName, SourceFileName, SourceLine, State, Status
| order by TimeGenerated desc
```

**High severity findings:**
```kql
CheckmarxSASTFindings_CL
| where Severity == "HIGH"
| project TimeGenerated, QueryName, LanguageName, SourceFileName, SourceLine, CvssScore, State
| order by CvssScore desc
```

**Findings by severity:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d)
| summarize Count = count() by Severity
| order by Count desc
```

**Findings by language:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d)
| summarize Count = count() by LanguageName
| order by Count desc
```

**Top vulnerability types:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d)
| summarize Count = count() by QueryName, Severity
| order by Count desc
```

**New vs. recurrent findings:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d)
| summarize Count = count() by Status
| order by Count desc
```

**Findings by source file:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d)
| summarize
    FindingCount = count(),
    HighSeverity = countif(Severity == "HIGH"),
    MediumSeverity = countif(Severity == "MEDIUM")
    by SourceFileName
| order by FindingCount desc
```

**CVSS score distribution:**
```kql
CheckmarxSASTFindings_CL
| where TimeGenerated > ago(7d) and isnotnull(CvssScore)
| summarize Count = count() by bin(CvssScore, 1.0)
| order by CvssScore desc
```

#

### Data Schema

#### CheckmarxSASTFindings_CL Table

| Column | Type | Description |
| --- | --- | --- |
| TimeGenerated | datetime | Time the record was ingested |
| ResultHash | string | Unique hash for the result |
| QueryID | string | ID of the query that found the vulnerability |
| QueryName | string | Name of the vulnerability query |
| LanguageName | string | Programming language |
| VulnerabilityGroup | string | Category/group of the vulnerability |
| CweID | int | Common Weakness Enumeration ID |
| Severity | string | Severity level (HIGH, MEDIUM, LOW, INFO) |
| CvssScore | real | CVSS vulnerability score |
| SimilarityID | int | ID for similar vulnerabilities |
| State | string | Current state (TO_VERIFY, CONFIRMED, etc.) |
| Status | string | Status (NEW, RECURRENT, FIXED) |
| ConfidenceLevel | int | Confidence level of the finding |
| FirstFoundAt | datetime | When the vulnerability was first found |
| FoundAt | datetime | When the vulnerability was found in this scan |
| FirstScanID | string | ID of the first scan that found this |
| Compliances | string | Comma-separated list of compliance frameworks |
| SourceFileName | string | Source file containing the vulnerability |
| SourceLine | int | Line number in the source file |
| SourceColumn | int | Column number in the source file |
| NodeCount | int | Number of nodes in the vulnerability path |
| NodesJson | string | JSON representation of the data flow nodes |
| ScanID | string | ID of the scan |

#

### Role Assignments Summary

The following role assignments are required for the Logic App to function:

| Resource | Role | Purpose |
| --- | --- | --- |
| Azure Key Vault | **Key Vault Secrets User** | Allows the Logic App to retrieve the Checkmarx secret |
| SAST Data Collection Rule | **Monitoring Metrics Publisher** | Allows the Logic App to send SAST data to the DCR ingestion endpoint |

#

### Troubleshooting

**Logic App fails at "Get_secret" step:**
* Verify the Key Vault name and secret name are correct.
* Ensure the Logic App managed identity has the "Key Vault Secrets User" role on the Key Vault (RBAC) or appropriate access policy (legacy).

**Logic App fails at "HTTP - Get Token" step:**
* Verify the Checkmarx IAM Base URL matches your Checkmarx region.
* Verify the Checkmarx Tenant name is correct.
* If using `client_credentials`, verify the client secret stored in Key Vault is valid.
* If using `refresh_token`, verify the refresh token stored in Key Vault is valid and not expired.
* Verify the Grant Type parameter matches the type of credential stored in Key Vault.
* Check that the Checkmarx IAM endpoint is accessible.

**Logic App fails at "HTTP - Get Scans" step:**
* Verify the Checkmarx AST Base URL matches your Checkmarx region.
* Verify the access token was successfully obtained.
* Check that the Checkmarx API endpoint is accessible.
* Verify the API permissions for your Checkmarx client.
* Ensure there are completed scans within the past 24 hours.

**Logic App fails at "HTTP - Get SAST Results Page" step:**
* Verify the scan ID was successfully retrieved from the previous step.
* Check that the SAST results endpoint is accessible.

**Logic App fails at "HTTP - Send SAST Batch to DCR" step with "ContentLengthLimitExceeded":**
* The DCR ingestion API enforces a 1 MB maximum payload size per request. This error indicates the batch size is too large for the SAST results being sent. Reduce the **Batch Size** deployment parameter (default: 200) and redeploy the Logic App.

**Logic App fails at "HTTP - Send SAST Batch to DCR" step with 403:**
* Ensure the Logic App managed identity has the "Monitoring Metrics Publisher" role on the SAST DCR.
* Wait up to 10 minutes for role assignment propagation.

**Logic App fails at DCR step with 404:**
* Verify the DCE Logs Ingestion Endpoint URL is correct.
* Verify the DCR Immutable ID is correct.

**No data appearing in Log Analytics:**
* Wait several minutes after the first successful run.
* Verify the custom table was created successfully.
* Verify there are completed SAST scans in your Checkmarx tenant within the past 24 hours.
* Check the Logic App run history for any errors.

**Condition step is skipped:**
* This is normal behavior if no SAST findings are available for the most recent scan.
* Verify you have completed SAST scans in Checkmarx.
