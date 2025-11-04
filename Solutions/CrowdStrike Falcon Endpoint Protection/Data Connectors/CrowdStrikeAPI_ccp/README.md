# CrowdStrike Falcon – API Data Connector (CCP Framework)

## **Summary**

This Microsoft Sentinel data connector enables ingestion of **security data** from **CrowdStrike Falcon**  Platform. The connector captures alerts, detections, incidents, host information, and vulnerability data from the CrowdStrike Falcon platform, providing comprehensive endpoint protection visibility.

This solution helps security teams monitor endpoints for threats, track security incidents, and maintain visibility into their security posture by sending normalized security data to **Microsoft Sentinel** in near real-time.

---

## **Features**

- Connects to the **CrowdStrike Falcon REST API** using OAuth2 authentication.
- Ingests five types of security data into custom Log Analytics tables:
  - `CrowdStrikeAlerts` - Security alerts and threat notifications
  - `CrowdStrikeDetections` - Threat detections and behavioral analysis
  - `CrowdStrikeIncidents` - Security incidents and investigations
  - `CrowdStrikeHosts` - Endpoint device information and status
  - `CrowdStrikeVulnerabilities` - Vulnerability data from Falcon Spotlight
- Uses secure **OAuth 2.0 Client Credentials** for authentication with automatic token refresh.
- Supports DCR-based ingestion time transformations for optimized query performance.
- Integrates seamlessly with Sentinel analytics, hunting queries, and incident detection.

---

## **Prerequisites**

1. A valid **CrowdStrike Falcon** tenant with administrative access.
2. An **API Client** configured in CrowdStrike Falcon with:  
   - **Client ID**
   - **Client Secret**
   - **Base URL** (region-specific)
3. Appropriate API scopes assigned to the client (see scope requirements below).
4. Access to an Azure subscription with **Microsoft Sentinel** enabled and permissions to deploy Data Connectors.
5. Permissions to create and configure Data Collection Rules (DCR) in the target workspace.

---

## **Generating CrowdStrike Falcon API Credentials**

### **1. Access the Falcon Console**
1. Sign into the **CrowdStrike Falcon console**.
2. Navigate to **Support & Resources** → **API clients and keys**.

### **2. Create API Client**
1. Click **Create/Add new API client**.
2. Provide a descriptive **name** and **description** for the connector.
3. Select the required **scopes** based on the data types you want to ingest:

### **Required API Scopes by Data Type**

| **Data Type** | **CrowdStrike Scope** | **Description** |
|---------------|----------------------|-----------------|
| Alerts | `alerts:read` | Read access to security alerts |
| Detections | `detects:read` | Read access to threat detections |
| Hosts | `hosts:read` | Read access to endpoint device information |
| Incidents | `incidents:read` | Read access to security incidents |
| Vulnerabilities | `spotlight-vulnerabilities:read` | Read access to Falcon Spotlight vulnerability data |

**Note**: You can grant only the scopes for the data types you need. If you want all data types, grant all scopes listed above.

### **3. Configure API Client**
1. After creating the client, note the **Client ID** and **Client Secret** (the secret is displayed only once).
2. Identify your **Base URL** based on your CrowdStrike cloud region:

### **Base URLs by Region**

| **Region** | **Base URL** |
|------------|--------------|
| US-1 | `https://api.crowdstrike.com` |
| US-2 | `https://api.us-2.crowdstrike.com` |
| EU-1 | `https://api.eu-1.crowdstrike.com` |
| US-GOV-1 | `https://api.laggar.gcw.crowdstrike.com` |

### **4. Save Credentials**
Save the following values for connector deployment:
- **Client ID**
- **Client Secret**
- **Base URL** (from the table above)

---

## **Deployment Parameters**

When deploying the connector, you'll need to provide:

- **Base API URL**: Your region-specific CrowdStrike API endpoint
- **Client ID**: The API client identifier from CrowdStrike
- **Client Secret**: The API client secret from CrowdStrike

### **Example Configuration**
```
Base API URL: https://api.us-2.crowdstrike.com
Client ID: a1b2c3d4e5f6g7h8i9j0
Client Secret: [Your secure client secret]
```

---

## **Deployment Instructions**

### **1. Deploy the Connector**
1. Go to **Microsoft Sentinel** → **Data Connectors**.
2. Search for "**CrowdStrike API Data Connector (via Codeless Connector Framework)**".
3. Click **Open connector page**.
4. Under **Configuration**, enter your CrowdStrike credentials:
   - **Base API URL** (region-specific)
   - **Client ID**
   - **Client Secret**
5. Click **Connect**.

### **2. Verify Connection**
- The connector status should show as **Connected** within a few minutes.
- Data ingestion typically begins within 5-10 minutes of successful connection.

---

## **Post-Deployment Steps**

### **1. Verify Data Ingestion**
After deployment, verify that data is flowing into Microsoft Sentinel:

1. Go to **Microsoft Sentinel** → **Logs**.
2. Run sample queries to check for data in each table:

```kql
// Check CrowdStrike Alerts
CrowdStrikeAlerts
| take 10

// Check CrowdStrike Detections  
CrowdStrikeDetections
| take 10

// Check CrowdStrike Incidents
CrowdStrikeIncidents
| take 10

// Check CrowdStrike Hosts
CrowdStrikeHosts
| take 10

// Check CrowdStrike Vulnerabilities
CrowdStrikeVulnerabilities
| take 10
```

### **2. Monitor Connector Health**
- Check the connector status regularly in the **Data Connectors** page.
- Monitor ingestion metrics and error logs for any issues.

---

## **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Authentication Errors (403 Forbidden)**
- **Cause**: Insufficient API scopes or incorrect credentials.
- **Solution**: 
  - Verify the Client ID and Client Secret are correct.
  - Ensure all required scopes are granted to the API client.
  - Check that the API client is enabled in CrowdStrike.

#### **2. No Data Ingestion**
- **Cause**: Incorrect Base URL or network connectivity issues.
- **Solution**:
  - Confirm the Base URL matches your CrowdStrike region.
  - Verify outbound connectivity to the CrowdStrike API endpoints.
  - Check for any firewall or proxy restrictions.

#### **3. Token Expiry Errors**
- **Cause**: Normal OAuth2 token lifecycle (tokens expire ~30 minutes).
- **Solution**: 
  - This is expected behavior; the connector automatically refreshes tokens.
  - Ensure system time synchronization is accurate.
  - Verify continuous outbound access to the token endpoint.


### **Support Resources**
- **CrowdStrike API Documentation**: Available in the Falcon console under API documentation
- **Microsoft Sentinel Documentation**: [Microsoft Learn - Sentinel Connectors](https://docs.microsoft.com/azure/sentinel/)
- **Connector Logs**: Available in the Azure portal under the data connector monitoring section

---
