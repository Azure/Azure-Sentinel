# Microsoft Active Directory Tier Model – Automation Rules

These 5 automation rules are a **required** part of the Microsoft Active Directory Tier Model solution. They must be deployed **after** the solution is installed and its analytic rules are enabled. Without them, Tier Model incidents are not tagged, severities are not adjusted, and the workbook will not reflect the intended triage state.

## What they do

| Order | Rule | Action |
|-------|------|--------|
| 1 | **TM000 – Tagging** | Adds the `TIERMODEL` label to every Tier Model incident |
| 2 | **TM002 – Object created/deleted** | Closes (Informational) incidents where a user or computer object was deleted |
| 3 | **TM004 – Object state change** | Sets severity to **Low** for Tier 1 / Tier 2 / Disabled object changes |
| 4 | **TM007 – OU created/deleted** | Closes (Informational) non–Tier 0 OU create/delete activity |
| 5 | **TM010 – BitLocker key stored** | Closes (Informational) BitLocker recovery-key storage events |

The rules match incidents by the `(TMxxx.1)` tag that the solution's analytic rules place at the start of each alert title, so **no analytic-rule IDs need to be supplied** — they work in any workspace.

## Deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Active%2520Directory%2520Tier%2520Model%2FAutomation%2520Rules%2Fazuredeploy.json)

1. Click **Deploy to Azure** above.
2. Select the subscription and the resource group that contains your Microsoft Sentinel–enabled Log Analytics workspace.
3. Enter the **workspace** name.
4. Review + create.

## Post-deployment

1. Confirm the 5 rules appear under **Microsoft Sentinel > Automation**.
2. Ensure the solution's analytic rules are **enabled** so incidents carry the `(TMxxx.1)` title tag.
