# blacklens.io

The **blacklens.io Microsoft Sentinel integration** allows you to ingest all related alerts about your Attack Surface directly in Microsoft Sentinel.

**blacklens.io** is a comprehensive **Attack Surface Management (ASM)** platform that helps organizations understand and secure their external attack surface. By combining automated security analysis, continuous monitoring, and penetration testing, blacklens.io identifies and addresses vulnerabilities early. Features such as **Darknet Monitoring**, **Vulnerability Scanning**, and **XDR Response** enable a proactive defense strategy and provide a clear, continuous view of an organization’s external security posture.

This integration enables security teams to **centralize blacklens.io alerts in Microsoft Sentinel**, correlate them with other security data sources, and automatically create incidents for investigation and response.

---

## What does this solution deploy?

When you install this solution, the following resources are deployed:

- A **custom Log Analytics table**: `blacklens_CL`
- A **Data Collection Endpoint (DCE)** and **Data Collection Rule (DCR)** for secure log ingestion
- A **Logic App (webhook-based)** to receive alerts from blacklens.io
- A **Microsoft Sentinel Analytics Rule** to generate incidents from ingested alerts

---

## Prerequisites

Before installing this solution, ensure that:

- Microsoft Sentinel is enabled on the target Log Analytics workspace
- You have **Contributor** or **Owner** permissions on the workspace and resource group

---

## Installation

1. Open **Microsoft Sentinel** in the Azure Portal.
2. Navigate to **Content hub**.
3. Search for **blacklens.io**.
4. Select the solution and click **Install**.
5. Choose the subscription, resource group, where you want to place the resources (probably the same resource group, where Sentinel's Log Analytics workspace is located) and the target Log Analytics workspace Resource ID.
6. Complete the installation.

After the installation finishes, continue with the post-deployment configuration steps below.

---

## Post-deployment configuration (Guided steps)

After deployment, a webhook endpoint is created that must be configured in blacklens.io.

### Step 1: Copy the webhook URL

1. Open the **deployment details** of the installed solution.
2. Navigate to the **Outputs** tab.
3. Copy the webhook
4. Integrate it into blacklens.io
5. After some minutes a informational test incident should appear in the Microsoft Sentinel

