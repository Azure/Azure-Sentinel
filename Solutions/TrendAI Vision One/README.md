# Trend Vision One - Microsoft Sentinel Data Connectors

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Workbench Alerts** &nbsp; [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FcreateUiDefinition.json) [![Deploy to Azure US Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FcreateUiDefinition.json)

**OAT (Observed Attack Techniques)** &nbsp; [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FcreateUiDefinition.json) [![Deploy to Azure US Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FcreateUiDefinition.json)

### Test Deploy (Azure Storage-hosted, while repo is private)

Templates served from a public Azure Blob container so the portal can fetch them without GitHub auth. Remove once the repo goes public.

**Before clicking the buttons below, publish the latest templates to the blob container** so the deploy URLs serve current code.

**One-time setup** (per developer):

```bash
# 1. Install Azure CLI if you don't have it
#    macOS:  brew install azure-cli
#    Linux:  https://learn.microsoft.com/cli/azure/install-azure-cli-linux

# 2. Log in and select the subscription that owns the trendaiccf45 storage account
az login
az account set --subscription "<subscription-name-or-id>"
```

Required access: at least **Contributor** (or **Storage Account Key Operator Service Role**) on the `trendaiccf45` storage account, so `az storage account keys list` works. If you only have data-plane access, use a SAS token instead — see [scripts/publish-templates.sh](scripts/publish-templates.sh).

**Each time you change templates**, publish them:

```bash
export AZURE_STORAGE_KEY="$(az storage account keys list \
  --account-name trendaiccf45 \
  --query '[0].value' -o tsv)"

./scripts/publish-templates.sh
```

The script stages `templates/`, rewrites the nested `baseUrl` from the GitHub raw URL to the blob URL, and uploads to `trendaiccf45/arm-templates/`.

**Workbench Alerts** &nbsp; [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Ftrendaiccf45.blob.core.windows.net%2Farm-templates%2Fworkbench%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Ftrendaiccf45.blob.core.windows.net%2Farm-templates%2Fworkbench%2FcreateUiDefinition.json)

**OAT (Observed Attack Techniques)** &nbsp; [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Ftrendaiccf45.blob.core.windows.net%2Farm-templates%2Foat%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Ftrendaiccf45.blob.core.windows.net%2Farm-templates%2Foat%2FcreateUiDefinition.json)

Production-ready data connectors for ingesting **Trend Vision One** security data into **Microsoft Sentinel** using Azure's Codeless Connector Platform (CCP).

## 🚀 Quick Deploy

Choose the connector you need and click the Deploy button above:

| Connector | Description | Data Volume | Deploy |
|-----------|-------------|-------------|--------|
| **Workbench Alerts** | Security incidents, investigations, and alerts with IOC extraction | Medium | [Deploy to Azure](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Fworkbench%2FcreateUiDefinition.json) |
| **OAT (Observed Attack Techniques)** | MITRE ATT&CK mapped detections with full process trees | High | [Deploy to Azure](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Ftrendmicro%2Ftrendai-sentinel-ccf-data-connector%2Fmain%2Ftemplates%2Foat%2FcreateUiDefinition.json) |

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ **Azure Subscription** with Owner or Contributor role
- ✅ **Log Analytics Workspace** with Microsoft Sentinel enabled (or workspace will be enabled during deployment)
- ✅ **Trend Vision One API Token** with 'SIEM' role permissions

### Getting Your API Token

1. Log in to **Trend Vision One Console**
2. Navigate to **Administration → API Keys**
3. Click **Generate New API Key**
4. Select role: **SIEM** or **Workbench**
5. Copy the token (you'll need it after deployment)

## 🎯 Deployment Process

### Step 1: Click Deploy Button

Click one of the blue/green Deploy buttons above

### Step 2: Fill Azure Portal Form

The custom deployment UI will appear with:
- **Subscription** - Select your Azure subscription
- **Resource Group** - Select or create new
- **Workspace** - Dropdown of your Sentinel workspaces
- **Region** - Your Trend Vision One region (US, UK, SG, CA, JP)

### Step 3: Deploy Resources

Azure will automatically deploy:
1. Microsoft Sentinel solution (if not enabled)
2. Custom log table (TrendMicro_XDR_WORKBENCH_CL or TrendMicro_XDR_OAT_CL)
3. Data Collection Endpoint (DCE)
4. Data Collection Rule (DCR) with data transformation
5. Connector definition in Sentinel portal
6. Parser function (Workbench: `TrendMicroWorkbench_Complete`, OAT: `TrendMicroOAT_Complete`)
7. Analytic rule template (disabled by default)
8. Workbook dashboard for monitoring

⏱️ **Deployment time**: 3-5 minutes

### Step 4: Connect the Data Source

After deployment completes:

1. Navigate to **Microsoft Sentinel → Data connectors**
2. Search for **"Trend Vision One - Workbench"** or **"Trend Vision One - OAT"**
3. Click **Open connector page**
4. Enter your API token (include `Bearer ` prefix)
5. Click **Connect**

🎉 **Data will start flowing in 5-10 minutes!**

### Step 5: Enable Analytic Rules (Optional)

Each connector includes an **Analytic Rule** that automatically creates incidents:

1. Navigate to **Microsoft Sentinel → Analytics**
2. Search for **"Trend Vision One"**
3. Find the rule:
   - **Workbench**: "Create Incident for Workbench Alerts"
   - **OAT**: "Create Incident for High-Risk OAT Detections"
4. Click the rule → **Edit** → **Enable** → **Save**

**What it does:**
- Runs every 5 minutes
- Creates incidents with mapped entities (Account, File, Process, IP, Host)
- Groups related alerts by WorkbenchID/EventID
- Adds custom details for investigations

### Step 6: View Dashboards (Optional)

Each connector includes a **Workbook** dashboard:

1. Navigate to **Microsoft Sentinel → Workbooks**
2. Click **My workbooks** tab
3. Find:
   - **Workbench**: "TrendVisionOneWorkbenchOverview"
   - **OAT**: "TrendVisionOneOATOverview"
4. Click **View saved workbook**

**Visualizations include:**
- Alert/Detection trends over time
- Severity/Risk level distribution
- Top affected hosts/endpoints
- MITRE ATT&CK tactics and techniques (OAT only)
- Detection model usage (Workbench only)

## 📊 Verify Data Ingestion

### Workbench Alerts

```kql
TrendMicro_XDR_WORKBENCH_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, workbenchId_s, severity_s, workbenchName_s
| take 10
```

### OAT Detections

```kql
TrendMicro_XDR_OAT_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, entityType_s, detail_endpointHostName_s, detail_filterRiskLevel_s
| take 10
```

## 🏗️ Architecture

This solution follows Microsoft's recommended **modular architecture** pattern:

```
mainTemplate.json (Orchestrator)
  ├─> sentinel-solution.json      # Enables Sentinel
  ├─> table.json                  # Creates custom table
  ├─> dce.json                    # Data Collection Endpoint
  ├─> dcr.json                    # Data Collection Rule (transforms data)
  ├─> connector-definition.json   # Connector UI in portal
  ├─> parser-function.json        # KQL parser (Workbench + OAT; universal old+new)
  ├─> analytic-rule.json          # Incident creation rule (disabled)
  └─> workbook.json               # Monitoring dashboard
```

**Benefits:**
- ✅ Single-click deployment via Azure Portal
- ✅ Each component can be updated independently
- ✅ Easy to troubleshoot and maintain
- ✅ Follows Microsoft Sentinel best practices

## 📖 Data Schemas

### Workbench Alerts (56 columns)

| Category | Fields |
|----------|--------|
| **Core** | workbenchId_s, severity_s, investigationStatus_s, alertProvider_s |
| **IOCs** | FileName_s, FileHashValue_s, IPAddress, DomainName_s, URL_s |
| **Entities** | HostHostName_s, UserAccountName_s, MailboxPrimaryAddress_s |
| **Dynamic** | indicators, entities, matchedRules (for advanced parsing) |

### OAT Detections (139 columns)

| Category | Fields |
|----------|--------|
| **Core** | entityType_s, entityName_s, detectionTime_t |
| **Endpoint** | endpoint_name_s, endpoint_guid_g, endpoint_ips_s |
| **Process** | detail_processCmd_s, detail_processFileHashSha256_s, detail_processPid_d |
| **Parent** | detail_parentCmd_s, detail_parentFileHashSha256_s, detail_parentName_s |
| **Network** | detail_src_s, detail_dst_s, detail_dpt_d, detail_spt_d |
| **File** | detail_fileName_s, detail_fileHash_s, detail_filePathName_s |

## 🔍 Sample Queries

### Workbench: High Severity Alerts with File IOCs

```kql
TrendMicroWorkbench_Complete()
| where severity_s in ("high", "critical")
| where isnotempty(FileHashValue_s)
| project TimeGenerated, workbenchName_s, FileName_s, FileHashValue_s, HostHostName_s
```

### OAT: Credential Dumping Detection

```kql
TrendMicro_XDR_OAT_CL
| where detail_filterRiskLevel_s == "high"
| where detail_eventName_s contains "Credential"
| project TimeGenerated, 
    Endpoint = detail_endpointHostName_s,
    Process = detail_processName_s,
    CommandLine = detail_processCmd_s,
    SHA256 = detail_processFileHashSha256_s
```

### OAT: Process Tree Analysis

```kql
TrendMicro_XDR_OAT_CL
| where isnotempty(detail_processName_s)
| project TimeGenerated,
    Endpoint = detail_endpointHostName_s,
    Process = detail_processName_s,
    Parent = detail_parentName_s,
    CommandLine = detail_processCmd_s
```

## 🌍 Supported Regions

| Region | Value | API Endpoint |
|--------|-------|--------------|
| United States | `US` | api.xdr.trendmicro.com |
| United Kingdom / EU | `UK` | api.uk.xdr.trendmicro.com |
| Singapore / APAC | `SG` | api.sg.xdr.trendmicro.com |
| Canada | `CA` | api.ca.xdr.trendmicro.com |
| Japan | `JP` | api.jp.xdr.trendmicro.com |

## 📁 Repository Structure

```
templates/
├── workbench/              # Workbench Alerts connector (modular)
│   ├── mainTemplate.json
│   ├── createUiDefinition.json
│   └── components/         # 6 modular components
│
├── oat/                    # OAT connector (modular)
│   ├── mainTemplate.json
│   ├── createUiDefinition.json
│   └── components/         # modular components (incl. parser-function.json)
│
├── legacy/                 # Archived old templates
└── ARCHITECTURE.md         # Detailed architecture documentation
```

## 🛠️ Advanced Deployment

### Using Azure CLI

**Workbench:**
```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates/workbench/mainTemplate.json \
  --parameters workspace=<workspace-name> trendaiRegion=US
```

**OAT:**
```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates/oat/mainTemplate.json \
  --parameters workspace=<workspace-name> trendaiRegion=US
```

### Testing Individual Components

Each component can be deployed independently for testing:

```bash
# Deploy just the custom table
az deployment group create \
  --template-file templates/workbench/components/table.json \
  --parameters workspace=test-ws workspace-location=eastus
```

## 🔧 Troubleshooting

### No data after 10 minutes

1. **Check API token**: Verify token has 'SIEM' role permissions
2. **Check region**: Ensure correct Trend Vision One region selected
3. **Check connector status**: Sentinel → Data connectors → View connector health
4. **Check DCR ingestion**: Azure Monitor → Data Collection Rules → View metrics

### Connection fails

- Ensure API token includes `Bearer ` prefix
- Regenerate API token if expired
- Verify workspace has Sentinel enabled

### Missing IOC fields (Workbench)

- Use the parser function: `TrendMicroWorkbench_Complete()`
- Parser extracts IOCs from dynamic columns automatically

## 📚 Documentation

New here? Start with the **[docs/](docs/)** folder — detailed, plain-language guides written for every experience level:

- [Docs home](docs/README.md) — the map of all guides
- [Concepts — how it all fits together](docs/01-concepts.md) — what this is and *why* it's built this way
- [Permissions you need (and why)](docs/02-permissions.md) — every Azure & Trend Vision One permission, explained
- [Deploying the connector](docs/03-deployment.md) — step-by-step, portal and CLI
- [Using the connector day to day](docs/04-using-the-connector.md) — verify data, query, alerts, dashboards, filters
- [Migrating from the old connector](docs/05-migration.md) — move off the old Azure Function connector safely
- [Troubleshooting](docs/06-troubleshooting.md) — fix the common problems

Deeper / maintainer references:

- [Architecture Details](templates/ARCHITECTURE.md) — deep dive into component design
- [Internal test-deploy notes](docs/internal/test-deploy.md) — 🔒 maintainers only, removed before going public

## 🤝 Support

- **Trend Vision One API**: [Trend Micro Support](https://www.trendmicro.com/support)
- **Azure Sentinel**: [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel)
- **Issues**: [GitHub Issues](https://github.com/trendmicro/trendai-sentinel-ccf-data-connector/issues)
- **Contributing**: see [CONTRIBUTING.md](CONTRIBUTING.md)

## 🤝 Contributing

Pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🔒 Security

Found a vulnerability? Please **do not** open a public issue — see [SECURITY.md](SECURITY.md) for the private reporting process.

## 📝 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

## 🏆 Credits

Built following Microsoft's [Codeless Connector Platform (CCP)](https://learn.microsoft.com/azure/sentinel/create-codeless-connector) best practices and [SentinelOne reference implementation](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp).

---

**Version**: 2.0.0  
**Last Updated**: May 2026  
**Maintained by**: Trend Micro
