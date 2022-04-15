# Threat Analysis & Response with MITRE ATT&CK Azure Function

This function app will download all the detection and hunting query yaml files from Microsoft Sentinel Github, parse it , convert it into structured tabular dataset and ingest as a customlog table named MITREATTACKMap_CL. For more details about the notebook, workflow, read the blog [Using Jupyter Notebook to analyze and visualize Azure Sentinel Analytics and Hunting Queries](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/using-jupyter-notebook-to-analyze-and-visualize-azure-sentinel/ba-p/1770400)

## How it works

The function will be deployed automatically once the solution is deployed. Once the function is deployed , plase set variables WorkspaceId and Workspacekey in the App Settings. For more information, check the docs [Configure App Settings](https://docs.microsoft.com/azure/azure-functions/functions-how-to-use-azure-function-app-settings)".



