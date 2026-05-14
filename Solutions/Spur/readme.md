# Spur Context API Solution

## Table of Contents

1. [Overview](#overview)
2. [Enrichment](#enrichment)
3. [App Registration](#appregistration)
4. [Deployment Instructions](#deployorder)


<a name="overview">

## Overview
Spur Context API provides access to the highest-fidelity IP intelligence available on-demand, delivering the right IP enriched data in real-time to protect digital assets from the risk of obscured VPN, residential proxy, and bot automation traffic.

Spur Context API delivers:

- Broad Coverage: Tracks hundreds of millions of active anonymous IPs and more than 1,000 VPN and proxy services, updated in real-time.
- Depth of Data: Returns 20+ enrichment attributes per IP – covering geography, ASN, proxy/VPN attribution, device and connection type, and tunnel entry/exit context.
- Zero Latency Access: Provides immediate enrichment for millions of IPs, including ASN, geolocation, and non-anonymized addresses, with no delay to decisioning systems.
- Real-Time Data: Continuously refreshes to reflect the latest observed anonymization infrastructure and behavioral changes.
- Also available as part of the Spur IP Intelligence and Session Enrichment Platform, Context API offers options and add-ons to match access and query volume  requirements for the most complex security, threat hunting, and fraud use cases.

This solution contains the following:

- Two playbooks,
- One custom connector. 

<a name="enrichment"></a>
## Enrichment Usecase   

| Playbook | Description |
| --------- | -------------- |
| **Spur-IP-Enrichment-Incident-Trigger** | This playbook runs on an incident trigger, fetches all the IP address entities associated with the incident, and adds the context data back to incident comments for further Analysis. Optionally, the context data is also saved in the log Analytics cusom table. |
| **Spur-IP-Enrichment-Alert-Trigger** | This playbook runs on an alert trigger, fetches all the IP address entities associated with the incident, and adds the context data back to incident comments for further Analysis. Optionally, the context data is also saved in the log Analytics cusom table.|

Please refer to the documentation pages for each playbook for more information.


<a name="appregistration"></a>

## App Registration

Before deploying the solution, you need to create an App Registration in Azure:

1. **Create App Registration**
   - Search for "App registrations" in the search bar
   - Click on "App registrations" from the results
   - Click the "New registration" button

2. **Configure App Registration**
   - **Name**: Enter a name for your app (e.g., "Spur-Context-Connector")
   - **Supported account types**: Select "Accounts in this organizational directory only" (single tenant)
   - **Redirect URI (optional)**: Add if needed for your application
   - Click "Register"

3. **Copy Application Details**
   - After registration, note down:
     - **Application (client) ID** - displayed on the Overview page
     - **Directory (tenant) ID** - displayed on the Overview page

4. **Add Client Secret**
   - In the left menu, Under Manage click "Certificates & secrets"
   - Under the "Client secrets" section, click "New client secret"
   - **Description**: Enter a description (e.g., "Spur Connector Secret")
   - **Expires**: Select expiration period (e.g., 180 days, 365 days, or never)
   - Click "Add"

5. **Copy Client Secret**
   - The secret value will be displayed (copy it immediately - you won't be able to see it again)
   - Store it securely in your key vault or secret management system

**Important**: The client secret value is only shown once after creation. Make sure to copy and save it securely before leaving the page.


<a name="deployorder"></a>
## Deployment Instructions

Please follow the following order while installing the solution.

1. Spur Custom Connector
2. Spur Playbooks

