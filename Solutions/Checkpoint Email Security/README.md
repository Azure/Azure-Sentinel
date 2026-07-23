# Check Point Email Security Solution for Microsoft Sentinel

## Overview

The Check Point Email Security (Harmony Email & Collaboration) solution for Microsoft Sentinel enables you to ingest security events and audit logs from Check Point's Email Security platform using the Codeless Connector Framework (CCF). This connector provides visibility into advanced email threats including:

## Data Collected

The connector ingests data into four custom tables in your Log Analytics workspace:

- Security events including phishing, malware, DLP, and other threat detections with severity levels, confidence indicators, and remediation actions
- Anti-phishing whitelist and exception rules configured in your tenant
- Spam whitelist and exception rules configured in your tenant
- Administrative actions and system events including login/logout, configuration changes, and other audit trail data

### Key Fields in Security Events

- **EventType** - Type of security event (dlp, phishing, malware, etc.)
- **Severity** - Severity level (Low, Medium, High, Highest)
- **ConfidenceIndicator** - Detection confidence (malicious, suspicious)
- **SenderAddress** - Email sender associated with the event
- **State** - Current event state (active, dismissed)
- **Saas** - Source platform (office365_emails, gmail)

## Prerequisites

Before configuring the connector, you need:

1. **Microsoft Sentinel workspace** with read and write permissions
2. **Check Point Infinity Portal account** with access to:
   - Harmony Email & Collaboration service
   - Logs as a Service capability

### API Credentials Required

You need **two separate API keys** from the Check Point Infinity Portal:

| Credential | Service | Purpose |
|------------|---------|---------|
| Client ID + Client Secret | Harmony Email & Collaboration | Security events and exceptions |
| Audit Client ID + Audit Client Secret | Logs as a Service | Audit logs |

## How to Connect

### Step 1: Generate API Keys in Check Point Infinity Portal

1. Log in to your [Check Point Infinity Portal](https://portal.checkpoint.com)
2. Navigate to **Global Settings** > **API Keys**
3. Create the first API key:
   - Select service: **Harmony Email & Collaboration**
   - Save the **Client ID** and **Client Secret**
4. Create the second API key:
   - Select service: **Logs as a Service**
   - Save the **Audit Client ID** and **Audit Client Secret**

### Step 2: Identify Your API Base URL

The API Base URL is region-specific. Use the appropriate URL for your tenant:

| Region | API Base URL |
|--------|--------------|
| US | `https://cloudinfra-gw.portal.checkpoint.com` |
| EU | `https://cloudinfra-gw-eu.portal.checkpoint.com` |
| AP | `https://cloudinfra-gw-ap.portal.checkpoint.com` |

### Step 3: Configure the Connector in Microsoft Sentinel

1. In Microsoft Sentinel, navigate to **Data connectors**
2. Search for **Check Point Email Security (via Codeless Connector Framework)**
3. Click **Open connector page**
4. Click **Add Connection**
5. Enter the following:
   - **API Base URL** - Your region-specific base URL
   - **Client ID** - From Harmony Email & Collaboration API key
   - **Client Secret** - From Harmony Email & Collaboration API key
   - **Audit Client ID** - From Logs as a Service API key
   - **Audit Client Secret** - From Logs as a Service API key
6. Click **Connect**

### Multi-Tenant Support

This connector supports ingesting data from multiple Check Point Email Security tenants. To add additional tenants, click **Add Connection** and provide the credentials for each tenant separately.


## Resources

- [Check Point Harmony Email & Collaboration Documentation](https://www.checkpoint.com/harmony/email-security/)