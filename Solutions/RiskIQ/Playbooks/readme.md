# RiskIQ Playbook Guide

![RiskIQ](./riskiq.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Authentication](#authentication)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)

<a name="overview">

# Overview
RiskIQ's security SaaS platform taps into our global Internet Intelligence graph, which has mapped the billions of relationships between the internet components belonging to every organization, business, and threat actor on Earth. Our people and systems continuously update our unmatched data sets and our customers' unique Intelligence Graphs with both a current and historical view of their attack surface.

# RiskIQ Playbook Documentation

<a name="authentication">

## Authentication
You need a valid community or enterprise in order to use the connector and playbook. To learn more about the service and request a trial key, [register for free](https://community.riskiq.com/) or see the [API documentation](https://api.passivetotal.org/index.html). Credentials can be found on your [account settings](https://community.riskiq.com/settings) page. For enterprise customers, it's preferred to use the "organization" credential pair, not the user. If you have trouble accessing your account or your credentials contact your account representative (support[@]riskiq.com).

<a name="deployment">

### Deployment Instructions
RiskIQ Playbooks make use of a "base" playbook that will set a shared API connection. In order for all other playbooks to function properly, the "[RiskIQ-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/RiskIQ/Playbooks/RiskIQ-Base/azuredeploy.json)" playbook must be deployed first. Alternatively, you can deploy the solution which will handle deploying all playbooks at once.

1. Deploy the playbooks by clicking on "Deploy to Azure" button within each sub-folder. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying the playbooks.

<a name="postdeployment">

### Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

**Note: If you've deployed the [RiskIQ-Base](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/RiskIQ/Playbooks/RiskIQ-Base/azuredeploy.json) playbook, you will only need to authorize the Microsoft Sentinel connection.**