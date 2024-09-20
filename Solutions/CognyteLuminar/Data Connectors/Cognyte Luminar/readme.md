# Luminar Threat Intelligence Connector - Azure Sentinel


## Table of Contents

1. [Overview](#overview)
2. [Luminar API Account](#prerequisites)
3. [Register an Azure AD App for TI Indicators Graph API Write Access](#graphapiaccess)
4. [Deployment](#deployment)
5. [Detection & Investigation](#investigation)

<a name="overview">

## Overview
Cognyte is a global leader in security analytics software that empowers governments and enterprises with Actionable Intelligence for a safer world. Our open software fuses, analyzes and visualizes disparate data sets at scale to help security organizations find the needles in the haystacks. Over 1,000 government and enterprise customers in more than 100 countries rely on Cognyte’s solutions to accelerate security investigations and connect the dots to successfully identify, neutralize, and prevent threats to national security, business continuity and cyber security.

Luminar is an asset-based cybersecurity intelligence platform that empowers enterprise organizations to build and maintain a proactive threat intelligence operation that enables to anticipate and mitigate cyber threats, reduce risk and enhance security resilience. Luminar enables security teams to define a customized, dynamic monitoring plan to uncover malicious activity in its earliest stages on all layers of the Web.

**Luminar IOCs and Leaked Credentials** connector allows integration of intelligence-based IOC data and customer-related leaked records identified by Luminar.


<a name="prerequisites">

## Luminar API Account
To utilize Luminar Threat Intelligence, you'll want to have Luminar Credentials.
- Luminar API Account ID
- Luminar API Client ID  
- Luminar API Client Secret
For registration and more details please contact luminar@cognyte.com


<a name="graphapiaccess>

## Register an Azure AD App for TI Indicators Graph API Write Access
This connector requires some basic information to allow you to connect to Luminar Threat Intelligence and send it threat indicators in microsoft sentinel. The three pieces of information you need are:
- Application (client) ID
- Directory (tenant) ID
- Client Secret

To obtain the above values please follow the below

- Go to Azure Active Directory / App Registrations
- Create +New Registration
- Give it a name. Click Register
- Click API Permissions Blade
- Click Add a Permission
- Click Microsoft Graph
- Click Application Permissions
- Check permissions for ThreatIndicators (ThreatIndicators.ReadWrite.OwnedBy). Click Add permissions
- Click grant admin consent for domain.com
- Click Certificates and Secrets
- Click New Client Secret
- Enter a description, select never. Click Add
- **IMPORTANT**. Click copy next to the new secret and paste it somewhere temporarily. You cannot come back to get the secret once you leave the blade
- Copy the client ID from the application properties and paste it somewhere as you will need it to be added to the Playbooks
- Also copy the tenant ID from the AAD directory properties blade

for more information please refer https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-tip

<a name="deployment">

## Deployment
- Go to Microsoft Sentinel
- Go to Content Hub
- Search for Luminar, Click on Install.
- Please follow the onscreen deployment screen and provide the required values.

<a name="investigation">

## Detection & Investigation
Now that we have Luminar Threat Intelligence data, you can use out of the box TI analytics rules for you hunting and investigation (or) write custom analytical rules.

A sample Azure Sentinel Analytics rule to identify a match in Azure AD SigninLogs from any malicious IP address from luminar threat intelligence

```
let ipIndicators =

ThreatIntelligenceIndicator

| where NetworkIP != ""

| project IPAddress = NetworkIP;

ipIndicators

| join (SigninLogs) on IPAddress

```

What this query is doing is creating a temporary table (“ipIndicators”) that is composed of just the IPv4 addresses from the ThreatIntelligenceIndicator table. This is then joined to the SigninLogs table using IPAddress as they key for the join (e.g. where the field values match in both tables).

 
Happy hunting!