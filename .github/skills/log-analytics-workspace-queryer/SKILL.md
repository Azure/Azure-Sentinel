---
name: log-analytics-workspace-queryer
description: Queries Log Analytics workspaces through an advertised official Sentinel Triage MCP tool first, with the REST API script as fallback.
---

# Query a Log Analytics workspace

## Inputs

This skill requires two inputs. This information should come from another skill and you do not need to ask the user for it.

- **KQL query** — the query to run against the Log Analytics workspace.
- **Workspace ID** — the GUID of the Log Analytics workspace.

## Step 1: Prefer official Sentinel Triage MCP

Inspect the connected official Sentinel Triage MCP capabilities. If it
advertises a suitable Log Analytics or Sentinel workspace-query tool, use that
tool first. Do not invent a tool name or assume the capability exists.

Fall back to the repository REST script only when the MCP lacks the capability
or has an availability, authentication, permission, connectivity, timeout, or
provider-service failure. A genuine KQL error is a query failure and must not
be retried through another provider.

## Step 2: REST fallback

Execute the PowerShell script at `scripts/queryLogAnalytics.ps1` (relative to this skill's directory) by passing the workspace ID and KQL query as parameters:

```
.\scripts\queryLogAnalytics.ps1 -WorkspaceId "<workspaceId>" -Query "<KQL query>"
```

## Step 3: Return results

Return the full query output to the calling skill. The calling skill is responsible for interpreting and filtering the results (e.g., filtering for Error or Warning patterns during ASIM validation).
