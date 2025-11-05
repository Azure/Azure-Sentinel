# Phosphorus Solution for Azure Sentinel
This repository contains all resources for the Phosphorus Azure Sentinel Solution.
The Phosphorus Solution is built in order to easily integrate Phosphorus with Azure Sentinel.

By deploying this solution, you'll be able to ingest device data from Phosphorus into Microsoft Sentinel

The solution consists out of the following resources:
- A codeless API connector to ingest data into Sentinel.

## Data Connector Deployment
The data connector will retrieve the Phosphorus device data through the Phosphorus REST API.

This is a codeless API connector. After the deployment of the ARM template, the connector will be available in the Data Connectors list to connect.

Input the Phosphorus Instance Domain name, Integration Name, API key , click Connect button and Microsoft Sentinel will start to pull in device data.
