# Quick Start Deployment Guide: MDO Detection & Insights Power BI Template

This guide outlines the steps to deploy the **Microsoft Defender for Office 365 Detection and Insights** template using the custom **KeyVaultConnector.mez** and an On-premises Data Gateway.

> **Prerequisites:**
> *   An **On-premises Data Gateway (Standard Mode)** must already be installed and online.
>     *   *If you do not have a gateway deployed, follow the official guide here:* [On-premises data gateway architecture | Microsoft Learn](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-onprem-indepth)
> *   The custom connector file: `KeyVaultConnector.mez`
> *   The Power BI template file: `Microsoft Defender for Office 365 Detection and Insights_v3.pbit`

---

## Phase 1: Deploy Custom Connector to Gateway

1.  **Place the Connector:**
    Copy the `KeyVaultConnector.mez` file to the custom connectors folder on the machine where your On-premises Data Gateway is running.
    *   *Default path is usually:* `C:\Users\SERVICE_ACCOUNT\Documents\Power BI Desktop\Custom Connectors` (or the specific folder configured in your gateway settings).

2.  **Restart the Gateway:**
    Open the **On-premises data gateway** app on the server and go to **Service Settings** > **Restart now** to ensure the new connector is loaded.

3.  **Enable Custom Connectors:**
    In the On-premises data gateway app, go to the **Connectors** tab.
    Ensure the folder path matches where you dropped the `.mez` file.
    **Verify** that `KeyVault` appears in the list of loaded custom connectors.

4.  **Enable in Power BI Service:**
    Go to Power BI Service (online) > **Manage connections and gateways**.
    Select your gateway cluster settings and ensure the checkbox **"Allow user's custom data connectors to refresh through this gateway cluster"** is checked.
    *   *Reference:* [Use custom data connectors with the on-premises data gateway | Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/connect-data/service-gateway-custom-connectors)

---

## Phase 2: Create Gateway Connections

You must create **3 specific connections** in the Power BI Service under your Gateway Cluster to match the data sources used by the report.

Go to **Manage connections and gateways** > **New** and configure the following three connections:

### 1. Custom KeyVault Connector
*   **Gateway cluster name:** Select your gateway (e.g., `Org_Gateway`)
*   **Connection type:** `KeyVault`
*   **URL:** `https://<YOUR_VAULT_NAME>.vault.azure.net`
    *   *Replace `<YOUR_VAULT_NAME>` with your actual Azure Key Vault name.*
*   **Authentication method:** `OAuth 2.0`
*   **Privacy level:** `Organizational`
*   *Click "Edit credentials" to sign in with an account that has permission to read secrets from this Key Vault.*

### 2. Azure Login (Web)
*   **Gateway cluster name:** Select your gateway
*   **Connection type:** `Web`
*   **URL:** `https://login.microsoftonline.com/`
*   **Authentication method:** `Anonymous` *(handled internally by the query logic)*
*   **Privacy level:** `Organizational`
*   **Skip test connection:** Checked (optional, if validation fails on root URL)

### 3. Microsoft Graph API (Web)
*   **Gateway cluster name:** Select your gateway
*   **Connection type:** `Web`
*   **URL:** `https://graph.microsoft.com/`
*   **Authentication method:** `Anonymous` *(handled internally via KeyVault token)*
*   **Privacy level:** `Organizational`
*   **Skip test connection:** Checked (optional, if validation fails on root URL)

---

## Phase 3: Publish & Configure Report

1.  **Open & Publish:**
    Open the `Microsoft Defender for Office 365 Detection and Insights_v3.pbit` in Power BI Desktop.
    When prompted, enter your **Key Vault Name** and other required parameters.
    Once loaded, click **Publish** to upload it to your Power BI Workspace.

2.  **Configure Semantic Model:**
    In Power BI Service, go to your Workspace.
    Find the **Semantic model** (dataset) for the report and click **Settings**.
    Expand **Gateway and cloud connections**.

3.  **Map Data Sources:**
    Select your gateway cluster (e.g., `MDO_Gateway`).
    **Map the data sources** to the connections you created in Phase 2:
    *   `Web{"url":"https://graph.microsoft.com/"}` -> Maps to: **Microsoft Graph API**
    *   `Web{"url":"https://login.microsoftonline.com/"}` -> Maps to: **Azure Login**
    *   `Extension{"extensionDataSourceKind":"KeyVault",...}` -> Maps to: **Custom KeyVault Connector**

    *Ensure the Status shows "Running" and click **Apply**.*

4.  **Configure Refresh:**
    Expand **Refresh**.
    Turn on **"Keep your data up to date"**.
    Set the **Refresh frequency** to `Daily` (and configure a time).
    Click **Apply**.

---
*Deployment Complete. Your report will now securely fetch secrets via the gateway and refresh automatically.*

## 🔧 Troubleshooting (quick checks)

- **Gateway refresh fails with "unknown function" or "credential" errors:**  
  - Ensure `KeyVaultConnector.mez` is deployed to the gateway machine (not just Desktop)
  - Verify custom connectors are enabled in the gateway settings
  - Check that all 3 connections (KeyVault, login.microsoftonline.com, graph.microsoft.com) are mapped in the dataset settings

