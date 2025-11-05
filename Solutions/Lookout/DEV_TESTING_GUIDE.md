# Lookout Mobile Risk API v2 - Development Testing Guide for Dummies

## 🎯 Overview
This guide walks you through setting up a complete development environment to test the Lookout solution locally before submitting to Microsoft's official Azure Sentinel repository.

## 📋 Prerequisites Checklist

### Required Accounts & Access
- [ ] **Azure Subscription** with Owner or Contributor access
- [ ] **Microsoft Sentinel workspace** (can create a dev/test workspace)
- [ ] **Lookout Enterprise account** with API access
- [ ] **GitHub account** for version control
- [ ] **Visual Studio Code** or preferred editor

### Required Tools
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install PowerShell (if on Linux/Mac)
# See: https://docs.microsoft.com/powershell/scripting/install/installing-powershell

# Install Git
sudo apt-get install git  # Ubuntu/Debian
# or
brew install git          # macOS
```

## 🏗️ Step 1: Set Up Development Environment

### Create Development Workspace
```bash
# 1. Create a resource group for testing
az group create \
  --name "rg-sentinel-lookout-dev" \
  --location "East US"

# 2. Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group "rg-sentinel-lookout-dev" \
  --workspace-name "law-sentinel-lookout-dev" \
  --location "East US"

# 3. Enable Microsoft Sentinel
az sentinel workspace create \
  --resource-group "rg-sentinel-lookout-dev" \
  --workspace-name "law-sentinel-lookout-dev"
```

### Clone and Set Up Local Repository
```bash
# 1. Fork the Azure Sentinel repository on GitHub
# Go to: https://github.com/Azure/Azure-Sentinel
# Click "Fork" button

# 2. Clone YOUR fork (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/Azure-Sentinel.git
cd Azure-Sentinel

# 3. Add upstream remote
git remote add upstream https://github.com/Azure/Azure-Sentinel.git

# 4. Create development branch
git checkout -b feature/lookout-v2-enhancements

# 5. Navigate to Lookout solution
cd Solutions/Lookout
```

## 🧪 Step 2: Local Component Testing

### Test Analytics Rules Syntax
```bash
# Install KQL validation tools
npm install -g @azure/kusto-language-service

# Validate each analytics rule
echo "Testing LookoutSmishingAlertV2.yaml..."
# Copy the query section and test in Azure Data Explorer or Sentinel

echo "Testing LookoutAuditEventV2.yaml..."
# Copy the query section and test in Azure Data Explorer or Sentinel
```

### Validate JSON Files
```bash
# Test workbook JSON syntax
python3 -m json.tool Workbooks/LookoutEventsV2.json > /dev/null
echo "✅ Workbook JSON is valid"

# Test solution metadata
python3 -m json.tool Data/Solution_Lookout.json > /dev/null
echo "✅ Solution metadata JSON is valid"

# Test data connector definitions
python3 -m json.tool "Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DataConnectorDefinition.json" > /dev/null
echo "✅ Data connector JSON is valid"
```

### Test YAML Files
```bash
# Install YAML validator
pip install yamllint

# Validate all YAML files
yamllint "Analytic Rules/"
yamllint "Parsers/"
yamllint "Hunting Queries/"
yamllint "Validation/"
echo "✅ All YAML files are valid"
```

## 🚀 Step 3: Deploy to Development Environment

### Method 1: Manual Component Deployment (Recommended for Testing)

#### Deploy Parser Function
```bash
# 1. Navigate to Sentinel workspace
# 2. Go to Logs (KQL editor)
# 3. Copy content from Parsers/LookoutEvents.yaml
# 4. Create the function:

.create-or-alter function LookoutEvents() {
    // Paste the KQL from LookoutEvents.yaml here
}
```

#### Deploy Analytics Rules
```bash
# 1. Go to Sentinel → Analytics → Create → Scheduled query rule
# 2. Copy settings from each YAML file:
#    - LookoutSmishingAlertV2.yaml
#    - LookoutAuditEventV2.yaml
#    - LookoutThreatEventV2.yaml (verify existing)
#    - LookoutDeviceComplianceV2.yaml (verify existing)

# 3. Test each rule with sample data
```

#### Deploy Workbook
```bash
# 1. Go to Sentinel → Workbooks → Add workbook
# 2. Click "Advanced Editor"
# 3. Paste content from Workbooks/LookoutEventsV2.json
# 4. Save as "Lookout Events V2 - DEV"
```

### Method 2: ARM Template Deployment
```bash
# 1. Create parameters file
cat > dev-parameters.json << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workspace": {
      "value": "law-sentinel-lookout-dev"
    },
    "workspace-location": {
      "value": "East US"
    }
  }
}
EOF

# 2. Deploy the solution
az deployment group create \
  --resource-group "rg-sentinel-lookout-dev" \
  --template-file "Package/mainTemplate.json" \
  --parameters @dev-parameters.json \
  --name "lookout-v2-dev-deployment"
```

## 🧪 Step 4: Generate Test Data

### Create Mock Data Ingestion
```bash
# Create a simple PowerShell script to inject test data
cat > inject-test-data.ps1 << 'EOF'
# Connect to Azure
Connect-AzAccount

# Set context
Set-AzContext -SubscriptionId "YOUR_SUBSCRIPTION_ID"

# Get workspace details
$WorkspaceId = (Get-AzOperationalInsightsWorkspace -ResourceGroupName "rg-sentinel-lookout-dev" -Name "law-sentinel-lookout-dev").CustomerId
$WorkspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKey -ResourceGroupName "rg-sentinel-lookout-dev" -Name "law-sentinel-lookout-dev").PrimarySharedKey

# Sample test data (based on TEST_DATA_SAMPLES.json)
$TestData = @'
{
  "type": "THREAT",
  "id": "test-threat-001",
  "enterprise_guid": "test-enterprise-123",
  "created_time": "2024-01-15T10:30:00.000Z",
  "change_type": "CREATE",
  "threat": {
    "id": "threat-test-001",
    "type": "MALWARE",
    "severity": "HIGH",
    "status": "OPEN",
    "action": "DETECTED"
  },
  "device": {
    "guid": "device-test-001",
    "platform": "ANDROID",
    "email_address": "test@company.com"
  }
}
'@

# Send to Log Analytics
$Body = @{
    "TimeGenerated" = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    "RawData" = $TestData
}

$BodyJson = $Body | ConvertTo-Json
$Headers = @{
    "Authorization" = "SharedKey $WorkspaceId:$WorkspaceKey"
    "Log-Type" = "LookoutMtdV2"
    "x-ms-date" = (Get-Date).ToUniversalTime().ToString("r")
}

Invoke-RestMethod -Uri "https://$WorkspaceId.ods.opinsights.azure.com/api/logs?api-version=2016-04-01" -Method Post -Body $BodyJson -Headers $Headers -ContentType "application/json"
EOF

# Run the script
powershell -File inject-test-data.ps1
```

### Alternative: Use REST API
```bash
# Create test data injection script
cat > inject-test-data.sh << 'EOF'
#!/bin/bash

WORKSPACE_ID="YOUR_WORKSPACE_ID"
WORKSPACE_KEY="YOUR_WORKSPACE_KEY"

# Test data from TEST_DATA_SAMPLES.json
TEST_DATA='{
  "type": "THREAT",
  "id": "test-threat-001",
  "enterprise_guid": "test-enterprise-123",
  "created_time": "2024-01-15T10:30:00.000Z",
  "threat": {
    "id": "threat-test-001",
    "type": "MALWARE",
    "severity": "HIGH"
  },
  "device": {
    "guid": "device-test-001",
    "platform": "ANDROID"
  }
}'

# Send to Log Analytics
curl -X POST \
  "https://${WORKSPACE_ID}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01" \
  -H "Authorization: SharedKey ${WORKSPACE_ID}:${WORKSPACE_KEY}" \
  -H "Log-Type: LookoutMtdV2" \
  -H "x-ms-date: $(date -u +%a,\ %d\ %b\ %Y\ %H:%M:%S\ GMT)" \
  -H "Content-Type: application/json" \
  -d "$TEST_DATA"
EOF

chmod +x inject-test-data.sh
./inject-test-data.sh
```

## ✅ Step 5: Run Validation Tests

### Execute Quick Validation
```bash
# 1. Open Sentinel → Logs
# 2. Copy and paste queries from Validation/QuickStartValidation.kql
# 3. Run each section step by step
# 4. Verify all components are working

# Expected results:
# ✅ Data ingestion working
# ✅ Parser extracting fields
# ✅ Analytics rules enabled
# ✅ Workbook displaying data
```

### Test Analytics Rules
```bash
# 1. Wait 5-10 minutes after data injection
# 2. Check if rules triggered:

SecurityAlert
| where TimeGenerated > ago(1h)
| where AlertName contains "Lookout"
| project TimeGenerated, AlertName, AlertSeverity, Description

# 3. If no alerts, check rule configuration and test data
```

### Test Workbook Functionality
```bash
# 1. Open "Lookout Events V2 - DEV" workbook
# 2. Verify all visualizations load
# 3. Test parameter filtering
# 4. Check for any errors or empty charts
```

## 🔧 Step 6: Troubleshooting Common Issues

### Issue: No Data Appearing
```bash
# Check raw data ingestion
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| take 10

# If empty, check:
# 1. Workspace ID and key are correct
# 2. Data injection script ran successfully
# 3. Wait 5-15 minutes for ingestion delay
```

### Issue: Parser Not Working
```bash
# Test parser function directly
LookoutEvents
| where TimeGenerated > ago(1h)
| take 5

# If error, check:
# 1. Parser function was created correctly
# 2. KQL syntax is valid
# 3. Field mappings are correct
```

### Issue: Analytics Rules Not Triggering
```bash
# Check rule query directly
LookoutEvents
| where TimeGenerated > ago(1h)
| where EventType == "THREAT"
| where ThreatSeverity in ("CRITICAL", "HIGH")

# If no results:
# 1. Verify test data has correct severity
# 2. Check field extraction
# 3. Adjust rule thresholds for testing
```

### Issue: Workbook Errors
```bash
# Common fixes:
# 1. Check parameter configuration
# 2. Verify KQL query syntax
# 3. Ensure data source permissions
# 4. Test queries individually in Logs
```

## 📦 Step 7: Package for Submission

### Validate All Components
```bash
# Run comprehensive validation
cd Solutions/Lookout

# 1. Validate file structure
echo "Checking file structure..."
ls -la "Analytic Rules/"
ls -la "Workbooks/"
ls -la "Hunting Queries/"
ls -la "Validation/"

# 2. Validate JSON syntax
echo "Validating JSON files..."
find . -name "*.json" -exec python3 -m json.tool {} \; > /dev/null
echo "✅ All JSON files valid"

# 3. Validate YAML syntax
echo "Validating YAML files..."
find . -name "*.yaml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \;
echo "✅ All YAML files valid"
```

### Create Pull Request
```bash
# 1. Commit your changes
git add .
git commit -m "feat: Add Lookout Mobile Risk API v2 enhancements

- Add SMISHING_ALERT analytics rule
- Add AUDIT event analytics rule  
- Add enhanced v2 workbook with advanced visualizations
- Add comprehensive hunting queries for threat correlation
- Add validation framework and testing documentation
- Update solution metadata with new components"

# 2. Push to your fork
git push origin feature/lookout-v2-enhancements

# 3. Create pull request on GitHub
# Go to: https://github.com/YOUR_USERNAME/Azure-Sentinel
# Click "Compare & pull request"
# Fill in description with validation results
```

### Pre-Submission Checklist
- [ ] All components tested in dev environment
- [ ] Validation queries pass successfully
- [ ] Analytics rules trigger correctly
- [ ] Workbook displays data properly
- [ ] Hunting queries execute without errors
- [ ] Documentation is complete and accurate
- [ ] JSON/YAML syntax validated
- [ ] Test data injection works
- [ ] Performance is acceptable
- [ ] No sensitive data in code

## 🎓 Step 8: Best Practices for Development

### Version Control
```bash
# Always work on feature branches
git checkout -b feature/your-enhancement

# Keep commits atomic and descriptive
git commit -m "feat: add smishing alert detection rule"
git commit -m "docs: update deployment guide"

# Sync with upstream regularly
git fetch upstream
git rebase upstream/master
```

### Testing Strategy
1. **Unit Testing**: Test individual components (rules, queries)
2. **Integration Testing**: Test complete data flow
3. **Performance Testing**: Validate query performance
4. **User Acceptance Testing**: Test workbook usability

### Documentation Standards
- Keep README files updated
- Document all configuration parameters
- Include troubleshooting guides
- Provide sample data and queries
- Add validation procedures

## 🚀 Next Steps After Development

1. **Submit Pull Request** to Azure Sentinel repository
2. **Respond to Review Feedback** from Microsoft team
3. **Update Documentation** based on feedback
4. **Monitor Solution Performance** after deployment
5. **Gather User Feedback** and iterate

---

**Remember**: This development environment is for testing only. Always clean up resources when done to avoid unnecessary costs!

```bash
# Clean up development resources
az group delete --name "rg-sentinel-lookout-dev" --yes --no-wait