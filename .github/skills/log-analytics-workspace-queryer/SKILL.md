---
name: log-analytics-workspace-queryer
description: Uses REST API to query Log Analytics workspaces. Use this skill when you need to query a Log Analytics workspace, for example, to check if the table exists in the workspace, or to validate an ASIM parser.
---

# Query Log Analytics workspace using REST API

## Inputs

This skill requires two inputs. This information should come from another skill and you do not need to ask the user for it.

- **KQL query** — the query to run against the Log Analytics workspace.
- **Workspace ID** — the GUID of the Log Analytics workspace.

## Step 1: Run the query

Execute the PowerShell script at `scripts/queryLogAnalytics.ps1` (relative to this skill's directory) by passing the workspace ID and KQL query as parameters:

```
.\scripts\queryLogAnalytics.ps1 -WorkspaceId "<workspaceId>" -Query "<KQL query>"
```

## Step 2: Return results

Return the full query output to the calling skill. The calling skill is responsible for interpreting and filtering the results (e.g., filtering for Error or Warning patterns during ASIM validation).
