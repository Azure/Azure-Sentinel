# Exercise 5 — Cross-Platform Response Actions (Device Isolation)

**Topic:** Understanding cross-platform response patterns between third-party EDR and MDE  
**Difficulty:** Advanced  
**Prerequisites:** None (reference exercise — hands-on requires MDE-onboarded devices)

> **Note:** This exercise is a **reference guide**. The join pattern shown here requires real MDE device data (the `DeviceInfo` table), which is only available if you have devices onboarded to Microsoft Defender for Endpoint. The lab's injected CrowdStrike data uses simulated hostnames that won't match your MDE inventory. Read through the pattern to understand the concept, and apply it in your production environment.

---

## Objective

Understand how to build a **cross-platform response** pattern where a detection from CrowdStrike EDR triggers an isolation action via Microsoft Defender for Endpoint (MDE). Learn how to resolve the MDE `DeviceId` by joining the `DeviceInfo` table, and how to configure automated response actions on custom detection rules.

## Background

### The Cross-Platform Response Challenge

In a multi-vendor environment, detections come from one tool (CrowdStrike) but response actions execute through another (MDE). The challenge:

```
CrowdStrike Detection → hostname: "WORKSTATION-01"
MDE Isolation Action  → requires: DeviceId (GUID)
```

CrowdStrike alerts contain the **hostname** but not the MDE **DeviceId**. To bridge this gap, you must join the CrowdStrike detection data with MDE's `DeviceInfo` table, which maps `DeviceName` → `DeviceId`.

### Available Response Actions

Custom detection rules in Defender XDR support the following automated response actions:

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

## How It Works in Practice

The following sections show the complete pattern for building a cross-platform detection-to-response rule. In a real environment with MDE-onboarded devices, you would create a custom detection rule using the query below and attach the `isolateDevice` response action.

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

---

## Next Steps

Continue to **[Exercise 6 — Port Scan Detection & Threshold Tuning](./E06_port_scan_threshold_tuning.md)**
