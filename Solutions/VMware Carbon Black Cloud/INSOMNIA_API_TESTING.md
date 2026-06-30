# VMware Carbon Black Cloud - Insomnia/Postman API Testing Guide

This guide provides step-by-step instructions to test the Carbon Black Cloud API locally using Insomnia or Postman to validate the fixed data connector type mismatches.

## Prerequisites

- Insomnia or Postman installed
- Carbon Black Cloud API credentials (API Key + API Secret)
- Org Key from your Carbon Black Cloud tenant
- Windows Subsystem for Linux (WSL) or PowerShell (for encoding examples)

## Authentication Setup

### Step 1: Generate Carbon Black Cloud API Credentials

1. Log in to your **Carbon Black Cloud Console**
2. Navigate to **Settings** → **API Access**
3. Create a new API credential with:
   - **Credential Type**: Custom
   - **Access Level**: Select required permissions (Alerts Read, Alert Update, Audit Logs Read, etc.)
   - **Name**: e.g., "Insomnia-Tester"
4. Copy the **API Key** (Client ID) and **API Secret** (Client Secret)
5. Also note your **Organization Key** (visible in Credentials list)

### Step 2: Set Up Insomnia Environment Variables

1. In Insomnia, go to **Manage Environments**
2. Create a new environment called "Carbon Black Cloud"
3. Add these variables:
   ```json
   {
     "API_KEY": "your_api_key_here",
     "API_SECRET": "your_api_secret_here",
     "ORG_KEY": "your_org_key_here",
     "CB_HOSTNAME": "api.us.conferdeploy.net",
     "TIMESTAMP": 1700000000
   }
   ```

   **Note**: Replace hostname based on your region:
   - US: `api.us.conferdeploy.net`
   - Europe: `api.eu.conferdeploy.net`
   - Asia-Pacific: `api.apac.conferdeploy.net`

### Step 3: Generate Request Signature

Carbon Black Cloud API uses HMAC-SHA256 authentication. Generate the signature:

**For Windows PowerShell:**
```powershell
# Store your credentials
$apiKey = "your_api_key"
$apiSecret = "your_api_secret"
$orgKey = "your_org_key"
$method = "GET"
$requestURL = "/api/alerts/v3/orgs/{your_org_key}/alerts"
$timestamp = [long](Get-Date -UFormat %s)

# Create signature
$message = "$method $requestURL $apiKey $timestamp"
$hmacsha = New-Object System.Security.Cryptography.HMACSHA256
$hmacsha.Key = [Text.Encoding]::UTF8.GetBytes($apiSecret)
$signature = $hmacsha.ComputeHash([Text.Encoding]::UTF8.GetBytes($message))
$signature = [Convert]::ToBase64String($signature)

Write-Output "X-CBC-AUTH-SIGNATURE: $signature"
Write-Output "X-ANTML-TIMESTAMP: $timestamp"
```

**For Linux/Mac Bash:**
```bash
API_KEY="your_api_key"
API_SECRET="your_api_secret"
ORG_KEY="your_org_key"
METHOD="GET"
REQUEST_URL="/api/alerts/v3/orgs/${ORG_KEY}/alerts"
TIMESTAMP=$(date +%s)

MESSAGE="${METHOD} ${REQUEST_URL} ${API_KEY} ${TIMESTAMP}"
SIGNATURE=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$API_SECRET" -binary | base64)

echo "X-CBC-AUTH-SIGNATURE: $SIGNATURE"
echo "X-ANTML-TIMESTAMP: $TIMESTAMP"
```

## Testing the API Endpoints

### Test 1: Get Alerts (Validates severity field type)

**Method**: GET  
**URL**: `https://{{ CB_HOSTNAME }}/api/alerts/v3/orgs/{{ ORG_KEY }}/alerts`  
**Headers**:
```
Authorization: Bearer {{ API_KEY }}
X-CBC-AUTH-SIGNATURE: {{ SIGNATURE }}
X-ANTML-TIMESTAMP: {{ TIMESTAMP }}
Content-Type: application/json
```

**Expected Response**:
```json
{
  "success": true,
  "org_key": "your_org_key",
  "alerts": [
    {
      "alert_id": "12345",
      "severity": 5,
      "process_pid": 42036,
      "parent_pid": 13036,
      "status": "OPEN",
      "category": "MALWARE",
      "detection_sha256": "abc123...",
      "type": "CB_ANALYTICS",
      "first_event_time": "2024-10-15T10:30:00Z",
      "last_event_time": "2024-10-15T10:35:00Z",
      "threat_id": "98765",
      "device_id": "11111",
      "device_name": "DESKTOP-TEST",
      "device_os": "WINDOWS",
      "process_name": "malware.exe",
      "process_path": "C:\\temp\\",
      "threat_indicators": []
    }
  ]
}
```

**Key Fields to Validate**:
- `severity`: Should be **integer** (e.g., 5, not "5")
- `process_pid`: Should be **integer** (e.g., 42036, not "42036")
- `parent_pid`: Should be **integer** (e.g., 13036, not "13036")

### Test 2: List Watchlists

**Method**: GET  
**URL**: `https://{{ CB_HOSTNAME }}/api/threatwarriors/watchlist/v3/orgs/{{ ORG_KEY }}/watchlists`  
**Headers**: Same authentication headers as Test 1

**Expected Response** - Validates watchlist severity field:
```json
{
  "org_key": "your_org_key",
  "watchlists": [
    {
      "id": "watchlist-123",
      "name": "IOC Watchlist",
      "severity": 3,
      "description": "Important indicators",
      "create_time": 1697374800000,
      "last_update_time": 1697374800000
    }
  ]
}
```

### Test 3: Get Authentication Events

**Method**: GET  
**URL**: `https://{{ CB_HOSTNAME }}/api/audit/v1/orgs/{{ ORG_KEY }}/audit_logs`  
**Query Parameters**:
```
start_time=2024-10-01
limit=10
sort=timestamp&desc=true
```

**Expected Response** - Validates auth port/length fields:
```json
{
  "success": true,
  "org_key": "your_org_key",
  "logs": [
    {
      "timestamp": 1697374800000,
      "actor_type": "USER",
      "action": "LOGIN_SUCCESS",
      "auth_remote_port": 22,
      "auth_key_length": 2048,
      "auth_failed_logon_count": 0,
      "auth_user_id": "user@example.com",
      "status": "SUCCESS"
    }
  ]
}
```

**Key Fields to Validate**:
- `auth_remote_port`: Should be **integer** (e.g., 22, not "22")
- `auth_key_length`: Should be **integer** (e.g., 2048)
- `auth_failed_logon_count`: Should be **integer** (e.g., 0)

### Test 4: Get Endpoint Data

**Method**: GET  
**URL**: `https://{{ CB_HOSTNAME }}/api/device/v4/orgs/{{ ORG_KEY }}/devices`  
**Query Parameters**:
```
status=ACTIVE
limit=5
```

**Expected Response** - Validates endpoint count fields:
```json
{
  "success": true,
  "org_key": "your_org_key",
  "devices": [
    {
      "device_id": "11111",
      "device_name": "DESKTOP-PROD",
      "status": "ACTIVE",
      "os": "WINDOWS",
      "os_version": "10",
      "childproc_pid": 4320,
      "filemod_count": 145,
      "modload_count": 89,
      "netconn_count": 23,
      "regmod_count": 456,
      "scriptload_count": 12,
      "last_contact_time": 1697374800000,
      "device_policy_id": "policy-123"
    }
  ]
}
```

**Key Fields to Validate** (should all be integers):
- `childproc_pid`: Integer (e.g., 4320)
- `filemod_count`: Integer (e.g., 145)
- `modload_count`: Integer (e.g., 89)
- `netconn_count`: Integer (e.g., 23)
- `regmod_count`: Integer (e.g., 456)
- `scriptload_count`: Integer (e.g., 12)

## Creating a Request Collection in Insomnia

1. **Create New Request**:
   - Name: "Get CB Alerts"
   - Folder: "Carbon Black Cloud"

2. **Set Request Details**:
   - Method: `GET`
   - URL: `https://{{ CB_HOSTNAME }}/api/alerts/v3/orgs/{{ ORG_KEY }}/alerts`

3. **Add Headers**:
   - `Authorization: Bearer {{ API_KEY }}`
   - `X-CBC-AUTH-SIGNATURE: {{ SIGNATURE }}`
   - `X-ANTML-TIMESTAMP: {{ TIMESTAMP }}`
   - `Content-Type: application/json`

4. **Send Request** and inspect response

## Using Postman Alternative

**For Postman Users**:
1. Import the requests using the same URL/header format
2. Use Postman's **Pre-request Script** to generate signature:
   ```javascript
   const timestamp = Math.floor(Date.now() / 1000);
   pm.environment.set('TIMESTAMP', timestamp);
   
   // For signature generation, use online tools or Postman's built-in utilities
   // Then paste the generated SIGNATURE value
   ```

## Validating the Fix in Log Analytics

Once data flows to Log Analytics:

```kusto
// Check severity field type in CarbonBlack_Alerts_CL
CarbonBlack_Alerts_CL
| extend SeverityType = typeof(severity)
| project-keep alert_id, severity, SeverityType
| limit 10

// Check process_pid field
CarbonBlack_Alerts_CL
| extend ProcessPidType = typeof(process_pid)
| project-keep alert_id, process_pid, ProcessPidType
| limit 10

// Check parent_pid field
CarbonBlack_Alerts_CL
| extend ParentPidType = typeof(parent_pid)
| project-keep alert_id, parent_pid, ParentPidType
| limit 10

// Filter alerts by severity level (now that it's properly typed as int)
CarbonBlack_Alerts_CL
| where severity >= 7  // High severity alerts
| summarize AlertCount = count(), LatestTime = max(TimeGenerated)
  by severity, category_c
```

## Troubleshooting

### Issue: 401 Unauthorized
- Verify API Key and Secret are correct
- Ensure timestamp hasn't expired (must be within 5 minutes)
- Check organization key is valid

### Issue: 403 Forbidden
- Verify API credential has required permissions
- Check credential hasn't been revoked

### Issue: Empty Results
- Verify Org Key is correct
- Check time range includes actual data
- Ensure device/alert exists in your environment

### Issue: Fields Still Showing as String in Log Analytics
- Wait 5-10 minutes for new DCR configuration to take effect
- Verify DCR was updated correctly:
  ```kusto
  DCR
  | where name contains "CarbonBlack"
  | project streamDeclarations
  ```

## References

- [Carbon Black Cloud API Documentation](https://developer.carbonblack.com)
- [HMAC-SHA256 Authentication](https://docs.vmware.com/en/VMware-Carbon-Black-Cloud/services/carbon-black-cloud-api/GUID-2B6030FA-B0A0-4BC6-8B5D-5DB70A44FE15.html)
- [Data Connector Troubleshooting](https://docs.microsoft.com/azure/sentinel/connect-data-sources)
