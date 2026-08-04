# AS-Checkmarx-Audit-Ingestion

Author: Accelerynt

For any technical questions, please contact [info@accelerynt.com](mailto:info@accelerynt.com)

This playbook will create a unidirectional integration with Microsoft Sentinel. It will pull Checkmarx audit events into a Microsoft Sentinel custom log table on a daily schedule where they can be tracked, queried, and correlated with other security data. This uses Data Collection Rules (DCR), Data Collection Endpoints (DCE), and custom log tables.

![Checkmarx_Audit_Integration_Demo_1](Images/Checkmarx_Audit_Integration_Demo_1.png)

> [!NOTE]
> Estimated Time to Complete: 15 minutes

> [!TIP]
> Required deployment variables are noted throughout. Reviewing the deployment page and filling out fields as you proceed is recommended.

> [!NOTE]
> This playbook handles **audit events only**. For SAST findings ingestion, see the [AS-Checkmarx-SAST-Ingestion](https://github.com/Accelerynt-Security/AS-Checkmarx-SAST-Ingestion) playbook.

#

### Requirements

The following items are required under the template settings during deployment:

* **Checkmarx Client Secret or Refresh Token** - a client secret (recommended) or refresh token with permissions to query audit events from your Checkmarx One instance. [Documentation link](#checkmarx-api-permissions)
* **Checkmarx IAM Base URL** - the base URL for Checkmarx IAM authentication based on your region (e.g., `https://us.iam.checkmarx.net`). [Documentation link](#checkmarx-api-permissions)
* **Checkmarx AST Base URL** - the base URL for Checkmarx AST API calls based on your region (e.g., `https://us.ast.checkmarx.net`). [Documentation link](#checkmarx-api-permissions)
* **Checkmarx Tenant** - your Checkmarx tenant/realm name used in the authentication URL. [Documentation link](#checkmarx-api-permissions)
* **Azure Key Vault Secret** - this will be used to store your Checkmarx client secret or refresh token. [Documentation link](#create-an-azure-key-vault-secret)
* **Log Analytics Workspace** - the name, location, and resource ID of the Log Analytics workspace that the Checkmarx data will be sent to. [Documentation link](#log-analytics-workspace)

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

![Checkmarx_Audit_Integration_Key_Vault_1](Images/Checkmarx_Audit_Integration_Key_Vault_1.png)

Choose a name for the secret, such as "**checkmarx-integration-secret**", and enter your Checkmarx client secret or refresh token in the "**Value**" field. All other settings can be left as is. Click "**Create**".

![Checkmarx_Audit_Integration_Key_Vault_2](Images/Checkmarx_Audit_Integration_Key_Vault_2.png)

> [!IMPORTANT]
> This deployment uses the **Azure role-based access control (RBAC)** permission model. Key Vault Access Policies will need to be set up manually post-deployment if this legacy permission model is still in use in your tenant. To switch a Key Vault from legacy Access Policies to the recommended RBAC, navigate to the "**Access configuration**" menu option under the "**Settings**" section and select "**Azure role-based access control**". Existing secrets, keys, and certificates are not affected by this change.

#### Log Analytics Workspace

Navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the workspace that the Checkmarx data will be sent to, and take note of the following values:

![Checkmarx_Audit_Integration_Log_Analytics_Workspace_1](Images/Checkmarx_Audit_Integration_Log_Analytics_Workspace_1.png)

From the left menu blade, click **Overview** and take note of the **Name** and **Location** field values. These will be needed during deployment.

![Checkmarx_Audit_Integration_Log_Analytics_Workspace_2](Images/Checkmarx_Audit_Integration_Log_Analytics_Workspace_2.png)

From the left menu blade, click **Overview** and take note of the **Resource ID** shown in the JSON View. This will also be needed during deployment.

![Checkmarx_Audit_Integration_Log_Analytics_Workspace_3](Images/Checkmarx_Audit_Integration_Log_Analytics_Workspace_3.png)

#

### Deployment

This single deployment creates the custom log table, Data Collection Endpoint (DCE), Data Collection Rule (DCR), Key Vault API connection, Logic App, and all required role assignments.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-Audit-Ingestion%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Checkmarx-Audit-Ingestion%2Fazuredeploy.json)

Click the "**Deploy to Azure**" button and it will bring you to the custom deployment template.

In the **Project details** section:

* Select the **Subscription** and **Resource group** from the dropdown boxes you would like the playbook deployed to.

In the **Instance details** section:

* **Playbook Name**: This can be left as "**AS-Checkmarx-Audit-Ingestion**" or you may change it.
* **Workspace Name**: Enter the **Name** of your Log Analytics workspace referenced in [Log Analytics Workspace](#log-analytics-workspace).
* **Workspace Resource Id**: Enter the full **Resource ID** of your Log Analytics workspace.
* **Workspace Location**: Enter the **Location** of your Log Analytics workspace. Note that this may differ from the selected Resource group's region; the DCE and DCR will be deployed to the workspace's region.
* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](#create-an-azure-key-vault-secret).
* **Key Vault Resource Group**: Enter the resource group containing the Key Vault.
* **Key Vault Secret Name**: This can be left as "**checkmarx-integration-secret**" or changed to match the secret name you used.
* **Data Collection Endpoint Name**: This can be left as the default. Override it only if you are deploying multiple ingestion playbooks into the same resource group and need to avoid a name collision.
* **Data Collection Rule Name**: This can be left as the default. Override it only if you are deploying multiple ingestion playbooks into the same resource group and need to avoid a name collision.
* **Checkmarx IAM Base Url**: Enter the IAM base URL for your Checkmarx region referenced in [Checkmarx API Permissions](#checkmarx-api-permissions).
* **Checkmarx AST Base Url**: Enter the AST base URL for your Checkmarx region referenced in [Checkmarx API Permissions](#checkmarx-api-permissions).
* **Checkmarx Tenant**: Enter your Checkmarx tenant/realm name (this appears in your Checkmarx URL and authentication settings).
* **Checkmarx Client Id**: Enter your Checkmarx OAuth Client ID (e.g., "**ast-app**").
* **Grant Type**: Select the OAuth grant type for Checkmarx authentication. Use `client_credentials` for client ID and secret, or `refresh_token` for refresh token authentication. See [Checkmarx API Permissions](#checkmarx-api-permissions) for details.
* **Lookback Days**: Number of days prior to each run to pull audit events from. Default is **2**. For the initial backfill, set this higher (e.g., **180**, or up to **365**, the Checkmarx retention maximum) to ingest historical events, then reduce to **2** for steady-state daily operation. See the [Checkmarx Audit Trail API documentation](https://docs.checkmarx.com/en/34965-156810-audit-trail-api.html) for endpoint specifics. This can be changed later by editing the **FromDate** variable in the Logic App's **Initialize_Variables** action.

Towards the bottom, click on "**Review + create**".

![Checkmarx_Audit_Integration_Deploy_1](Images/Checkmarx_Audit_Integration_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![Checkmarx_Audit_Integration_Deploy_2](Images/Checkmarx_Audit_Integration_Deploy_2.png)

The resources should take around two minutes to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.

![Checkmarx_Audit_Integration_Deploy_3](Images/Checkmarx_Audit_Integration_Deploy_3.png)

#

### Role Assignments

The following role assignments are created automatically by this deployment:

| Resource | Role | Purpose |
| --- | --- | --- |
| Azure Key Vault | **Key Vault Secrets User** | Allows the Logic App to retrieve the Checkmarx secret |
| Audit Data Collection Rule | **Monitoring Metrics Publisher** | Allows the Logic App to send audit data to the DCR ingestion endpoint |

> [!IMPORTANT]
> The role assignments may take some time to propagate. If your Logic App is not running successfully immediately after deployment, please allow up to 10 minutes before retrying.

> [!NOTE]
> The user performing the deployment must hold the **Owner** or **User Access Administrator** role on the resource group, Key Vault, and workspace being targeted. Most customers deploying Sentinel playbooks already have this level of access.

#

### Post-Deployment Tuning

A small number of operational values are baked into the Logic App definition rather than exposed as deployment parameters, because they are constrained by the Checkmarx API contract rather than by customer choice. They are not expected to need changes, but the edit locations are documented here in case they ever do (e.g., if Checkmarx updates an API limit).

To edit these, navigate to the deployed Logic App, open the **Code view** from the left menu, and modify the value in place. Save when done.

| Value | Default | Location in Logic App code | When to change |
| --- | --- | --- | --- |
| Audit page size | `1000` | `Initialize_Variables` action → `AuditPageSize` variable `value` | Only if Checkmarx changes the documented maximum for `/api/audit-events`. The current API maximum is 1000. |

#

### Initial Run

This playbook runs once daily, paginating the Checkmarx `/api/audit-events/` endpoint and ingesting events into Microsoft Sentinel. Each run retrieves events from the configured lookback window (default **2** days). Because consecutive runs overlap, the same event will appear multiple times in the table; the **EventID** column lets you collapse to one row per event at query time when desired.

This playbook is deployed in a **Disabled** state. After waiting for role assignments to propagate, navigate to the Logic App overview page and click "**Enable**" to activate the playbook. Then click "**Run**" > "**Run**" to execute the initial run.

Click on the run to view the execution details. Verify that all steps completed successfully, particularly the "**HTTP - Send Audit Events to DCR**" step inside the `Until_Paginate_Audit_Logs` loop.

#

### Viewing Custom Logs

After the initial run has been completed, navigate to the Log Analytics Workspace page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

From there, select the workspace your deployed logic app references and click "**Logs**" in the left-hand menu blade. Expand "**Custom Logs**". Here, you should see the **CheckmarxAuditEvents_CL** table.

> [!NOTE]
> It may take several minutes for the table to appear and data to be visible after the initial run. If the logs are not yet visible, try querying them periodically.

![Checkmarx_Audit_Custom_Logs_1](Images/Checkmarx_Audit_Custom_Logs_1.png)

> [!IMPORTANT]
> The Checkmarx audit-events endpoint returns the full set of currently-available events on each request. The playbook ingests this full set on every run, so the same event may appear multiple times in the table across runs. **Use the `EventID` column to deduplicate rows at query time.** The sample queries below show the standard pattern: `summarize arg_max(TimeGenerated, *) by EventID`. Consider saving the dedup pattern as a workspace function (e.g., `CheckmarxAuditEvents`) so downstream queries can reference deduplicated data without repeating the boilerplate.

#### Sample KQL Queries

**View all audit events (deduplicated):**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| project EventDate, EventType, ActionType, Username, IpAddress, Status, TenantID
| order by EventDate desc
```

**User login activity:**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where ActionType == "login"
| project EventDate, Username, IpAddress, Status
| order by EventDate desc
```

**Failed login attempts:**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where ActionType == "login" and Status != "OK"
| project EventDate, Username, IpAddress, Status
| order by EventDate desc
```

**Activity by user (last 7 days):**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventDate > ago(7d)
| summarize ActionCount = count() by Username, ActionType
| order by ActionCount desc
```

**Activity by IP address (last 7 days):**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventDate > ago(7d)
| summarize Count = count(), Users = make_set(Username) by IpAddress
| order by Count desc
```

**Audit events timeline:**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventDate > ago(7d)
| summarize Count = count() by bin(EventDate, 1h), ActionType
| render timechart
```

**User activity summary:**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventDate > ago(7d)
| summarize
    EventCount = count(),
    UniqueActions = dcount(ActionType),
    UniqueIPs = dcount(IpAddress),
    LastSeen = max(EventDate)
    by Username
| order by EventCount desc
```

**Login activity by IP address:**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventType has "login"
| summarize
    LoginCount = count(),
    UniqueUsers = dcount(Username),
    LastLogin = max(EventDate)
    by IpAddress
| order by LoginCount desc
```

**Sensitive event types (creates, deletes, role changes):**
```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventDate > ago(30d)
| where ActionType in ("create", "delete", "assign", "update")
| project EventDate, EventType, ActionType, ActionUserId, AuditResource, DataJson
| order by EventDate desc
```

#

### Data Schema

#### CheckmarxAuditEvents_CL Table

| Column | Type | Description |
| --- | --- | --- |
| TimeGenerated | datetime | Time the record was ingested |
| EventID | string | Unique identifier for the audit event. Used as the deduplication key. |
| EventDate | datetime | Date and time of the audit event |
| EventType | string | Type of audit event (e.g., `users.login`, `scans.create`) |
| AuditResource | string | Resource being audited (e.g., `users`, `scans`, `projects`) |
| ActionType | string | Type of action performed (e.g., `login`, `create`, `update`, `delete`) |
| ActionUserId | string | User ID who performed the action |
| IpAddress | string | IP address of the user (empty for events without an originating IP) |
| TenantID | string | Tenant ID for the Checkmarx instance |
| UserId | string | User ID from the data payload (login events) |
| Status | string | Status of the action (login events; e.g., `OK`) |
| Username | string | Username who performed the action (login events) |
| DataJson | string | Full JSON data payload. Fields vary by event type. |

> [!NOTE]
> The `UserId`, `Status`, and `Username` columns are extracted from the event's `data` object and are primarily populated for login events. For other event types (e.g., `scans.create`, `environment.delete`, `applications.update`), the event-specific fields are preserved in the `DataJson` column and can be extracted in KQL using `parse_json(DataJson)`.

#### Extracting fields from DataJson

The `data` object varies by event type. Use `parse_json` to extract event-specific fields:

```kql
CheckmarxAuditEvents_CL
| summarize arg_max(TimeGenerated, *) by EventID
| where EventType == "scans.create"
| extend ScanID = tostring(parse_json(DataJson).scanID),
         Initiator = tostring(parse_json(DataJson).initiator)
| project EventDate, ScanID, Initiator
```

#

### Troubleshooting

**Deployment fails at the Key Vault role assignment:**
* Verify **Key Vault Resource Group** is correct.
* Verify the Key Vault is configured for **Azure RBAC**. If it's on the legacy Access Policy model, the automated role assignment won't apply; either switch to RBAC from the Key Vault's "Access configuration" blade and redeploy, or grant the Logic App's managed identity **Get** secret access manually via an Access Policy.
* The deploying principal needs `Microsoft.Authorization/roleAssignments/write` on the Key Vault (e.g., Owner or User Access Administrator).

**Logic App fails at "Get_secret" step:**
* Verify the Key Vault name and secret name are correct.
* Role assignment may still be propagating. Wait up to 10 minutes after deployment before retrying.

**Logic App fails at "HTTP - Refresh Token" step:**
* Verify the Checkmarx IAM Base URL matches your Checkmarx region.
* Verify the Checkmarx Tenant name is correct.
* If using `client_credentials`, verify the client secret stored in Key Vault is valid.
* If using `refresh_token`, verify the refresh token stored in Key Vault is valid and not expired.
* Verify the Grant Type parameter matches the type of credential stored in Key Vault.
* Check that the Checkmarx IAM endpoint is accessible.

**Logic App fails at "HTTP - Get Audit Events Page" step:**
* Verify the Checkmarx AST Base URL matches your Checkmarx region.
* Verify the access token was successfully obtained.
* Check that the Checkmarx API endpoint is accessible.
* Verify the API permissions for your Checkmarx client.

**Logic App fails at "HTTP - Send Audit Events to DCR" step with 403:**
* Wait up to 10 minutes for the Monitoring Metrics Publisher role assignment to propagate.

**Logic App fails at DCR step with 404:**
* The DCE endpoint URL and DCR immutable ID are resolved at deploy time from the resources created by this template, so 404s should not occur unless the DCE or DCR was deleted out-of-band. Redeploy the template to restore them.

**No data appearing in Log Analytics:**
* Wait several minutes after the first successful run, since ingestion is asynchronous.
* Verify the **CheckmarxAuditEvents_CL** table exists under **Custom Logs** in the workspace.
* Check the Logic App run history for any errors.

**Pagination loop reaches its iteration limit:**
* The loop is bounded by a 15-minute timeout and a maximum iteration count as safety nets. If runs hit these limits, the audit event volume in your tenant may exceed what one page-by-page sweep can complete in 15 minutes. Inspect the run to see how many pages were retrieved and contact support to evaluate options for very large tenants.

**Only one page of events ingested when more should exist:**
* The playbook follows the API's HATEOAS-style pagination in two parts: `Compose_NextRelativeHref` extracts the relative path from `Links._links.next.href` in each response, and `Set_NextPageUrl` prepends the Checkmarx AST base URL to build the absolute URL for the next request. To diagnose a premature loop exit, drill into a run of `Compose_NextRelativeHref` and check its output. If the output is empty when more pages should exist, the API response structure has changed. Inspect the actual response body of `HTTP - Get Audit Events Page` and update the extraction expression to match the path where `next.href` actually lives. If the output is a relative path but `Set_NextPageUrl` still produces an empty result, verify the `CheckmarxASTBaseUrl` variable is populated correctly.

**Duplicate rows in the table:**
* This is expected. Each run pulls events from the configured lookback window, so events within the overlap between consecutive runs will appear multiple times in the table. Always deduplicate at query time using `summarize arg_max(TimeGenerated, *) by EventID` (see the sample queries above). Consider saving a workspace function that wraps this pattern so downstream queries don't need to repeat it.

**Condition step is skipped for a page:**
* This is normal behavior if the page returned zero events (e.g., the very last page when the total event count is an exact multiple of the page size). The condition guards against ingesting empty result sets.