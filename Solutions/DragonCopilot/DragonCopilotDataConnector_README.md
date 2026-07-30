# Microsoft Dragon Copilot — Microsoft Sentinel Data Connector

## Overview

Microsoft Dragon Copilot is an AI-powered clinical assistant that captures and processes clinician interactions to generate structured clinical documentation and activity records. It leverages conversational, ambient, and generative AI to streamline clinical workflows and surface actionable insights for healthcare professionals — including clinicians, nurses, and radiologists.

This connector ingests Dragon Copilot **audit and activity logs** into Microsoft Sentinel via the Office Management API. The logs are stored in the standard **`DragonCopilot`** table in your Log Analytics workspace and enable:

- **Security monitoring** — detect anomalous access patterns and suspicious activity.
- **Compliance auditing** — maintain audit trails for HIPAA and organizational policies.
- **Operational visibility** — track usage, sessions, and system actions across clinical workflows.

> **Note:** This connector is currently in **Preview**.

---

## Prerequisites

Before deploying the connector, ensure you have the following:

| Requirement | Details |
|---|---|
| **Microsoft Sentinel workspace** | An active Log Analytics workspace with Microsoft Sentinel enabled. |
| **Permissions** | `Security Administrator` or `Global Administrator` role on the tenant. Read, write, and delete permissions on the Log Analytics workspace. |
| **Dragon Copilot license** | An active Microsoft Dragon Copilot subscription with audit logging enabled in your tenant. |
| **Azure subscription** | An Azure subscription linked to the tenant where Dragon Copilot is provisioned. |

---

## Deployment Steps (ARM Template — Current)

The Dragon Copilot connector is not yet available in the Microsoft Sentinel Content Hub. During this initial phase, the connector can be deployed by running the provided ARM template directly.

### Step 1 — Deploy the ARM Template

**Option A — Azure Portal (Custom Deployment):**

1. In the [Azure portal](https://portal.azure.com), search for **Deploy a custom template** and select it.
2. Click **Build your own template in the editor**.
3. Load the `mainTemplate.json` file provided to you (paste or upload).
4. Click **Save**.
5. Fill in the required parameters:

   | Parameter | Description |
   |---|---|
   | **Subscription** | The Azure subscription where your Sentinel workspace resides. |
   | **Resource Group** | The resource group containing your Log Analytics workspace. |
   | **Workspace** | The name of your Log Analytics workspace with Microsoft Sentinel enabled. |
   | **Workspace Location** | The region of your Log Analytics workspace (e.g., `eastus`, `westeurope`). |

6. Click **Review + create** → **Create**.
7. Wait for the deployment to complete (typically 1–2 minutes).

**Option B — Azure CLI:**

```bash
az deployment group create \
  --resource-group <ResourceGroupName> \
  --template-file mainTemplate.json \
  --parameters workspace=<WorkspaceName> workspace-location=<Region>
```

**Option C — PowerShell:**

```powershell
New-AzResourceGroupDeployment `
  -ResourceGroupName "<ResourceGroupName>" `
  -TemplateFile "mainTemplate.json" `
  -workspace "<WorkspaceName>" `
  -workspace-location "<Region>"
```

The deployment creates the following resources in your workspace:

| Resource | Purpose |
|---|---|
| **Data Connector Definition** (`DragonCopilot`) | Registers the connector in the Sentinel Data Connectors gallery. |
| **Standard Table** (`DragonCopilot`) | Log Analytics table that stores the ingested audit records. |
| **Data Collection Rule** (`DragonCopilot-DCR`) | Routes data from the Office Management API to the standard table. |
| **Polling Configuration** (`DragonCopilotPolling`) | Defines the polling schedule and retry behavior for data ingestion. |

### Step 2 — Connect the Data Connector

1. In Microsoft Sentinel, go to **Data connectors** (under *Configuration*).
2. Search for **Dragon Copilot** and select it.
3. Click **Open connector page**.
4. Review the description and prerequisites.
5. Click the **Connect** button.
6. Wait for the status to change to **Connected** (this may take a few minutes).

### Step 3 — Verify Data Ingestion

After connecting, allow **15–30 minutes** for initial data to arrive. Then verify:

1. Navigate to **Logs** in your Sentinel workspace.
2. Run the following KQL query:

   ```kql
   DragonCopilot
   | sort by TimeGenerated desc
   | take 10
   ```

3. Confirm that records are appearing with expected fields such as `Operation`, `UserId`, `RecordType`, and `ResultStatus`.

You can also verify from the connector page — the **Data received** graph should show incoming data.

---

## Data - `DragonCopilot`

The table contains four categories of records, identified by `RecordType`:

| RecordType | Name | Description |
|---|---|---|
| **454** | Admin | Administrative operations (configuration changes, policy updates). |
| **468** | Access | User authentication and access events. |
| **469** | ClinicalData | Clinical data generation and interaction events. |
| **470** | Session | Session lifecycle events (start, end, disconnect). |

---

## Sample KQL Queries

### All Dragon Copilot logs (most recent first)

```kql
DragonCopilot
| sort by TimeGenerated desc
```

### Failed operations

```kql
DragonCopilot
| where ResultStatus == "Failed"
| summarize FailureCount = count() by Operation, UserId
| order by FailureCount desc
```

### Access events by authentication method

```kql
DragonCopilot
| where RecordType == 468
| summarize Count = count() by AuthenticationMethod, HostType
| order by Count desc
```

---

## Migrating from the preview custom-table deployment

If you previously deployed the preview connector that wrote to `DragonCopilot_CL`, disconnect it before enabling this connector to avoid duplicate data ingestion and unnecessary costs. Historical data remains in the custom table until you explicitly remove it.

### Step 1 — Disconnect the Custom Connector

1. In Microsoft Sentinel, go to **Data connectors**.
2. Search for **Dragon Copilot** and select the custom connector.
3. Click **Open connector page**.
4. Click **Disconnect**.
5. Confirm the disconnection.

### Step 2 — Delete the ARM Deployment Resources

Since the connector was deployed via ARM template (not Content Hub), you need to manually remove the deployed resources.

**Delete the Data Connector:**

1. In Microsoft Sentinel, go to **Data connectors**.
2. Find the disconnected **Dragon Copilot** connector.
3. If a delete option is available, use it. Otherwise, use the CLI commands below.

**Delete the Data Collection Rule:**

1. In the Azure portal, go to **Monitor** → **Data Collection Rules**.
2. Search for `DragonCopilot-DCR`.
3. Select it and click **Delete**.

**Delete the Custom Table** (optional — only if you no longer need historical data):

*Option A — Azure Portal:*

1. Navigate to your **Log Analytics workspace**.
2. Go to **Settings** → **Tables**.
3. Search for `DragonCopilot_CL`.
4. Click the context menu (**...**) and select **Delete**.

*Option B — Azure CLI:*

```bash
az monitor log-analytics workspace table delete \
  --resource-group <ResourceGroupName> \
  --workspace-name <WorkspaceName> \
  --name DragonCopilot_CL
```

*Option C — PowerShell:*

```powershell
Remove-AzOperationalInsightsTable `
  -ResourceGroupName "<ResourceGroupName>" `
  -WorkspaceName "<WorkspaceName>" `
  -TableName "DragonCopilot_CL"
```

> **Important:** Deleting the table permanently removes all historical data. If you need to retain the data for compliance or investigation purposes, export it first or adjust the retention period before deleting.

### Step 3 - Install the Standard Connector from Content Hub

1. In Microsoft Sentinel, go to **Content hub** (under *Content management*).
2. Search for **Dragon Copilot**.
3. Select the solution and click **Install / Update**.
4. Choose the target **Subscription**, **Resource Group**, and **Workspace**, then click **Review + create** → **Create**.

### Step 4 - Connect the Standard Connector

1. Go to **Data connectors** in Microsoft Sentinel.
2. Locate the new standard **Dragon Copilot** connector (built-in).
3. Click **Open connector page** and follow the on-screen instructions to connect.
4. Verify data is flowing into the new standard table.

---

## Troubleshooting

| Issue | Resolution |
|---|---|
| Connector shows **Disconnected** | Verify that Dragon Copilot audit logging is enabled in your tenant and that you have the required permissions. Re-click **Connect**. |
| No data in `DragonCopilot` | Allow up to 30 minutes for initial ingestion. Check that the DCR and Data Collection Endpoint are healthy under **Monitor** -> **Data Collection Rules**. |
| Permission errors during install | Ensure you have `Security Administrator` or `Global Administrator` role, plus workspace read/write/delete permissions. |

---

