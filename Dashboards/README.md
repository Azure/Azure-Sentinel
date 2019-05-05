
# About

* This folder contains the Azure Sentinel dashboard gallery.

* This page describe how to add new dashboard to the public Azure Sentinel dashboards gallery.

# Step 1 - Create Azure dashboard:

[Follow these instructions to create a new dashboard using Log Analytics query]([https://docs.microsoft.com/azure/azure-monitor/learn/tutorial-app-dashboards#add-analytics-query](https://docs.microsoft.com/azure/azure-monitor/learn/tutorial-app-dashboards#add-analytics-query))

[Azure Log Analytics Query Language Reference]([https://docs-analytics-eus.azurewebsites.net/index.html](https://docs-analytics-eus.azurewebsites.net/index.html))

* Make sure that you save a 1x1 square for the Azure Sentinel button in the top left corner (this button navigate back to Azure Sentinel dashboard gallery).

* Use the Markdown tile for the dashboard standalone titles and the logos.

* Do not define any time filters on your charts.

![Azure Sentinel part](https://ibb.co/47dhVYG)


# Step 2 - Export the dashboard into a JSON file:

* On the dashboard view click "Download" - this action will download a JSON file to your computer.

* Edit the JSON file to hide your personal details:

* Replace the following fields:

Subscription id to "{Subscription_Id}"

Resource Group to "{Resource_Group}"

Name (your workspace id) to "{Workspace_Name}"

# Step 3 - Share the Dashboard JSON with Azure Sentinel community

In this step you will upload the dashboard JSON, logo, screenshots and desctiption.

To do this create a **single** pull request containing the following:

1. Upload the dashboard JSON file to [Azure-Sentinel/Dashboards/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards](https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards)) repo (make sure the file name will be in the following format: Text_Text.json)

2. Upload the logo to [Azure-Sentinel/Dashboards/Images/Logos/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Logos](https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Logos)) repo, the logo has to be in SVG format (make sure the file name will be in the following format: text_text.svg)

3. (optional) capture two or more screenshots of the dashboard, where at least one is in white theme and another in the dark theme. Upload the screenshots to [Azure-Sentinel/Dashboards/Images/Preview/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Preview](https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Preview)) repo (make sure the name of the files will be in the following format: text_text_white1.png, text_text_black1.png )

4. Add a short paragraph that describes your dashboard purpose to the pull request comment.
