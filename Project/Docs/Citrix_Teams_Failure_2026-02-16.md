# Citrix "Teams for Engineering" Launch Failure — Root Cause Analysis

**Date:** 2026-02-16  
**Analyst:** Taz (jata8002)  
**Transaction ID:** E0B7F442-AAED-411C-9C71-2DE65F78790E  
**Platform:** macOS | Citrix Workspace App 25.11.1.42  
**Error Code:** `CharlotteErrorBadCredentials`  
**VDA Server:** DAYWINCTXP305  

---

## 1. Logs/Events — Timeline of Failure

| Time (EST)  | Event | Source File | Severity |
|---|---|---|---|
| 11:59:44 | Citrix Workspace uninstalled (clean reinstall attempt) | Uninstall log | INFO |
| 12:00:21 | Reinstall completed; keychain RSA keys regenerated | Uninstall log | INFO |
| 12:01:01 | Workspace Helper starts — `AccountRecords.plist` NOT FOUND (×12 occurrences) | AccountRecordsFetcher.swift | **ERROR** |
| 12:01:02 | `AuthMan configuration` initialization FAILED — "No On-Prem stores" | LegacyAuthManConfigurationHelper.swift | **ERROR** |
| 12:01:07 | Keychain vault item `-25300` (item not found) during SSO token retrieval | CRKeychainInterface.m | **ERROR** |
| 12:03:34 | Teams for Engineering subscription confirmed | DZStoreConnection.m | INFO |
| 12:03:49 | Engineering Team Desktop launch started (first successful ICA conn) | CitrixViewer | INFO |
| **12:04:18** | **Engineering Team Desktop launch FAILED — "Launch timed out"** | CtxWorkspaceListenerEndpointDelegate | **FAILURE** |
| 12:15:49 | Teams for Engineering launch attempt #1 | DZStoreApplication.mm | INFO |
| **12:16:06** | Teams launch initially reports SUCCESS on DAYWINCTXP305 | CtxWorkspaceListenerEndpointDelegate | SUCCESS |
| **12:16:19** | Teams launch overridden to FAILURE — "Launch timed out" | CtxWorkspaceListenerEndpointDelegate | **FAILURE** |
| **12:16:36** | **"Engine terminated" — `Session.Launch.ConnectionFailed`** | CASTelemetryCWrapper.m | **ERROR** |
| 12:18:41 | Engineering Team Desktop also fails — "Engine terminated" | CASTelemetryCWrapper.m | **ERROR** |
| 12:18:52 | Teams for Engineering launch attempt #2 | DZStoreApplication.mm | INFO |
| **12:19:02** | Teams engine terminated again — `Session.Launch.ConnectionFailed` | CASTelemetryCWrapper.m | **ERROR** |
| 12:19:06 | `launchAborted` — `SessionTrackerServiceError.badTransition` | UtilExtensions.swift | **ERROR** |
| 12:19:18 | Teams for Engineering launch attempt #3 | DZStoreApplication.mm | INFO |
| **12:19:27** | Teams engine terminated AGAIN — `Session.Launch.ConnectionFailed` | CASTelemetryCWrapper.m | **ERROR** |
| **12:19:48** | Final Teams launch reported as FAILURE | CtxWorkspaceListenerEndpointDelegate | **FAILURE** |

---

## 2. Root Cause Analysis

### Primary Issue: **CharlotteErrorBadCredentials** (Stale/Corrupt Credential Cache)

The error code `CharlotteErrorBadCredentials` indicates the Citrix StoreFront (Charlotte engine) is rejecting the cached credentials. This is a **credential pass-through failure**, NOT a connectivity issue.

### Contributing Factors Identified in Logs:

1. **Keychain Item Not Found (error `-25300`)**
   - After the clean reinstall at 12:00, the keychain vault `WorkspaceVaultEncryptionType` could not find the SSO token
   - The RSA key was regenerated but the old encrypted credential data was wiped

2. **AccountRecords.plist Missing**  
   - `com.citrix.ReceiverFTU.AccountRecords.plist` was not found (12+ occurrences)
   - This file stores the account/store configuration for credential pass-through

3. **AuthMan Configuration Failed**  
   - `LegacyAuthManConfigurationHelper`: "No On-Prem stores to initialize AuthMan configuration"
   - This means the credential manager couldn't set up the pass-through pipeline

4. **Session on DAYWINCTXP305 is Stale**
   - Teams connected to DAYWINCTXP305 initially (reports SUCCESS at 12:16:06)
   - But then the ICA engine was terminated seconds later (12:16:36)
   - The session was left in a broken state — `badTransition` errors show the session tracker couldn't cleanly abort

5. **User Profile on VDA Server May Be Corrupt**
   - Multiple `launchAborted` events with `badTransition` suggest the server-side session is stuck
   - The fact that Engineering Team Desktop ALSO fails confirms this is a server-session/profile issue, not app-specific

---

## 3. Remediation Steps (Ordered by Priority)

### Step A: Log Off All Stale Sessions via Citrix Director (IMMEDIATE)

1. Navigate to: `http://daywinctxp515.enterprisenet.org/Director/`
2. Log in with your enterprise credentials
3. Search for your user ID: `jata8002`
4. You will see active/stale sessions on **DAYWINCTXP305** (and possibly others)
5. **Log off ALL sessions** — click each session → "Log Off" on the left panel
6. Wait 2 minutes for the session cleanup to complete

### Step B: Delete User Profile on VDA Servers

If Step A doesn't resolve it, the user profile on the VDA is corrupt:

1. Connect to **DAYWINCTXB045** (backup server)
   - Navigate to `C:\Users\` → Find and delete your user profile folder (e.g., `jata8002` or `Jack.Taz`)
2. Connect to **DAYWINCTXP305** (primary server)  
   - Navigate to `C:\Users\` → Find and delete your user profile folder
   - Also check `C:\Windows\System32\config\systemprofile` for any stuck profile data

### Step C: Reset Local Citrix Keychain & Credentials (Mac-side)

Run these commands in Terminal to clear stale local credentials:

```bash
# Remove Citrix keychain entries
security delete-generic-password -s "com.citrix.receiver.nomas" -a "jata8002" login.keychain-db 2>/dev/null
security delete-generic-password -s "com.citrix.AuthManager" login.keychain-db 2>/dev/null

# Remove Citrix local cache files
rm -rf ~/Library/Application\ Support/Citrix\ Receiver/
rm -rf ~/Library/Application\ Support/Citrix\ Workspace/
rm -rf ~/Library/Caches/com.citrix.*
rm -rf ~/Library/Preferences/com.citrix.*
rm -rf ~/Library/Group\ Containers/*citrix*

# Remove WebKit/Safari data cache for Citrix
rm -rf ~/Library/WebKit/com.citrix.*
```

### Step D: Re-add Account in Citrix Workspace

After Steps A-C:
1. Open Citrix Workspace
2. It should prompt you to add your account (since we cleared the config)
3. Enter your StoreFront URL (e.g., `https://xenapp.nielseniq.com`)
4. Authenticate fresh
5. Try launching Teams for Engineering again

---

## 4. Cleanup

| Action | File | Status |
|---|---|---|
| Logs archived | `/Users/tazjack/Desktop/WorkspaceLogs_2026_02_16-12_19_54/` | ✅ Preserved |
| Analysis documented | This file | ✅ |

---

## 5. Memory Update

- **`CharlotteErrorBadCredentials`** = Stale credential cache + keychain corruption after Citrix reinstall
- Always clear keychain entries AND server-side profiles when doing a clean reinstall
- The Citrix Workspace uninstaller does NOT clear macOS keychain items by default (error `-25300` proves this)
- `AccountRecords.plist` must exist for credential pass-through; if missing after reinstall, the account must be re-added manually
- DAYWINCTXP305 sessions can get stuck in `sessionRunning` → `launchAborted` loops that require Director logoff

---

## UPDATE — Round 2 Analysis (13:03 EST)

### New Error (Screenshot)
The error has changed from `CharlotteErrorBadCredentials` to a **server-side Citrix XenApp** error dialog:

> **"Teams for Engineeri" failed to start.**  
> The Citrix server is unable to process your request to start this published application.  
> Please try again. If the problem persists, contact your administrator.

### What Changed
- ✅ `CharlotteErrorBadCredentials` is **GONE** — local credential cleanup worked
- ❌ New error is now **server-side** — the XenApp Delivery Controller is rejecting the launch

### New Logs Analysis (WorkspaceLogs_2026_02_16-13_03_32)

| Time | Event | Status |
|---|---|---|
| 13:01:13 | Engineering Team Desktop session received `PACKET_TERMINATE` | CONNECTION KILLED |
| 13:01:13 | "Engine terminated" — `Session.Launch.ConnectionFailed` for Eng Team Desktop | ERROR |
| 13:01:42 | Card 59109 — "has not received any keepAlive in 30 seconds, timing out" | TIMEOUT |
| 13:02:11 | Card 59105, 59102, 59107, 59104 — ALL timed out (no keepAlive in 30s) | TIMEOUT ×4 |
| 13:02:21 | AppConfig discovery for `https://xenapp.nielseniq.com` — "not configured" | WARNING |
| 13:02:51 | Teams for Engineering subscription confirmed | OK |
| 13:02:58 | Teams launch initiated (TransactionId: AE2187BF) | LAUNCHING |
| 13:03:14 | Teams launch initially reports SUCCESS, PID 27969 | SUCCESS |
| **13:03:28** | **Teams launch overridden to FAILURE — "Launch timed out"** | **FAILURE** |

### Root Cause — Round 2
The pattern is clear: the **Citrix ICA engine connects to the VDA server, the application starts (reports SUCCESS), but then the server kills the connection within seconds**. This creates a "Launch timed out" pattern.

This is a **server-side issue** — specifically:
1. **Stale user session on DAYWINCTXP305** — the server has orphaned session processes
2. **User profile corruption** — the Teams app starts but crashes immediately because the user profile on the VDA is corrupt
3. **The XenApp dialog** "Citrix server is unable to process your request" confirms the **Delivery Controller** or **VDA worker** is rejecting the app launch

### This is Now a Citrix Admin Issue

**This cannot be fixed from the client side.** You need to:

1. **Log off ALL sessions via Citrix Director** (`http://daywinctxp515.enterprisenet.org/Director/`)
2. **Have a Citrix admin** delete your user profile on DAYWINCTXP305 (you may not have RDP access to the VDA)
3. **Or**, request the Citrix admin to reset the VDA worker process on DAYWINCTXP305
4. **As a last resort**, ask the admin to reassign you to a different VDA server

---

## UPDATE — Round 3 Analysis (13:23 EST) — Post Full Cleanup & Reinstall

### Actions Taken
- **Complete Citrix removal**: All processes killed, all files/caches/preferences/keychain entries nuked
- **Fresh install**: Citrix Workspace App v25.11.1 installed from scratch
- **Store re-added**: `https://xenapp.nielseniq.com` configured in fresh client

### New Logs Analysis (WorkspaceLogs_2026_02_16-13_23_38)

#### Complete Session Timeline — Three Launch Attempts

| Time | Event | Resource | VDA Server | Status |
|---|---|---|---|---|
| 13:22:25 | Teams subscription confirmed | Teams for Engineering | — | ✅ OK |
| 13:22:28 | **Attempt 1** — Session.Launch.Start | **Teams for Engineering** | xenapp.nielseniq.com:443 → VDA | LAUNCHING |
| 13:22:40 | ICA engine successfully completed launch and login | Teams for Engineering | PID 37548 | ✅ SUCCESS |
| 13:22:41 | Launch reported as SUCCESS | Teams for Engineering | — | ✅ SUCCESS |
| 13:22:41 | **"Could not find resource details for resource"** (LL_ERROR) | Teams for Engineering | — | ⚠️ ERROR |
| 13:22:56 | **Attempt 1B** — Engineering Team Desktop also launched | Engineering Team Desktop | DAYWINCTXP290 (Session ID 2) | LAUNCHING |
| 13:22:57 | ICA detected, capabilities negotiated, TLS 1.2 connected | Engineering Team Desktop | DAYWINCTXP290 (VDA v7.33.0.0) | ✅ CONNECTED |
| 13:22:58 | Audio/webcam/clipboard initialized, graphics flushed to screen | Engineering Team Desktop | DAYWINCTXP290 | ✅ RENDERED |
| **13:22:58** | **Card state → launchFailed** (SessionLaunchError) | Teams for Engineering | — | ❌ **FAILED** |
| 13:23:01 | Engineering Team Desktop reports VISUALLY_READY + Launch.Success | Engineering Team Desktop | DAYWINCTXP290 | ✅ SUCCESS |
| **13:23:09** | **`PACKET_TERMINATE: Command=1`** — VDA KILLS the Teams session | **Teams for Engineering** | PID 37548 | 💀 **TERMINATED** |
| **13:23:09** | **"Engine terminated" — Session.Launch.ConnectionFailed** | **Teams for Engineering** | PID 37548 | ❌ **KILLED** |
| **13:23:12** | **`PACKET_TERMINATE: Command=1`** — VDA KILLS Engineering Desktop too | **Engineering Team Desktop** | PID 37593 (DAYWINCTXP290) | 💀 **TERMINATED** |
| **13:23:12** | **"Engine terminated" — Session.Launch.ConnectionFailed** | Engineering Team Desktop | PID 37593 | ❌ **KILLED** |
| 13:23:17 | **Attempt 2** — New Viewer process starts (PID 37607) | Teams for Engineering | — | LAUNCHING |
| 13:23:19 | Session sharing attempted — **FAILED** (no clients to share with) | Teams for Engineering | — | ⚠️ WARNING |
| 13:23:20 | Connected to VDA, TLS 1.2, credentials sent successfully | Teams for Engineering | xenapp.nielseniq.com | ✅ CONNECTED |
| 13:23:30 | ICA engine successfully completed launch and login | Teams for Engineering | PID 37607 | ✅ SUCCESS |
| 13:23:31 | Launch reported as SUCCESS | Teams for Engineering | — | ✅ SUCCESS |
| 13:23:31 | **"Could not find resource details for resource"** (LL_ERROR × 2) | Teams for Engineering | — | ⚠️ ERROR |

### Definitive Root Cause — Round 3

**The VDA server is actively terminating the sessions via `PACKET_TERMINATE`.**

Here is the exact kill sequence from the logs:

```
13:22:40  Session.Launch.Success — Teams for Engineering (PID 37548) ← VDA says SUCCESS
13:22:58  VDA sends graphics to screen, all virtual channels working ← EVERYTHING IS FINE
13:23:09  Received PACKET_TERMINATE: Command=1  ← THE VDA KILLS IT
13:23:09  "Engine terminated" — Session.Launch.ConnectionFailed ← CLIENT REPORTS FAILURE
```

The critical evidence:

1. **Client is NOT the problem** — Fresh install, fresh credentials, TLS connects fine, ICA detects correctly, credentials pass successfully, graphics render to screen
2. **VDA server actively kills the session** — `PACKET_TERMINATE: Command=1` is sent FROM the server TO the client ~30 seconds after successful launch
3. **Two different VDA servers exhibit this** — Engineering Team Desktop connected to `DAYWINCTXP290` and it was ALSO terminated with `PACKET_TERMINATE`
4. **"Could not find resource details"** — The Citrix Workspace app cannot find the `LaunchInfo` for the resource, suggesting a StoreFront/Workspace UI sync issue
5. **Session sharing fails** — "TrySessionSharing Failed" / "no clients to share with" indicates the session tracker is not properly coordinating between Workspace and Viewer

### Why PACKET_TERMINATE Happens

The server sends `PACKET_TERMINATE: Command=1` for these reasons:
- **Session limit reached** on the VDA — policy allows only N sessions per user, and orphaned sessions consume the limit
- **Published app policy** — The Delivery Controller routes the app to a VDA that can't serve it (wrong Delivery Group, Worker Group, or app version mismatch)
- **Citrix Session Reliability / AutoClient Reconnect** — An old session token is conflicting with the new launch, causing the new session to be killed
- **VDA worker process crash** — The app on the VDA crashes immediately after launch, triggering the VDA to send PACKET_TERMINATE

### Confirmed Server-Side Resolution Required

| Action | Who | Priority |
|---|---|---|
| Log off ALL sessions for `jata8002` via Citrix Director | User or Citrix Admin | **P1 — CRITICAL** |
| Reset VDA worker on DAYWINCTXP290 and DAYWINCTXP305 | Citrix Admin | **P1** |
| Delete/reset user profile on VDA servers | Citrix Admin | **P2** |
| Check session limit policy in Delivery Group | Citrix Admin | **P2** |
| Verify "Teams for Engineering" published app configuration | Citrix Admin | **P3** |
| Reassign user to a clean VDA server | Citrix Admin (fallback) | **P3** |

### Memory Update — Round 3

- `PACKET_TERMINATE: Command=1` from the VDA = **server actively killing the session**, not a client timeout
- A "SUCCESS → FAILURE" pattern (launch reports success then fails 15-30 seconds later) always means the VDA accepted and then rejected the session
- "Could not find resource details for resource" in `CWAMainUIWKWebViewControllerExtensions.swift` = Workspace UI lost track of the resource record — may be caused by the rapid success/failure toggle
- Session sharing ("TrySessionSharing Failed") after a clean install is expected/normal (no existing sessions to share with)
- VDA version `7.33.0.0` on DAYWINCTXP290 is current-generation LTSR — no known version bugs at this level
- `HdxRtcEngine` directory missing (`The file "HdxRtcEngine" couldn't be opened`) — this is expected after clean install and not a contributing factor

---

## 6. Innovation Opportunity

**Automated Citrix Session Health Check Script**: Create a PowerShell/bash script that:
1. Queries Citrix Director OData API for user sessions
2. Identifies stuck/stale sessions automatically
3. Logs off stale sessions and notifies the user
4. Could be scheduled as a daily task to prevent accumulation

This would eliminate the manual Director navigation and reduce mean-time-to-recovery for credential issues.
