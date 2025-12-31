# Heartbeat

Reference for Heartbeat table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Endpoint |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✗ No |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/heartbeat) |

## Solutions (6)

This table is used by the following solutions:

- [DORA Compliance](../solutions/dora-compliance.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [PCI DSS Compliance](../solutions/pci-dss-compliance.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [VMware SD-WAN and SASE](../solutions/vmware-sd-wan-and-sase.md)
- [Windows Firewall](../solutions/windows-firewall.md)

---

## Content Items Using This Table (6)

### Analytic Rules (1)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [M2131_AssetStoppedLogging](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131AssetStoppedLogging.yaml)

### Workbooks (5)

**In solution [DORA Compliance](../solutions/dora-compliance.md):**
- [DORACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json)

**In solution [PCI DSS Compliance](../solutions/pci-dss-compliance.md):**
- [PCIDSSCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PCI%20DSS%20Compliance/Workbooks/PCIDSSCompliance.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [VMware SD-WAN and SASE](../solutions/vmware-sd-wan-and-sase.md):**
- [VMwareSASESOCDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Workbooks/VMwareSASESOCDashboard.json)

**In solution [Windows Firewall](../solutions/windows-firewall.md):**
- [WindowsFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.compute/virtualmachines`
- `microsoft.containerservice/managedclusters`
- `microsoft.kubernetes/connectedclusters`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`
- `microsoft.compute/virtualmachinescalesets`
- `microsoft.hybridcontainerservice/provisionedclusters`
- `microsoft.automation/automationaccounts`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
