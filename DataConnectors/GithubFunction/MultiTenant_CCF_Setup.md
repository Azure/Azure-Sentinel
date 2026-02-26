# Setting up Multiple GitHub Enterprise Cloud Organizations with Audit Log Connector (CCF)

This guide explains how to configure the GitHub Enterprise Audit Log connector to collect audit data from multiple GitHub Enterprise Cloud organizations into Microsoft Sentinel using the Codeless Connector Framework (CCF).

## Prerequisites

To integrate with GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview) make sure you have:

1. **Workspace**: Read and Write permissions are required
2. **GitHub API personal access token**: To enable polling for the Enterprise audit log, ensure the authenticated user is an Enterprise admin and has a GitHub personal access token (classic) with the `read:audit_log` scope
3. **GitHub Enterprise type**: This connector will only function with GitHub Enterprise Cloud; it will not support GitHub Enterprise Server

## Overview

Using the GitHub Enterprise Audit Log connector (CCF), you can:
- Collect audit logs from all organizations under your GitHub Enterprise Cloud account
- Monitor activity across all repositories within those organizations
- View all GitHub Enterprise audit events in a single Sentinel workspace
- Apply unified security policies across your entire Enterprise

## Setup Steps

### 1. Configure Sentinel Connector

1. In Microsoft Sentinel:
   - Go to Data Connectors
   - Search for "GitHub Enterprise Audit Log (CCF)"
   - Click "Open connector page"

### 2. Get GitHub Enterprise Details

For each GitHub Enterprise Cloud instance you want to monitor:

1. Get Enterprise Access Token:
   - Create a personal access token in your GitHub Enterprise Cloud account
   - Ensure you have Enterprise Admin permissions
   - Token must have `read:audit_log` scope

2. Note Required Information:
   - Enterprise name (from your Enterprise URL)
   - Personal access token with Enterprise admin permissions

### 3. Configure Connector

1. In the connector page:
   - Click "Add Enterprise"
   - Enter the Enterprise Name
     - Note: Your enterprise profile URL is https://github.com/enterprises/yourenterprisename
   - Enter the API Key (GitHub personal access token)
     - Note: For instructions on creating a personal access token, see [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)
   - Click "Add Enterprise" to save the configuration
   - Repeat these steps for your second GitHub Enterprise

## Validation

1. Check Data Collection:
   - Wait 5-10 minutes for initial data collection
   - Go to Logs in Sentinel
   - Run this query:
   ```kql
   GitHubEnterpriseAudit
   | where TimeGenerated > ago(1h)
   | summarize count() by Organization
   ```

## Troubleshooting

Common issues:

1. No Data Flowing:
   - Verify the Enterprise Name matches your GitHub Enterprise URL
   - Check if the API Key (personal access token) is valid and hasn't expired
   - Confirm the token has the required `read:audit_log` scope
   - Ensure the user is an Enterprise admin

2. Missing Events:
   - Verify Enterprise access permissions
   - Check network connectivity
   - Review GitHub API rate limits

## Security Best Practices

- Regularly rotate your GitHub personal access tokens
- Monitor audit log collection status
- Set up alerts for collection failures
- Review Enterprise access permissions periodically
