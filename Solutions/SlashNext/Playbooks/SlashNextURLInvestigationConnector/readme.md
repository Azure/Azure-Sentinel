# SlashNext URL Investigation Connector

<img src="../logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Overview

**SlashNext Connector** is based upon its Real-time Phishing Defense(RPD) APIs which are connected to SlashNext real-time threat intelligence database, continuously updated with the latest phishing threats. SlashNext RPD APIs are designed to be very fast and give accurate binary verdict on each enrichment request to ease its integration in any phishing Incident Response(IR) or SOAR environment.

## SlashNext URL Investigation Connector

### Prerequisites

**SlashNext Logic Apps Connector** supports **Basic** authentication, while creating connection you will be asked to provide API key. 
To acquire SlashNext API key, please contact us at [support@slashnext.com](mailto:support@slashnext.com) or visit [SlashNext.com](www.slashnext.com)

### Supported Actions

Get binary verdict of URLs

### Deployment Instructions

Deploy the Logic Apps Connector by clicking on **Deploy to Azure** button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextURLInvestigationConnector%2Fdeploy.json) 
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextURLInvestigationConnector%2Fdeploy.json)