# About

This folder contains Detections based on different types of data sources that you can leverage in order to create alerts and respond to threats in your environment. These detections are termed as Analytics Rule templates in Microsoft Sentinel.

**Note**: Many of these analytic rule templates are being delivered in Solutions for Microsoft Sentinel. You can discover and deploy those in [Microsoft Sentinel Content Hub](https://docs.microsoft.com/azure/sentinel/sentinel-solutions-deploy). These are available in this repository under [Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) folder. For example, Analytic rules for the McAfee ePolicy Orchestrator solution are found [here](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules).

For general information please start with the [Wiki](https://github.com/Azure/Azure-Sentinel/wiki) pages.

More Specific to Detections:
* [Contribute](https://github.com/Azure/Azure-Sentinel/wiki/Contribute-to-Sentinel-GitHub-Community-of-Queries) to Analytic Templates (Detections) and Hunting queries
* Specifics on what is required for Detections and Hunting queries is in the [Query Style Guide](https://github.com/Azure/Azure-Sentinel/wiki/Query-Style-Guide)
* These detections are written using [KQL query langauge](https://docs.microsoft.com/azure/kusto/query/index) and will provide you a starting point to protect your environment and get familiar with the different data tables.
* To enable these detections in your environment follow the [out of the box guidance](https://docs.microsoft.com/azure/sentinel/tutorial-detect-threats-built-in) (Notice that after a detection is available in this GitHub, it might take up to 2 weeks before it is available in Microsoft Sentinel portal).
* The rule created will run the query on the scheduled time that was defined, and trigger an alert that will be seen both in the **SecurityAlert** table and in a case in the **Incidents** tab
* If you are contributing analytic rule templates as part of a solution, follow [guidance for solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#step-1--create-your-content) to include those in the right folder paths. Do NOT include content to be packaged in solutions under the Detections folder. 

# Feedback
For questions or feedback, please contact AzureSentinel@microsoft.com
