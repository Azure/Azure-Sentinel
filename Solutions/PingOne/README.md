# Ping Identity – PingOne Audit Logs CCP Connector

## **Summary**

This Microsoft Sentinel data connector enables ingestion of **audit activity logs** from **PingOne** via the CCP framework. These logs capture administrative actions, configuration changes, sign-in attempts, and other audit-relevant events across the PingOne platform.

This solution helps security teams monitor identity infrastructure for suspicious behavior, policy violations, and compliance-relevant changes by sending normalized audit data to **Microsoft Sentinel** in near real-time.

---

## **Features**

- Connects to the **PingOne Audit Activities API**.
- Parses and ingests audit logs into the custom Log Analytics table: `PingOne_AuditActivities_CL`.
- Uses secure **OAuth 2.0 Client Credentials** for authentication.
- Integrates into Sentinel analytics, hunting queries, and incident detection.

---

## **Prerequisites**

1. A valid **PingOne** tenant.
2. A **Client Credentials** application in PingOne with:  
   - **Client ID**
   - **Client Secret**
   - **Environment ID**
   - Scope: `p1:read:audit` (Audit role added via custom roles, **Environment Admin** from predefined roles and additional roles like others suitable for your needs)
   [refer to section below to generate credentials]
3. Access to an Azure subscription with **Microsoft Sentinel** enabled and permissions to deploy Data Connectors.

---

## **Generating PingOne OAuth Client Credentials**

1. Sign into the *PingOne Identity portal*
2. Go to **Connections > Applications**.
3. Click **Add Application** and select **Client Credentials**.
4. Assign the required scope:
  * `p1:read:audit`(Audit role added via custom roles)
  * Assign **Environment Admin** role from predefined roles.
  * Can add other suitable roles according to your needs,
  * without adding the roles, logs would not be ingested.
7. Save the following values:
   - **Client ID**
   - **Client Secret**
   - **Environment ID** (available in the PingOne URL or Environment settings)

These credentials are required for connector deployment.

---

## **Deployment Instructions**

Click the button below to deploy the connector using an ARM template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/YOUR-DEPLOYMENT-URL-HERE)

### **Deployment Parameters**

- **Client ID**
- **Client Secret**
- **Environment ID**

Once deployed, the connector will begin ingesting audit logs from PingOne and send them to the `PingOne_AuditActivities_CL` table in your Sentinel workspace.

---

## **Post-Deployment Steps**

### **Assign Required Roles**

Ensure the deployed Data Connector has the required permissions to write to Log Analytics:

1. Go to **Microsoft Sentinel** > **Configuration** > **Data Connectors**.
2. Find the PingOne connector in the list and open it.
3. Ensure the connector has appropriate permissions to send data to your **Log Analytics Workspace**.

---

## **How Logs are Generated**

The **PingOne Audit Logs** are automatically ingested into **Microsoft Sentinel** whenever an activity is triggered in the **PingOne Admin Console**. These logs capture a wide range of events, including but not limited to:

- **User Sign-ins**: Every sign-in attempt to the PingOne platform will generate an event that logs details such as the time, IP address, user identity, and result successful.