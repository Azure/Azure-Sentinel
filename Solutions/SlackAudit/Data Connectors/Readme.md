# Integrating SlackAudit into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#step2)
- [Steps to get the Access Token from the Slack](#token)
- [Action Name limit for Sentinel Integration](#action)

## Introduction

The Slack Codeless Connector for Microsoft Sentinel enables seamless integration of Slack Audit logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Connector Framework(CCF), this connector simplifies the process of collecting and ingesting audit logs from Slack into Sentinel.

<a name="step2">

## Prerequisites
The below mentioned resources are required to connect SlackAudit with Sentinel.
- UserName
- API Key
- Actions

<a name="UserName">

## UserName

- While connecting to sentinel, In the UserName field, you can enter the name of the user who created the Slack app.

<a name="token">

## Steps to get the Access token from the Slack
- Create an App from scratch.
- In your App's settings, navigate to **OAuth & Permissions**, add the necessary OAuth scopes(auditlogs:read) and add a Redirect URL (this is where Slack will send the authorization code).
- In the left menu, click on Manage Distribution, under **Share Your App with Other Workspaces**, ensure all four checklist items have green checkmarks.
- Under **Share Your App with Your Workspace**, copy the **Sharable URL**, paste it into a browser while logged in as the owner of your Slack Enterprise Grid.
- Slack will redirect you to your specified redirect_uri and append a verification code to the URL.
- **Exchange Code for Access Token** : Open the Insomnia app (or use Curl in your terminal), and use the following Curl command to exchange the code for an access token

  curl -F code=YOUR_CODE \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     https://slack.com/api/oauth.v2.access

- Go to your app's **Basic Information** section to find the Client ID and Client Secret.

- After sending the request, you'll receive a response containing your access token.

- While connecting to sentinel, In the API Key field, enter the access token.

<a name="action">

## Action Name Limit for Sentinel Integration
- While connecting to sentinel, In the Action Type field, you can enter up to 30 action names at once separated by commas.
