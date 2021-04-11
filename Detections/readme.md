# About

This folder contains Detections based on different types of data sources that you can leverage in order to create alerts and respond to threats in your environment.

For general information please start with the [Wiki](https://github.com/Azure/Azure-Sentinel/wiki) pages.

More Specific to Detections:
* [Contribute](https://github.com/Azure/Azure-Sentinel/wiki/Contribute-to-Sentinel-GitHub-Community-of-Queries) to Analytic Templates (Detections) and Hunting queries
* Specifics on what is required for Detections and Hunting queries is in the [Query Style Guide](https://github.com/Azure/Azure-Sentinel/wiki/Query-Style-Guide)
* These detections are written using [KQL query langauge](https://docs.microsoft.com/azure/kusto/query/index) and will provide you a starting point to protect your environment and get familiar with the different data tables.
* To enable these detections in your environment follow the [out of the box guidance](https://docs.microsoft.com/azure/sentinel/tutorial-detect-threats-built-in) (Notice that after a detection is available in this GitHub, it might take up to a week before it is available in Azure Sentinel portal).
* The rule created will run the query on the scheduled time that was defined, and trigger an alert that will be seen both in the **SecurityAlert** table and in a case in the **Incidents** tab

# Feedback
For questions or feedback, please contact AzureSentinel@microsoft.com
