# About

* This folder contains Detections based on different types of data sources that you can leverage in order to create alerts and respond to threats in your environment.
* These detections are written using [KQL query langauge](https://docs.microsoft.com/en-us/azure/kusto/query/index) and will provide you a starting point to protect your environment and get familiar with the different data tables.
* To create the detection in your environment - 
  - go to the 'Analytics' section
  - copy the required query
  - update the alert rule parameters according to the detection parameters - copy the name, the description, lookback time, threshold and severity.
  - the query will be simulated and you will be able to immediately see if a you have hits based on the detection.
  - create the alert rule
* The rule created will run the query on the scheduled time that was defined, and trigger an alert that will be seen both in the **SecurityAlert** table and in a case in the **Cases** page
 
 For questions or feedback, please contact AzureSentinel@microsoft.com
