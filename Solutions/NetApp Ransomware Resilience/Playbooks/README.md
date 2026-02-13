# NetApp Ransomware Resilience Playbooks

## Overview
The NetApp Ransomware Resilience solution provides a set of modular playbooks that work together to help you respond to ransomware and security incidents affecting your NetApp storage infrastructure. These playbooks integrate with Microsoft Sentinel to provide automated investigation and response capabilities.

## Architecture
The playbooks are designed as **building blocks** that you can combine to create custom incident response workflows. Each playbook serves a specific purpose, and they work together to provide comprehensive ransomware protection.

### Playbook Categories

**Foundation Playbooks** (Required Infrastructure):
- **Authentication Playbook** - Manages credentials and provides authentication tokens
- **Async Poll Playbook** - Monitors asynchronous operations until completion

**Investigation Playbooks** (Data Enrichment):
- **Enrich IP Playbook** - Retrieves network interface details for IP addresses
- **Enrich StorageVM Playbook** - Retrieves Storage VM configuration and volume information

**Response Playbooks** (Protective Actions):
- **Volume Snapshot Playbook** - Creates point-in-time snapshots for data protection
- **Volume Offline Playbook** - Takes volumes offline to isolate compromised storage

## 🚀 Deployment Order

**You MUST deploy the playbooks in this specific order:**

### 1. Authentication Playbook (FIRST)
Deploy the **NetApp-RansomwareResilience-Auth-Playbook** first. This creates the shared Key Vault and provides authentication services that all other playbooks depend on.

📖 [Auth Playbook Documentation](./NetApp-RansomwareResilience-Auth-Playbook/README.md)

### 2. Async Poll Playbook (SECOND)
Deploy the **NetApp-RansomwareResilience-Async-Poll-Playbook** next. This monitors asynchronous operations and is used by most other playbooks.

📖 [Async Poll Playbook Documentation](./NetApp-RansomwareResilience_Async_Poll_Playbook/README.md)

### 3. Enrich IP Playbook (THIRD)
Deploy the **NetApp-RansomwareResilience-Enrich-IP-Playbook** to enable IP address investigation capabilities.

📖 [Enrich IP Playbook Documentation](./NetApp-RansomwareResilience_Enrich_IP_Playbook/README.md)

### 4. Enrich StorageVM Playbook (FOURTH)
Deploy the **NetApp-RansomwareResilience-Enrich-StorageVM-Playbook** to enable storage configuration investigation.

📖 [Enrich StorageVM Playbook Documentation](./NetApp-RansomwareResilience_Enrich_StorageVM_Playbook/README.md)

### 5. Volume Snapshot Playbook (FIFTH)
Deploy the **NetApp-RansomwareResilience-Volume-Snapshot-Playbook** to enable data protection through snapshots.

📖 [Volume Snapshot Playbook Documentation](./NetApp-RansomwareResilience_Volume_Snapshot_Playbook/README.md)

### 6. Volume Offline Playbook (SIXTH)
Deploy the **NetApp-RansomwareResilience-Volume-Offline-Playbook** to enable volume isolation capabilities.

📖 [Volume Offline Playbook Documentation](./NetApp-RansomwareResilience_Volume_Offline_Playbook/README.md)

## Building Custom Incident Response Workflows

These playbooks are designed to work together as building blocks. You can create powerful automated response workflows by combining them in different ways.

### Example Workflow Pattern

Here's a typical ransomware incident response pattern:

```
Incident Detected
    ↓
Investigate (Enrich IP or Enrich StorageVM)
    ↓
Identify Affected Volumes
    ↓
Protect Data (Volume Snapshot)
    ↓
Contain Threat (Volume Offline)
```

### Sample Use Cases

**Use Case 1: Suspicious IP Investigation**
1. Alert triggers on suspicious IP activity
2. **Enrich IP Playbook** - Gather network interface details
3. **Enrich StorageVM Playbook** - Get full storage context
4. **Volume Snapshot Playbook** - Protect volumes before taking action
5. **Volume Offline Playbook** - Isolate if threat is confirmed

**Use Case 2: Ransomware Alert Response**
1. Ransomware detection alert triggers
2. **Enrich StorageVM Playbook** - Identify all volumes on affected storage
3. **Volume Snapshot Playbook** - Immediately snapshot all critical volumes
4. **Volume Offline Playbook** - Take compromised volumes offline
5. Restore from snapshots after remediation

**Use Case 3: Manual Investigation**
1. SOC analyst receives threat intelligence
2. Manually trigger **Enrich IP Playbook** with suspicious IP
3. Review enrichment data to assess risk
4. If needed, manually trigger **Volume Snapshot** and **Volume Offline** playbooks

## Getting Started

### Prerequisites
Before deploying any playbooks:
- Access to an Azure subscription with Microsoft Sentinel enabled
- Valid NetApp Ransomware Resilience API credentials (client ID, client secret, account ID)
- Appropriate permissions to create Azure resources
- Understanding of your NetApp storage infrastructure

### Deployment Steps
1. **Deploy Foundation Playbooks** (Auth, then Async Poll)
2. **Configure Authentication** - Add your NetApp API credentials to the Key Vault
3. **Test Foundation Playbooks** - Verify authentication is working
4. **Deploy Investigation Playbooks** - Add enrichment capabilities as needed
5. **Deploy Response Playbooks** - Add protective action capabilities
6. **Test Each Playbook** - Verify functionality with non-production resources
7. **Create Automation Rules** - Connect playbooks to Microsoft Sentinel alerts
8. **Document Procedures** - Define when and how each playbook should be used

### Testing Recommendations
- Always test with non-production volumes first
- Verify authentication before deploying action playbooks
- Create test automation rules before enabling production triggers
- Document volume offline/online procedures
- Establish snapshot retention policies

## Best Practices for SOC Analysts

### Investigation Phase
- Use **Enrich IP** and **Enrich StorageVM** playbooks to gather context
- Review enrichment data before taking protective actions
- Document findings for incident reports

### Response Phase
- **Always take snapshots BEFORE taking volumes offline**
- Verify you're targeting the correct volumes
- Understand the business impact of taking volumes offline
- Follow your organization's approval process for disruptive actions

### Recovery Phase
- Use snapshots to restore clean data
- Verify threats are fully remediated before bringing volumes online
- Update security controls to prevent recurrence

## Security Considerations
- All NetApp API credentials are stored securely in Azure Key Vault
- Playbooks use managed identities for Azure resource access
- Review and approve automation rules before enabling auto-response
- Maintain audit logs of all playbook executions
- Regularly review and update API credentials

## Support and Troubleshooting

### Common Issues
- **Authentication failures**: Verify credentials in Key Vault and Auth Playbook functionality
- **Polling timeouts**: Check network connectivity to NetApp API endpoints
- **Invalid volume IDs**: Confirm IDs from enrichment playbooks before using action playbooks
- **Permission errors**: Verify playbook managed identities have required access

### Getting Help
- Review individual playbook README files for specific troubleshooting
- Check Logic App run history for detailed error messages
- Verify prerequisites are met for each playbook
- Test with known-good values from your NetApp environment

## Additional Resources
- Microsoft Sentinel Documentation: [https://docs.microsoft.com/azure/sentinel/](https://docs.microsoft.com/azure/sentinel/)
- Azure Logic Apps Documentation: [https://docs.microsoft.com/azure/logic-apps/](https://docs.microsoft.com/azure/logic-apps/)
- NetApp Ransomware Resilience Documentation: Contact NetApp Support

---

**Remember:** These playbooks are powerful tools for incident response. Always test thoroughly, understand the impact of actions, and follow your organization's security procedures.
