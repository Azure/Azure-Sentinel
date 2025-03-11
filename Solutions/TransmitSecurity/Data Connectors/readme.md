# Transmit Security Integration for Microsoft Sentinel

## Introduction

This folder contains the Azure Function Time Trigger code for the Transmit Security-Microsoft Sentinel connector. The connector will run periodically and ingest Transmit Security data into the Microsoft Sentinel logs custom table `TransmitSecurityActivity_CL`.

## Folders

1. **TransmitSecurity/** - Contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. **TransmitSecurityConnector/** - Contains the Azure Function source code along with sample data.

## Installing for Users

After the solution is published, you can find the connector in the connector gallery of Microsoft Sentinel among other connectors in the Data Connectors section.

1. Go to **Microsoft Sentinel** -> **Data Connectors**.
2. Click on the **Transmit Security connector**; the connector page will open.
3. Click on the blue **Deploy to Azure** button.

This will lead to a custom deployment page where, after entering accurate credentials and other information, the resources will be created.

The connector should start ingesting data into the logs within the next 10-15 minutes.

## Installing for Testing

1. Log in to the Azure portal using the URL - [https://aka.ms/sentineldataconnectorvalidateurl](https://aka.ms/sentineldataconnectorvalidateurl).
2. Go to **Microsoft Sentinel** -> **Data Connectors**.
3. Click the **Import** button at the top and select the JSON file `TransmitSecurity_API_FunctionApp.JSON` downloaded on your local machine from GitHub.
4. This will load the connector page; the rest of the process will be the same as the **Installing for Users** guideline above.

## Monitoring the Function

Each invocation and its logs of the function can be seen in the Function App service of Azure, available in the Azure Portal outside Microsoft Sentinel.

1. Go to **Function App** and click on the function you have deployed, identified by the name given at the deployment stage.
2. Go to **Functions** -> **TransmitSecurityConnector** -> **Monitor**.
3. By clicking on the invocation time, you can see all the logs for that run.

**Note:** For more detailed logs, check Application Insights of the function. You can search the logs by operation ID in the Transaction search section.
