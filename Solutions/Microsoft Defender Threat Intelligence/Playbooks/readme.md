# MDTI Playbook Guide

![Microsoft Defender Threat Intelligence](./MDTI.jpg)<br>

## Table of Contents

1. [Overview](#overview)
1. [Authentication](#authentication)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)

<a name="overview">

# Overview
Microsoft centralizes numerous data sets into a single platform, Microsoft Defender Threat Intelligence [(MDTI)](https://learn.microsoft.com/en-us/defender/threat-intelligence/what-is-microsoft-defender-threat-intelligence-defender-ti), making it easier for Microsoft’s community and customers to conduct infrastructure analysis. Microsoft’s primary focus is to provide as much data as possible about Internet infrastructure to support a variety of security use cases. If you have trouble accessing your account or your credentials contact your account representative or reach out to discussMDTI[@]microsoft.com

# MDTI Playbook Documentation

<a name="authentication">

## Authentication
Azure AD App Registration credentials(ClientId/ClientSecret/TenantId) with MDTI API Permissions are needed when configuring this playbook. Those can be found on your [Azure Client App](https://learn.microsoft.com/en-us/rest/api/azure/#register-your-client-application-with-azure-ad) page.

MDTI API documentation for more details, [MDTI API](https://learn.microsoft.com/en-us/graph/api/resources/security-threatintelligence-overview?view=graph-rest-beta&branch=pr-en-us-20472).

<a name="deployment">

### Deployment Instructions
MDTI Playbooks make use of a "base" playbook that will set a shared API connection. In order for all other playbooks to function properly, the [MDTI-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Microsoft%20Defender%20Threat%20Intelligence/Playbooks/MDTI-Base/azuredeploy.json) playbook must be deployed first. Alternatively, you can deploy the solution which will handle deploying all playbooks at once.

1. Deploy the playbooks by clicking on "Deploy to Azure" button within each sub-folder. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying the playbooks.

<a name="postdeployment">

### Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

**Note: If you've deployed the [MDTI-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Microsoft%20Defender%20Threat%20Intelligence/Playbooks/MDTI-Base/azuredeploy.json) playbook, you will only need to authorize the Microsoft Sentinel connection.**
