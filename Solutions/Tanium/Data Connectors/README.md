# Tanium Data Connector for Microsoft Sentinel

<img src="../images/Tanium.svg" alt="Tanium" width="20%"/><br>

## Overview

The Tanium Data Connector deploys the required resources to your Azure instance to enable sending data from Tanium to Sentinel via Logs Ingestion Workspaces. For more information see [Tanium Data Connector](https://help.tanium.com/bundle/ConnectAzureSentinel/page/Integrations/MSFT/ConnectAzureSentinel/Get_to_know_our_Content.htm#_Tanium_Data_Connector)

## Setup Data Flow

Once you have deployed the Data Connector you'll be provided with the configuration values needed for your connections in Tanium. You'll need to create connections using the Tanium Connect Module in your Tanium Server.

> [!IMPORTANT]  
> Once of the values that will be displayed after you deploy the connector will be the App Registration secret. Be sure to capture this value before refreshing or navigating away from the page, as you will not be able to access this again since it's a sensitive/secret value.

Use the [JSON file found here](./connect-module-connections.json) along with the [instructions on the Tanium Help site](https://help.tanium.com/bundle/ConnectAzureSentinel/page/Integrations/MSFT/ConnectAzureSentinel/Create_Connections.htm) to setup the necessary connections.

## Help

Having issues? See our [Tanium Help documentation](https://help.tanium.com/bundle/ConnectAzureSentinel/page/Integrations/MSFT/ConnectAzureSentinel/Overview.htm) for common issues, questions and FAQs.
