# PingOne

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-20 |
| **Last Updated** | 2025-04-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Ping One (via Codeless Connector Framework)](../connectors/pingoneauditlogsccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PingOne_AuditActivitiesV2_CL`](../tables/pingone-auditactivitiesv2-cl.md) | [Ping One (via Codeless Connector Framework)](../connectors/pingoneauditlogsccpdefinition.md) | - |

## Additional Documentation

> 📄 *Source: [PingOne/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne/README.md)*

# Ping Identity – PingOne Audit Logs CCP Connector

## **Summary**

This Microsoft Sentinel data connector enables ingestion of **audit activity logs** from **PingOne** via the CCP framework. These logs capture administrative actions, configuration changes, sign-in attempts, and other audit-relevant events across the PingOne platform.

This solution helps security teams monitor identity infrastructure for suspicious behavior, policy violations, and compliance-relevant changes by sending normalized audit data to **Microsoft Sentinel** in near real-time.

---

## **Features**

- Connects to the **PingOne Audit Activities API**.
- Parses and ingests audit logs into the custom Log Analytics table: `PingOne_AuditActivitiesV2_CL`.
- Uses secure **OAuth 2.0 Client Credentials** for authentication.
- Integrates into Sentinel analytics, hunting queries, and incident detection.

---

## **Prerequisites**

1. A valid **PingOne** tenant.
2. A **Client Credentials** application in PingOne with:  
   - **Client ID**
   - **Client Secret**
   - **Environment ID**
   - **APi domain**
3. Necessary roles are manadatory to generate tokens and view Audit logs.
4. Access to an Azure subscription with **Microsoft Sentinel** enabled and permissions to deploy Data Connectors.
   
---

## **Generating PingOne OAuth Client Credentials**

1. Sign into the *PingOne Identity portal*
2. Go to **Connections > Applications**.
3. Click **Add Application** and select your preferred app.
4. Assign the required roles: 
  * `p1:read:audit`(Audit role added via custom roles)
  * Assign **Environment Admin** role from predefined roles. (Needed to generate token)
  * Can add other suitable roles according to your needs,
  * without adding the roles, logs would not be ingested.
  
5. Ensure the token auth method in OIDC settings is  'Client Secret Post'  enabled in configaration section of App.
6. The grant type in OIDC settings should be 'Client Credentials'
7. Ensure the application is enabled.
8. Save the following values:
   - **Client ID**
   - **Client Secret**
   - **Environment ID** (available in the PingOne URL or Environment settings)
   - **Api domain** ( available in the PingOne URL )

These credentials are required for connector deployment.

---

### **Deployment Parameters**

- **Client ID**
- **Client Secret**
- **Environment ID**
- **Api domain**

Once deployed, the connector will begin ingesting audit logs from PingOne and send them to the `PingOne_AuditActivitiesV2_CL` table in your Sentinel workspace.

---

## **Post-Deployment Steps**

### **Assign Required Roles**

Ensure the deployed Data Connector has the required permissions to write to Log Analytics:

1. Go to **Microsoft Sentinel** > **Configuration** > **Data Connectors**.
2. Find the PingOne connector in the list and open it.
3. Ensure the connector has appropriate permissions to send data to your **Log Analytics Workspace**.

---

## **How Logs are Generated**


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------| 
| 3.0.2       | 14-08-2025                     | PingOne **CCF Data Connector** moving to GA		                  	      | 
| 3.0.1       | 23-07-2025                     | Update to **CCF Data Connector** Readme File Link                  	      |        
| 3.0.0       | 23-06-2025                     | Initial Solution release with one **CCF Data Connector**                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
