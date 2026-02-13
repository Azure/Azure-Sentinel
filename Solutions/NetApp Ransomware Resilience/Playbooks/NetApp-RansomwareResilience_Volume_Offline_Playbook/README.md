# NetApp Ransomware Resilience Volume Offline Playbook

## Overview
This playbook takes NetApp volumes offline to immediately stop access and prevent further damage during a security incident. Taking a volume offline is a protective action that isolates compromised or at-risk storage.

## Purpose
When you identify a volume that is compromised by ransomware or under active attack, taking it offline immediately stops all access, preventing the spread of malware and protecting other parts of your infrastructure.

## Deployment Order
**This playbook should be deployed SIXTH**, after:
1. ✅ Auth Playbook (required)
2. ✅ Async Poll Playbook (required)
3. ✅ Enrich IP Playbook (optional)
4. ✅ Enrich StorageVM Playbook (optional)
5. ✅ Volume Snapshot Playbook (optional, but **strongly recommended**)

## What It Does
- Accepts volume ID, agent ID, and system ID as input
- Retrieves authentication from the Auth Playbook
- Initiates a volume offline operation via the NetApp API
- Uses the Async Poll Playbook to monitor operation completion
- Confirms when the volume is successfully taken offline
- Returns operation status

## Prerequisites
Before deploying this playbook:
1. Auth Playbook must be deployed and functioning correctly
2. Async Poll Playbook must be deployed and functioning correctly
3. Valid NetApp API credentials configured

## How to Use
This playbook can be:
- Called manually when you need to isolate a compromised volume
- Triggered automatically by Microsoft Sentinel automation rules during high-severity incidents
- Used as the final step in incident response workflows
- Combined with snapshot playbooks for data protection before isolation

**Input Required:**
- `volume_id`: The ID of the volume to take offline
- `agent_id`: The NetApp agent identifier
- `system_id`: The NetApp system identifier

## ⚠️ Critical Considerations
**Before taking a volume offline:**
- **Create a snapshot first** using the Volume Snapshot Playbook—this ensures you have a recovery point
- Understand the business impact—offline volumes are completely inaccessible
- Verify you're targeting the correct volume
- Have a recovery plan in place
- Document the reason for taking the volume offline

## Use Case Example
**Ransomware Containment:**
1. Receive alert about active file encryption on a volume
2. Use Enrich IP or Enrich StorageVM playbooks to confirm the affected volume
3. **Use Volume Snapshot playbook to create a clean recovery point**
4. **Use this playbook to take the compromised volume offline**
5. Investigation and remediation can proceed safely
6. Restore from snapshot when ready

## Post-Deployment Configuration
After deploying this playbook:
1. Test with a non-production volume using valid IDs
2. Verify the volume is taken offline successfully
3. Test bringing the volume back online to ensure recoverability
4. Configure automation rules with appropriate severity thresholds
5. Document your volume offline procedures and approval workflows

## Building Custom Workflows
This playbook is typically the **final protective action** in an incident response workflow:
- Enrich IP → Identify volume → Take snapshot → **Take volume offline**
- Critical alert → Enrich StorageVM → Snapshot critical volumes → **Offline compromised volume**

## Need Help?
If the volume offline operation isn't working, verify:
- The Auth Playbook is returning valid tokens
- The Async Poll Playbook is functioning correctly
- Volume ID, agent ID, and system ID are correct
- You have appropriate permissions to modify volume states
- The volume is currently online and accessible

## Recovery
To bring a volume back online after remediation:
- Use NetApp management tools or APIs
- Verify the threat has been fully remediated before bringing volumes online
- Restore from snapshots if data was compromised
