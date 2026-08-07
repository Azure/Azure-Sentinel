# 🚀 Quick Start Guide - Forwarder Pickup Processor

## Quick Installation in 5 Minutes

### 1️⃣ Prerequisites (2 minutes)

```powershell
# Install Azure modules (if using Log Ingestion API)
Install-Module -Name Az.Accounts, Az.Monitor -Force -Scope CurrentUser

# Verify installation
Get-Module -Name Az.Accounts -ListAvailable
```

### 2️⃣ Configuration (1 minute)

```powershell
# Navigate to scripts folder
cd "C:\ESI\Scripts"

# Copy configuration file
Copy-Item "Config\ForwarderPickupConfig.json" "Config\ForwarderPickupConfig-BACKUP.json"

# Edit configuration
notepad "Config\ForwarderPickupConfig.json"
```

**Minimum configuration to modify:**

```json
{
    "SentinelConnection": {
        "UseLogIngestionAPI": true,
        "DataCollectionEndpointURI": "https://VOTRE-DCE.ingest.monitor.azure.com",
        "DCRImmutableId": "dcr-VOTRE-DCR-ID",
        "TenantID": "VOTRE-TENANT-ID",
        "ApplicationId": "VOTRE-APP-ID",
        "CertificateThumbprint": "VOTRE-CERT-THUMBPRINT"
    }
}
```

### 3️⃣ Configuration Test (30 seconds)

```powershell
# Test configuration
.\Test-ForwarderSetup.ps1

# Test with test file creation
.\Test-ForwarderSetup.ps1 -CreateTestFile

# Test Azure connection
.\Test-ForwarderSetup.ps1 -TestConnection
```

### 4️⃣ Scheduled Task Installation (1 minute)

```powershell
# Simple installation (15 minute interval)
.\Install-ForwarderScheduledTask.ps1

# With SYSTEM account (for Managed Identity)
.\Install-ForwarderScheduledTask.ps1 -UseSystemAccount

# With service account
.\Install-ForwarderScheduledTask.ps1 -ServiceAccount "DOMAIN\svc-esi" -IntervalMinutes 10

# Customized
.\Install-ForwarderScheduledTask.ps1 `
    -ScriptPath "C:\ESI\Scripts\ForwarderPickupProcessor.ps1" `
    -ConfigPath "C:\ESI\Scripts\Config\ForwarderPickupConfig.json" `
    -IntervalMinutes 5
```

### 5️⃣ Manual Test (30 seconds)

```powershell
# Execute manually once
.\ForwarderPickupProcessor.ps1

# Check logs
Get-Content "C:\ESI\Logs\ForwarderProcessor_*.log" | Select-Object -Last 50
```

---

## ✅ Deployment Checklist

- [ ] PowerShell modules installed
- [ ] JSON configuration edited with your values
- [ ] Configuration test successful (0 errors)
- [ ] Folders created (Pickup, Archive, Error, Logs)
- [ ] Certificate installed (if certificate authentication)
- [ ] Permissions configured on DCR/Workspace
- [ ] CollectExchSecIns.ps1 configured in forwarder mode
- [ ] Scheduled task created
- [ ] Manual test successful
- [ ] Data visible in Sentinel

---

## 🔍 Quick Verification

### Check that forwarder is working:

```powershell
# Count pending files
(Get-ChildItem "C:\ESI\ForwarderPickup" -Filter "*.json").Count

# Count archived files
(Get-ChildItem "C:\ESI\Archive" -Filter "*.json").Count

# Last task execution
Get-ScheduledTask -TaskName "ESI Forwarder Processor" | Get-ScheduledTaskInfo
```

### Check in Sentinel:

```kql
// View data from last 24 hours
ESIExchangeConfig_CL
| where TimeGenerated > ago(24h)
| summarize Count=count() by bin(TimeGenerated, 1h)
| render timechart
```

---

## 🆘 Quick Troubleshooting

### Problem: Files remain in Pickup

```powershell
# Check logs
Get-Content "C:\ESI\Logs\ForwarderProcessor_*.log" | Select-String "Error|Failed"

# Check error files
Get-ChildItem "C:\ESI\Error"

# Execute manually with verbose
.\ForwarderPickupProcessor.ps1 -Verbose
```

### Problem: Authentication error

```powershell
# Check certificate
Get-ChildItem Cert:\LocalMachine\My | Where-Object {$_.Thumbprint -eq "YOUR-THUMBPRINT"}

# Test Azure connection
Connect-AzAccount -CertificateThumbprint "THUMBPRINT" -Tenant "TENANT" -ApplicationId "APPID"
```

### Problem: Data doesn't appear in Sentinel

```powershell
# Wait 10-15 minutes for first ingestion
# Check DCR
Get-AzDataCollectionRule -Name "YourDCR"

# Check DCR streams
$dcr = Get-AzDataCollectionRule -Name "YourDCR"
$dcr.DataFlows
```

---

## 📱 Useful Commands

```powershell
# Start task manually
Start-ScheduledTask -TaskName "ESI Forwarder Processor"

# View task status
Get-ScheduledTask -TaskName "ESI Forwarder Processor" | Format-List *

# Stop task
Stop-ScheduledTask -TaskName "ESI Forwarder Processor"

# Disable temporarily
Disable-ScheduledTask -TaskName "ESI Forwarder Processor"

# Re-enable
Enable-ScheduledTask -TaskName "ESI Forwarder Processor"

# Remove task
Unregister-ScheduledTask -TaskName "ESI Forwarder Processor" -Confirm:$false
```

---

## 🎯 Recommended Production Configuration

```json
{
    "PickupFolder": "C:\\ESI\\ForwarderPickup",
    "ArchiveFolder": "D:\\ESI\\Archive",
    "ErrorFolder": "D:\\ESI\\Error",
    "LogFolder": "D:\\ESI\\Logs",
    "DeleteAfterProcessing": false,
    "MaxFilesPerRun": 100,
    "FilePattern": "*.json",
    "SentinelConnection": {
        "UseManagedIdentity": true,
        "UseLogIngestionAPI": true,
        "DataCollectionEndpointURI": "https://prod-dce.ingest.monitor.azure.com",
        "DCRImmutableId": "dcr-xxxxx",
        "MaxSegmentSizeMb": 0.9
    }
}
```

**Scheduled task:** Every 10-15 minutes  
**Archive retention:** 30 days minimum  
**Monitoring:** Alerts if ErrorFolder > 10 files  

---

## 📞 Support

- **Logs** : `C:\ESI\Logs\ForwarderProcessor_*.log`
- **Erreurs** : `C:\ESI\Error\`
- **Documentation** : `README-ForwarderPickup.md`
- **Contact** : nilepagn@microsoft.com

---

## 💡 Tips

### Automatically purge old archives:

```powershell
# Add to scheduled task or create separate task
Get-ChildItem "C:\ESI\Archive" -Filter "*.json" | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item -Force
```

### Monitoring with PowerShell:

```powershell
# Monitoring script to run every hour
$pickupCount = (Get-ChildItem "C:\ESI\ForwarderPickup" -Filter "*.json").Count
$errorCount = (Get-ChildItem "C:\ESI\Error" -Filter "*.json").Count

if ($pickupCount -gt 50) {
    Write-Warning "Too many pending files: $pickupCount"
}

if ($errorCount -gt 10) {
    Write-Error "Too many errors: $errorCount files"
}
```

### Quick statistics:

```powershell
# Number of files processed today
$today = Get-Date -Format "yyyy-MM-dd"
$processed = (Get-ChildItem "C:\ESI\Archive" | 
    Where-Object {$_.LastWriteTime.ToString("yyyy-MM-dd") -eq $today}).Count
Write-Host "Files processed today: $processed"

# Total size
$totalSize = (Get-ChildItem "C:\ESI\Archive" -Recurse | 
    Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Data processed: $([Math]::Round($totalSize, 2)) MB"
```

---

**🎉 You're ready! The forwarder is now operational.**
