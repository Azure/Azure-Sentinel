# CSE Event Backfill for Microsoft Sentinel

`cse_backfill.py` fills gaps in SonicWall Cloud Secure Edge (CSE) events in Microsoft Sentinel,
typically following an outage, a reconnect of the connector, or a planned rotation of API keys.

The tool sends only events that are not yet in Sentinel, unchanged, through the connector's own
data collection rule, so it is safe to run more than once over the same period.

## Before You Start

- **When:** this tool should be run within **48 hours** of the gap (see [The 48-Hour Limit](#the-48-hour-limit)).
  CSE keeps events for 14 days; older events cannot be backfilled.
- **CSE API key:** a read-only API key from the CSE Command Center (**Settings > API Keys**).
- **Permissions** for the Azure account you sign in with:
  - **Microsoft Sentinel Reader** on the Sentinel workspace, to find the CSE connector.
  - **Reader** on the workspace's resource group, to find the connector's data collection rule.
  - **Monitoring Metrics Publisher** on the connector's data collection rule, to send events.
  - **Log Analytics Reader** on the Sentinel workspace, to check which events are present.
- **The Sentinel workspace's resource ID:** in the Azure portal, open **Log Analytics
  workspaces**, select the workspace used by Microsoft Sentinel, open **JSON View** on the
  **Overview** page, and copy the **Resource ID**. It ends with
  `/providers/Microsoft.OperationalInsights/workspaces/<name>`.

The tool finds the data collection rule used by the CSE connector in that workspace.

## Run in Azure Cloud Shell

1. Sign in to the [Azure portal](https://portal.azure.com) with the account above, and select
   the **Cloud Shell** icon (`>_`) in the top bar, to the right of the search box. Choose **Bash**.
   If asked about storage, choose **No storage account required**, select your subscription, and
   select **Apply**.
2. Download the tool into Cloud Shell:

   ```bash
   curl -fsSLO "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/SonicWall%20Cloud%20Secure%20Edge/Tools/cse_backfill.py"
   ```

   Alternatively, download `cse_backfill.py` from this folder and upload it with
   **Manage files > Upload** in the Cloud Shell toolbar.
3. Enter the CSE API key without it being shown:

   ```bash
   read -rsp "CSE API key: " CSE_API_TOKEN && export CSE_API_TOKEN && echo
   ```

4. Set the workspace's resource ID:

   ```bash
   WORKSPACE_ID="/subscriptions/<subscription>/resourceGroups/<group>/providers/Microsoft.OperationalInsights/workspaces/<name>"
   ```

5. Do a dry run for the gap, in UTC. It reports how many events are missing and sends nothing.
   Use a window from 15 minutes before the last event prior to the outage, to 15 minutes after the
   outage ended and events were confirmed as being received again in Sentinel.

   ```bash
   python3 cse_backfill.py --workspace "$WORKSPACE_ID" --after 2026-10-28T16:40:00Z --before 2026-10-28T17:10:00Z
   ```

   The first line of the output shows the data collection rule the tool found.

6. Send the missing events by repeating the command with `--send`:

   ```bash
   python3 cse_backfill.py --workspace "$WORKSPACE_ID" --after 2026-10-28T16:40:00Z --before 2026-10-28T17:10:00Z --send
   ```

7. Wait 10 minutes, then repeat the dry run from step 5. It should report `Missing: 0`.
8. Remove the key from the session:

   ```bash
   unset CSE_API_TOKEN
   ```

## More Than One CSE Connector in a Workspace

If a workspace has more than one CSE connector, for example one per CSE organization, and they
use different data collection rules, the tool cannot tell which connector the API key belongs
to. If this is the case, the tool will list each of the rules with their connector names and stop.
Record the correct data collection rule resource ID from the list and run the below command,
inserting the resource ID as `--dcr-id`:

```bash
python3 cse_backfill.py --dcr-id "<data collection rule resource ID>" --after 2026-10-28T16:40:00Z --before 2026-10-28T17:10:00Z
```

Before sending, the tool also checks that the CSE organization of the events already has events
in the workspace, so events are not sent to another organization's workspace by mistake. If it
has none in the last 30 days, the tool reports it and does not send. When this is expected, for
example for a connector added in the last few days, add `--allow-new-org`.

## The 48-Hour Limit

Sentinel sorts events by their `TimeGenerated` time, which the connector sets to the time the
event occurred in CSE. Azure accepts that time only if it is less than about 48 hours old. For
older events, Azure replaces it with the time the events are received. This is an Azure rule,
not a setting of the connector or this tool.

To avoid this happening unnoticed, the tool does not send events older than 47 hours. It
reports them with a warning instead.

To send them anyway, add `--allow-old`. Events up to 14 days old can then be sent, with these
effects:

- Every event and all of its data is kept.
- `TimeGenerated` is the time of the backfill, so searches, workbooks, and analytic rules that
  use the Sentinel time range show these events on the backfill date. Analytic rules may raise
  alerts for them at that time.
- The time the event occurred is still available in the `EventTime` column of the `CSEEvents`
  function. Filter on `EventTime` to find these events by when they happened.

## Options

| Option | Purpose |
|---|---|
| `--workspace` | Resource ID of the Sentinel workspace; the tool finds the CSE connector's data collection rule |
| `--dcr-id` | Resource ID of the CSE connector's data collection rule, in place of `--workspace` |
| `--after`, `--before` | Start and end of the gap, ISO 8601 UTC (for example `2026-10-28T16:40:00Z`) or epoch milliseconds; both included |
| `--region` | `us` (default, `net.banyanops.com`) or `eu` (`eucc.console.banyanops.com`) |
| `--send` | Send the missing events. Without it, the tool only reports |
| `--allow-old` | Also send events older than 47 hours; Sentinel records them at the time of sending |
| `--allow-new-org` | Send even if the events' CSE organization has no events in the workspace yet |

## Messages

| Message | Meaning |
|---|---|
| `Missing: 0` / `Nothing to backfill.` | Sentinel already has every event in the period |
| `The CSE API key was not accepted (HTTP 401).` | The key is wrong, deleted, or for another region |
| `No SonicWall CSE connector found in this workspace.` | The workspace has no CSE connector, or the account cannot read it (Microsoft Sentinel Reader) |
| `This workspace has SonicWall CSE connectors that send to different DCRs` | See [More Than One CSE Connector in a Workspace](#more-than-one-cse-connector-in-a-workspace) |
| `Warning: the CSE organization of these events ... has no events in this workspace` | Check that the API key and the workspace belong to the same organization; add `--allow-new-org` if expected |
| `Sending was refused (HTTP 403).` | The account lacks Monitoring Metrics Publisher on the rule; a new role can take a few minutes to apply |
| `Warning: ... older than 47 hours` | Those events would be recorded at the backfill time; add `--allow-old` to send them anyway |

## How It Works

- Finds the CSE connector in the workspace and the data collection rule it sends to.
- Pulls CSE events in 1-hour windows, oldest first, because requests over long periods can
  time out on busy tenants. A window that still fails is split in half and retried.
- Retries on HTTP 429 and server errors, honoring `Retry-After`.
- Checks the `CSEEvents_CL` table for each event's ID, and sends only the missing events.
- Uses only Python 3 and the Azure CLI, both included in Cloud Shell.
