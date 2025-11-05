# Inject Test Data to Validate Changes

## Quick Test Data Injection (No Connector Needed)

### Step 1: Get Your Workspace Details

1. In Azure Portal, go to your Sentinel workspace
2. On the left menu, click **Settings**
3. Look for **Workspace ID** - copy it (looks like: `12345678-1234-1234-1234-123456789abc`)
4. Keep this page open, we'll need it

---

### Step 2: Create Test Data Using Azure Portal

The easiest way is to use the Custom Logs API directly from Azure:

1. In Sentinel, click **Logs** on the left menu
2. Click the **X** to close the query window
3. At the top right, click your account icon
4. Open **Cloud Shell** (the terminal icon `>_`)
5. Choose **PowerShell** when prompted

---

### Step 3: Run This Script in Cloud Shell

Copy and paste this entire script into Cloud Shell:

```powershell
# Your workspace name (change this to YOUR workspace name)
$WorkspaceName = "YOUR-WORKSPACE-NAME"
$ResourceGroup = "YOUR-RESOURCE-GROUP-NAME"

# Get workspace details
$Workspace = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroup -Name $WorkspaceName
$WorkspaceId = $Workspace.CustomerId
$WorkspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKey -ResourceGroupName $ResourceGroup -Name $WorkspaceName).PrimarySharedKey

# Test data samples
$TestEvents = @(
    @{
        event_type = "THREAT"
        id = "test-threat-001"
        enterprise_guid = "test-enterprise"
        change_type = "CREATE"
        device_guid = "device-001"
        device_platform = "ANDROID"
        device_email_address = "test@company.com"
        device_activation_status = "ACTIVE"
        threat_id = "threat-001"
        threat_type = "MALWARE"
        threat_severity = "HIGH"
        threat_status = "OPEN"
        threat_action = "DETECTED"
    },
    @{
        event_type = "SMISHING_ALERT"
        id = "test-smishing-001"
        enterprise_guid = "test-enterprise"
        change_type = "CREATE"
        device_guid = "device-002"
        device_platform = "IOS"
        device_email_address = "user@company.com"
        smishing_alert_id = "smish-001"
        smishing_alert_type = "PHISHING"
        smishing_alert_severity = "CRITICAL"
        smishing_alert_description = "Suspicious SMS detected"
    },
    @{
        event_type = "AUDIT"
        id = "test-audit-001"
        enterprise_guid = "test-enterprise"
        change_type = "UPDATE"
        audit_type = "POLICY_CHANGE"
        actor_type = "ADMIN"
        actor_guid = "admin-001"
    }
)

# Function to send data to Log Analytics
function Send-LogAnalyticsData {
    param($CustomerId, $SharedKey, $Body, $LogType)
    
    $TimeStampField = ""
    $json = $Body | ConvertTo-Json -Depth 10
    $jsonBytes = [Text.Encoding]::UTF8.GetBytes($json)
    $contentLength = $jsonBytes.Length
    
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    $signature = Build-Signature -customerId $CustomerId -sharedKey $SharedKey -date $rfc1123date -contentLength $contentLength -method "POST" -contentType "application/json" -resource "/api/logs"
    
    $uri = "https://" + $CustomerId + ".ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    
    $headers = @{
        "Authorization" = $signature
        "Log-Type" = $LogType
        "x-ms-date" = $rfc1123date
        "time-generated-field" = $TimeStampField
    }
    
    Invoke-RestMethod -Uri $uri -Method Post -ContentType "application/json" -Headers $headers -Body $json
}

function Build-Signature {
    param($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
    
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
    
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)
    
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    
    return "SharedKey ${customerId}:${encodedHash}"
}

# Send test events
Write-Host "Injecting test data..." -ForegroundColor Green
foreach ($event in $TestEvents) {
    Send-LogAnalyticsData -CustomerId $WorkspaceId -SharedKey $WorkspaceKey -Body $event -LogType "LookoutMtdV2"
    Write-Host "  ✓ Sent $($event.event_type) event" -ForegroundColor Cyan
}

Write-Host "`nTest data injected successfully!" -ForegroundColor Green
Write-Host "Wait 5-10 minutes for data to appear in Sentinel" -ForegroundColor Yellow
```

---

### Step 4: Update the Script Variables

Before running, change these lines at the top:
```powershell
$WorkspaceName = "YOUR-WORKSPACE-NAME"      # Change this
$ResourceGroup = "YOUR-RESOURCE-GROUP-NAME"  # Change this
```

To find these values:
- **WorkspaceName**: In Sentinel, click **Settings** → look at the top
- **ResourceGroup**: Same page, you'll see it listed

---

### Step 5: Wait and Verify

1. **Wait 5-10 minutes** for data to ingest
2. Go back to **Logs**
3. Run this query:

```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, event_type, device_guid, threat_severity
```

You should see 3 test events!

---

### Step 6: Create the Parser Function

Once you see the test data, create the parser:

1. Still in **Logs**, run this command:

```kql
.create-or-alter function LookoutEvents() {
    LookoutMtdV2_CL
    | extend 
        EventType = event_type,
        EventId = id,
        DeviceGuid = device_guid,
        DevicePlatform = device_platform,
        DeviceEmailAddress = device_email_address,
        ThreatId = threat_id,
        ThreatType = threat_type,
        ThreatSeverity = threat_severity,
        SmishingAlertId = smishing_alert_id,
        SmishingAlertType = smishing_alert_type,
        AuditType = audit_type
}
```

2. You should see a success message

---

### Step 7: Test Everything

Now run the validation query:

```kql
LookoutEvents
| where TimeGenerated > ago(1h)
| summarize count() by EventType
```

**Expected result:**
- THREAT: 1
- SMISHING_ALERT: 1  
- AUDIT: 1

---

## If You Don't Have Cloud Shell Access

Use this simpler method in **Logs**:

```kql
// Manually create test records
let TestData = datatable(
    event_type:string, 
    device_guid:string, 
    threat_severity:string
)
[
    "THREAT", "device-001", "HIGH",
    "SMISHING_ALERT", "device-002", "CRITICAL",
    "AUDIT", "device-003", ""
];
TestData
| extend TimeGenerated = now()
```

This won't persist, but lets you test queries.

---

**Need help?** Tell me which step failed and I'll guide you through it.
