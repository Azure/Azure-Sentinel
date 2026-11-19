# Conditional Access Emergency Access Safeguard

Microsoft recommends excluding emergency access (break-glass) accounts from Conditional Access policies so administrators are never locked out of the tenant. Over time, new or edited policies can miss these exclusions.

This solution includes one playbook, **CA-EmergencyAccessSafeguard**, which checks every Conditional Access policy daily, restores missing emergency access exclusions, verifies each change, and emails the result.

See [Playbooks/CA-EmergencyAccessSafeguard/README.md](Playbooks/CA-EmergencyAccessSafeguard/README.md) for prerequisites, deployment and post-deployment steps.

Supported clouds: Commercial, GCC, GCC High, and DoD.
