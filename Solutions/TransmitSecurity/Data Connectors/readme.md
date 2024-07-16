# Transmit Security Integration for Microsoft Sentinel

## Introduction

This folder contains the Azure function time trigger code for the Transmit Security-Microsoft Sentinel connector. The connector will run periodically and ingest the Transmit Security data into the Microsoft Sentinel logs custom table `TransmitSecurityAdminActivity_CL` and `TransmitSecurityUserActivity_CL`.

## Folders

1. **TransmitSecurity/** - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. **TransmitSecurityConnector/** - This contains the Azure function source code along with sample data.

## Installing for Users

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in the Data connectors section of Sentinel.

1. Go to **Microsoft Sentinel** -> **Data Connectors**.
2. Click on the **Transmit Security connector**; the connector page will open.
3. Click on the blue **Deploy to Azure** button.

This will lead to a custom deployment page where, after entering accurate credentials and other information, the resources will be created.

The connector should start ingesting the data into the logs in the next 10-15 minutes.

## Installing for Testing

1. Log in to the Azure portal using the URL - [https://aka.ms/sentineldataconnectorvalidateurl](https://aka.ms/sentineldataconnectorvalidateurl).
2. Go to **Microsoft Sentinel** -> **Data Connectors**.
3. Click the **import** button at the top and select the JSON file `TransmitSecurity_API_FunctionApp.JSON` downloaded on your local machine from GitHub.
4. This will load the connector page; the rest of the process will be the same as the **Installing for Users** guideline above.

## Monitoring the Function

Each invocation and its logs of the function can be seen in the Function App service of Azure, available in the Azure Portal outside Microsoft Sentinel.

1. Go to **Function App** and click on the function you have deployed, identified with the given name at the deployment stage.
2. Go to **Functions** -> **Transmit Security Connector** -> **Monitor**.
3. By clicking on the invocation time, you can see all the logs for that run.

**Note:** For more detailed logs, you can check Application Insights of the given function. You can search the logs by operation ID in the Transaction search section.