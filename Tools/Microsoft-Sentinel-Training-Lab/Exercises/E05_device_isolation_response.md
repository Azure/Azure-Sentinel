# (Optional) Exercise 5 — Cross-Platform Response Actions (Device Isolation) - Requires a VM onboarded to MDE

**Rule:** `[E5] [CrowdStrike] Device Isolation Response` _(the `[E5]` prefix is the deployed rule tag)_
**Deployed in:** `Artifacts/DetectionRules/rules.json`
**MITRE ATT&CK:** T1204.002 (User Execution: Malicious File)
**Difficulty:** Advanced

---

## Objective

Add an automated **device isolation** response action to a Custom Detection rule. This exercise demonstrates **cross-platform response**: a detection from CrowdStrike EDR triggers an isolation action via Microsoft Defender for Endpoint (MDE). You'll learn how to resolve the MDE `DeviceId` by joining the `DeviceInfo` table.

## Background

### The Cross-Platform Response Challenge

In a multi-vendor environment, detections come from one tool (CrowdStrike) but response actions execute through another (MDE). The challenge:

```
CrowdStrike Detection → hostname: "WORKSTATION-01"
MDE Isolation Action  → requires: DeviceId (GUID)
```

CrowdStrike alerts contain the **hostname** but not the MDE **DeviceId**. To bridge this gap, you must join the CrowdStrike detection data with MDE's `DeviceInfo` table, which maps `DeviceName` → `DeviceId`.

### Available Response Actions

Custom Detection rules in Defender XDR support the following automated response actions:

| Action | Required Column | Scope |
|---|---|---|
| **Isolate device** | `DeviceId` | Network isolation via MDE |
| **Block file** | `SHA256` or `SHA1` | Org-wide file block (already used in S2) |
| **Mark user as compromised** | `AccountObjectId` | Set Entra ID risk to High |
| **Disable user** | `AccountSid` | Temporarily block sign-in |
| **Force password reset** | `AccountSid` | Require password change |
| **Quarantine file** | `SHA1` or `SHA256` | Remove file + quarantine |
| **Collect investigation package** | `DeviceId` | Forensic data collection |
| **Run antivirus scan** | `DeviceId` | Trigger MDE AV scan |
| **Restrict app execution** | `DeviceId` | Limit to Microsoft-signed binaries |
| **Initiate investigation** | `DeviceId` | Start automated investigation |
| **Soft/hard delete email** | `NetworkMessageId` + `RecipientEmailAddress` | Email remediation |

> **Reference:** [Custom detection rule actions](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules#4-specify-actions)

### Why DeviceId?

Most device-scoped response actions require the MDE `DeviceId` — a GUID that uniquely identifies a device in MDE's inventory. This is different from:

- **DeviceName** — the hostname (human-readable, not unique)
- **CrowdStrike AID** — the CrowdStrike agent ID (not known to MDE)

The only way to map CrowdStrike detections to MDE actions is through the shared **hostname**.

## Prerequisites

> **Important:** This exercise requires **Defender for Endpoint** to be deployed and devices onboarded. The `DeviceInfo` table must contain the devices referenced in CrowdStrike detections. If `DeviceInfo` is empty or the hostnames don't match, the join will produce no results.

Verify `DeviceInfo` is available:

```kusto
DeviceInfo
| where Timestamp > ago(14d)
| summarize count() by DeviceName
| take 10
```

> **Note:** The `DeviceInfo` table uses `Timestamp` (not `TimeGenerated`) because it's a native Defender XDR table, not a Sentinel custom table.

## Techniques Covered

### Joining CrowdStrike with DeviceInfo

```kusto
CrowdStrikeDetections
| where TimeGenerated > ago(4h)
| where SeverityName == "Critical"
| extend CSHostname = tostring(Device.hostname)
| join kind=inner (
    DeviceInfo
    | where Timestamp > ago(14d)
    | summarize arg_max(Timestamp, DeviceId) by DeviceName
    | project DeviceName, DeviceId
) on $left.CSHostname == $right.DeviceName
```

| Element | Purpose |
|---|---|
| `extend CSHostname = tostring(Device.hostname)` | Extract hostname from CrowdStrike's nested `Device` object |
| `DeviceInfo \| where Timestamp > ago(14d)` | Use 14-day window to ensure device is found even if temporarily offline |
| `summarize arg_max(Timestamp, DeviceId) by DeviceName` | Get the **latest** DeviceId for each hostname |
| `join kind=inner` | Only return CrowdStrike detections where the device exists in MDE |
| `$left.CSHostname == $right.DeviceName` | Match on hostname |

> **Why `arg_max`?** A device may have multiple DeviceId entries (e.g., after re-imaging). `arg_max(Timestamp, DeviceId)` ensures you get the most recent one.

> **Why `kind=inner`?** If the device isn't in MDE, you can't isolate it — so there's no point generating an alert you can't act on.

### Adding the Response Action (via Graph API)

The `isolateDeviceResponseAction` is configured in the rule JSON:

```json
"responseActions": [
    {
        "@odata.type": "#microsoft.graph.security.isolateDeviceResponseAction",
        "identifier": "deviceId",
        "isolationType": "full"
    }
]
```

| Property | Value | Description |
|---|---|---|
| `@odata.type` | `#microsoft.graph.security.isolateDeviceResponseAction` | Action type |
| `identifier` | `deviceId` | Column in query results containing the MDE DeviceId |
| `isolationType` | `full` | Full network isolation (alternative: `selective`) |

### Adding via the Defender UI

If editing in the Defender portal instead of the Graph API:

1. Open the rule → **Edit** → Step 4 (**Actions**)
2. Under **Actions on devices**, select **Isolate device**
3. Set **Isolation type** to **Full**
4. Set **Scope** to the appropriate device groups

## Steps

### Step 1 — Verify the Current Rule

The deployed rule E5 currently has **no join** and **no response action**. It detects CrowdStrike critical alerts but can't trigger isolation because it doesn't have the `DeviceId`.

Run the current query in Advanced Hunting:

```kusto
CrowdStrikeDetections
| where TimeGenerated > ago(4h)
| where SeverityName == "Critical"
| extend CSHostname = tostring(Device.hostname)
| project TimeGenerated, Name, CSHostname, SeverityName
```

### Step 2 — Add the DeviceInfo Join

Modify the query to join with `DeviceInfo`:

```kusto
CrowdStrikeDetections
| where TimeGenerated > ago(4h)
| where SeverityName == "Critical"
| extend CSHostname = tostring(Device.hostname)
| join kind=inner (
    DeviceInfo
    | where Timestamp > ago(14d)
    | summarize arg_max(Timestamp, DeviceId) by DeviceName
    | project DeviceName, DeviceId
) on $left.CSHostname == $right.DeviceName
| project
    TimeGenerated,
    Name,
    Description,
    SeverityName,
    Tactic,
    Technique,
    TechniqueId,
    SourceAccountUpn,
    CSHostname,
    DeviceId,
    Filename,
    Sha256,
    Cmdline
| extend
    AccountUpn = SourceAccountUpn,
    DeviceName = CSHostname,
    FileName = Filename,
    SHA256 = Sha256,
    ProcessCommandLine = Cmdline,
    ReportId = tostring(hash_sha256(strcat(tostring(TimeGenerated), Name, CSHostname)))
```

Run the query to verify results include `DeviceId`.

### Step 3 — Add the Response Action

**Option A — Via Defender Portal:**
1. Save the modified query
2. Edit the rule → Step 4 (Actions) → Select **Isolate device**

**Option B — Via Graph API (JSON):**
Update the rule file to add the response action:

```json
"responseActions": [
    {
        "@odata.type": "#microsoft.graph.security.isolateDeviceResponseAction",
        "identifier": "deviceId",
        "isolationType": "full"
    }
]
```

Then redeploy using the deployment script:
```
.\Scripts\DeployDetectionRules.ps1
```

> **Warning:** In a production environment, automatic device isolation is a high-impact action. Always test with a `selective` isolation type first, and scope to a test device group.

### Step 4 — Enable and Test

1. Enable the rule
2. Ingest attack data using `.\Scripts\IngestCSV.ps1`
3. Monitor **Triggered alerts** and **Triggered actions** in the rule details
4. Verify the device isolation action was taken (check **Action Center** in Defender)

## Comparison with S2 (blockFile)

| Aspect | S2 — blockFile | E5 — isolateDevice |
|---|---|---|
| **Action** | Block file hash org-wide | Isolate device from network |
| **Required column** | `SHA256` | `DeviceId` |
| **Column source** | Native in CrowdStrike data | Requires `DeviceInfo` join |
| **Impact** | Prevents file execution everywhere | Cuts device network access |
| **Reversible** | Yes (unblock via Action Center) | Yes (release via Action Center) |
| **Risk** | Low — blocks one hash | High — disrupts user's work |

## Key Takeaways

- Cross-platform response requires **column resolution** — map identifiers between tools
- `DeviceInfo` is the bridge between third-party EDR hostnames and MDE DeviceIds
- Native Defender tables use `Timestamp`, not `TimeGenerated`
- `arg_max()` ensures you get the latest record for each device
- `kind=inner` join prevents alerts for devices not manageable by MDE
- Device isolation is a **high-impact** action — always scope carefully in production
- The Graph API requires both the query column (`DeviceId`) and the JSON `identifier` property to match

## Microsoft Learn References

- [Custom detection rule actions](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules#4-specify-actions)
- [Isolate devices from the network](https://learn.microsoft.com/en-us/defender-endpoint/respond-machine-alerts#isolate-devices-from-the-network)
- [DeviceInfo table schema](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceinfo-table)
- [Manage existing custom detection rules](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-manage)
- [MITRE T1204.002 — User Execution: Malicious File](https://attack.mitre.org/techniques/T1204/002/)
