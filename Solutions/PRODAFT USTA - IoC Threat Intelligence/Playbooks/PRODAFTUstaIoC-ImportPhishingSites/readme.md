# PRODAFTUstaIoC-ImportPhishingSites

Hourly import playbook for the **phishing-sites** USTA IoC feed. Each run resumes from a
**watermark** — the newest already-imported indicator's `created` time — maps each new record
to a STIX 2.1 indicator, and uploads them to Microsoft Sentinel Threat Intelligence (Upload
STIX Objects API) using its **system-assigned managed identity**. The feed has no expiry, so a
validity window (`ValidityDays`, default 365 — one year) is synthesized from each site's `created` date.
Indicators appear in the Threat Intelligence blade / `ThreatIntelIndicators` table with
`SourceSystem == "PRODAFT USTA - Phishing Sites"`.

## How the fetch window works

At the start of every run the playbook queries the `ThreatIntelIndicators` table for
`max(Created)` of `SourceSystem == "PRODAFT USTA - Phishing Sites"` and uses that (minus a
5-minute safety overlap) as the `start=` of the fetch. Because a record only lands in that
table after a **successful** upload, a failed run does not advance the watermark: the next run
re-reads the same value and retries the missed window, so **no indicators are skipped on
failure**. If the table has no such indicators yet (first run), it falls back to `LookBackHours`.
The watermark query runs through the **Azure Monitor Logs** connection (managed-identity auth) using the
same managed identity, but it needs **Log Analytics Reader** on the workspace *in addition to* the **Microsoft Sentinel
Contributor** role used for the upload. Microsoft Sentinel Contributor is not sufficient on its own: it grants
`Microsoft.OperationalInsights/workspaces/*/read`, and an Azure RBAC wildcard of that shape does not
cover the bare `Microsoft.OperationalInsights/workspaces/read` action this connection performs, so the
query fails with `AuthorizationFailed`.

## Resolved IP addresses

When a record carries `ip_addresses`, every address is appended to the **same** indicator's
pattern as its own observation expression — `ipv4-addr:value` or `ipv6-addr:value`, chosen per
address — so the indicator covers the URL/hash and its resolved IPs under one validity window.
Only the **first 10** addresses of a record are included; any beyond that are dropped.

Microsoft Sentinel expands a multi-observation pattern into one `ObservableKey`/`ObservableValue` row per
observable, so those IPs are independently matchable. Note that CDN-fronted hosts resolve to
shared edge addresses, which can produce false positives if you match on IP alone.

## Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `PlaybookName` | no | `PRODAFTUstaIoC-ImportPhishingSites` | Logic App name. |
| `UstaBaseUrl` | no | `https://usta.prodaft.com` | USTA API base URL. |
| `UstaApiKey` | **yes** | — | USTA long-lived API key (secured). |
| `WorkspaceName` | **yes** | — | Name of the Microsoft Sentinel (Log Analytics) workspace that indicators are uploaded to. |
| `WorkspaceResourceGroup` | no | resource group of the deployment | Resource group of the workspace, if it differs from where the playbook is deployed. |
| `LookBackHours` | no | `2` | First-run / fallback look-back window (hours), used only until the first indicator is imported (empty watermark). Afterwards each run resumes from the import watermark. |
| `ValidityDays` | no | `365` | Validity window (days) applied from each site's `created` date, since the feed has no expiry. |

## Deploy — from the portal

1. **Microsoft Sentinel → Content hub → PRODAFT USTA - IoC Threat Intelligence → Manage → Playbook templates**, select **PRODAFT USTA - Import Phishing Sites**, choose **Create playbook**, and supply `UstaApiKey` and `WorkspaceName`. (Or **Automation → Create → Playbook**, then deploy this `azuredeploy.json`.)
2. The playbook is created with a **system-assigned managed identity** automatically.
3. **Grant two roles** on the **Log Analytics workspace → Access control (IAM) → Add → Add role assignment** → **Members: Managed identity** → pick this Logic App by name → **Review + assign**. Assign both **Microsoft Sentinel Contributor** (for the Upload STIX Objects call) and **Log Analytics Reader** (for the watermark query — Microsoft Sentinel Contributor on its own returns `AuthorizationFailed`). **Open IAM on the workspace itself, not on the Logic App** — granting the role while the playbook's own blade is open scopes it to the Logic App (`.../Microsoft.Logic/workflows/...`), which looks correct in the portal but gives the identity no access to the workspace.
4. It now runs hourly. To run immediately, open the Logic App → **Run Trigger → Recurrence**.

## Deploy — via Azure CLI (run from this folder)

```bash
# ---- configuration ----
SUB="<subscription-id>"
RG="<resource-group>"                 # resource group of the Microsoft Sentinel workspace
WS="<workspace-name>"                  # Log Analytics workspace name
USTA_API_KEY="<usta-api-key>"
PLAYBOOK="PRODAFTUstaIoC-ImportPhishingSites"

az account set --subscription "$SUB"

# 1. Deploy the playbook and capture its managed-identity principalId
PRINCIPAL_ID=$(az deployment group create \
  --resource-group "$RG" \
  --template-file azuredeploy.json \
  --parameters PlaybookName="$PLAYBOOK" \
               UstaApiKey="$USTA_API_KEY" \
               WorkspaceName="$WS" \
  --query properties.outputs.playbookPrincipalId.value -o tsv)

# 2. Grant that identity BOTH roles on the workspace:
#      Microsoft Sentinel Contributor -> the Upload STIX Objects call
#      Log Analytics Reader           -> the watermark query (Sentinel Contributor alone is not enough)
for ROLE in "Microsoft Sentinel Contributor" "Log Analytics Reader"; do
  az role assignment create \
    --assignee-object-id "$PRINCIPAL_ID" \
    --assignee-principal-type ServicePrincipal \
    --role "$ROLE" \
    --scope "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS"
done

# 3. (Optional) run once now instead of waiting for the hourly schedule
az rest --method POST \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Logic/workflows/$PLAYBOOK/triggers/Recurrence/run?api-version=2016-10-01"
```

> **RBAC propagation:** the role assignment in step 2 can take a minute to take effect. If the
> first run shows 403 on the Upload STIX Objects action, wait a moment and run the trigger again.

## Verify

```kql
ThreatIntelIndicators
| where SourceSystem == "PRODAFT USTA - Phishing Sites"
| where TimeGenerated > ago(1h)
| sort by TimeGenerated desc
| take 20
```

## Troubleshooting — `401 UnauthorizedAccess` on Upload STIX Objects

If the run fails at the **Upload STIX Objects** action with:

```
UnauthorizedAccess: The Object ID [<object-id>] does not have required permission
to perform this action on the workspace [<workspace-guid>].
```

the playbook's **system-assigned managed identity** does not (yet) hold **Microsoft Sentinel
Contributor** on that workspace. The request body is fine — this is purely the role
assignment (step 2 above) not being effective for **this** identity.

1. Treat the **Object ID in the error message as authoritative** — that is the identity that
   must get the role. Confirm it matches the Logic App's identity: **Logic App → Identity →
   System assigned → Object (principal) ID**. (Redeploying with the same playbook name keeps
   this id; deleting and recreating the playbook changes it, so re-grant after a recreate.)
2. Grant the role to that exact object id, scoped to the workspace named in the error
   (resolve the name from its GUID with
   `az monitor log-analytics workspace list -g "$RG" --query "[?customerId=='<workspace-guid>'].name"`):

   ```bash
   for ROLE in "Microsoft Sentinel Contributor" "Log Analytics Reader"; do
     az role assignment create \
       --assignee-object-id "<object-id>" \
       --assignee-principal-type ServicePrincipal \
       --role "$ROLE" \
       --scope "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS"
   done
   ```
   If the failing action is **Get_Import_Watermark** and the error names
   `Microsoft.OperationalInsights/workspaces/read`, the missing role is **Log Analytics Reader**.
3. Data-plane RBAC for the threat-intelligence API can take **5–15 minutes** to propagate.
   Wait, then re-run the trigger. Verify with
   `az role assignment list --assignee "<object-id>" --all -o table`.

Common causes: the role was assigned at the **wrong scope** — most often on the **Logic App
itself** (scope ends in `/Microsoft.Logic/workflows/<playbook>`) instead of on the workspace,
which is what happens if IAM was opened from the playbook's blade; or on a different workspace
or resource group. Other causes: it was assigned to a **different identity** (wrong playbook, or
a recreated one), or it simply **hasn't propagated** yet. Check the `scope` column of

```bash
az role assignment list --assignee "<object-id>" --all \
  --query "[].{role:roleDefinitionName, scope:scope}" -o table
```

It must end in `/Microsoft.OperationalInsights/workspaces/<workspace>`.
