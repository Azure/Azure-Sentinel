# About

* This repo contains the Azure Sentinel dashboard gallery.

* This page describe how to add a new dashboard to the public Azure Sentinel dashboards gallery.

# Step 1 - Create Azure Sentinel dashboard:

[Follow these instructions to create a new dashboard using a Log Analytics query]([https://docs.microsoft.com/azure/azure-monitor/learn/tutorial-app-dashboards#add-analytics-query](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fazure%2Fazure-monitor%2Flearn%2Ftutorial-app-dashboards%23add-analytics-query&data=01%7C01%7CMor.Shabi%40microsoft.com%7C9b88386118784a0b388108d6d1dd07dc%7C72f988bf86f141af91ab2d7cd011db47%7C1&sdata=alDjGebhQLCFvN5bRRBdFESR68gXBNvPNjVAbzki%2B7Q%3D&reserved=0))

[Azure Log Analytics Query Language Reference]([https://docs-analytics-eus.azurewebsites.net/index.html](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs-analytics-eus.azurewebsites.net%2Findex.html&data=01%7C01%7CMor.Shabi%40microsoft.com%7C9b88386118784a0b388108d6d1dd07dc%7C72f988bf86f141af91ab2d7cd011db47%7C1&sdata=NNMmNdMpZM2JqdNJtSNxK%2B8%2FPM7QThpK3Ox%2Fn71AbpA%3D&reserved=0))

* Make sure that you save a 1x1 square for the Azure Sentinel button in the top left corner (this button navigates back to the Azure Sentinel dashboard gallery).

* Use the Markdown tile for the dashboard standalone titles and the logos.

* Do not define any time filters on your charts.

# Step 2 - Export the dashboard into a JSON file:

* From the dashboard view, click "Download" - this will download a JSON file to your computer.

* Edit the JSON file to hide your personal details:

* Replace the following fields:

>Change your subscription ID to "{Subscription_ID}"

>Change your resource group to "{Resource_Group}"

>Change your name (your workspace ID) to "{Workspace_Name}"

# Step 3 - Share the Dashboard JSON with the Azure Sentinel community

In this step you will upload the dashboard JSON, logo, screenshots, and description.

To do this create a **single** pull request containing the following:

1. Upload the dashboard JSON file to [Azure-Sentinel/Dashboards/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FDashboards&data=01%7C01%7CMor.Shabi%40microsoft.com%7C9b88386118784a0b388108d6d1dd07dc%7C72f988bf86f141af91ab2d7cd011db47%7C1&sdata=5tpVCCXcCg9RsQQWGpzbT0jAD90qAd9pPicVnTCtQAE%3D&reserved=0)) repo (make sure the file name is in the format: Text_Text.json).

2. Upload the logo to [Azure-Sentinel/Dashboards/Images/Logos/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Logos](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FDashboards%2FImages%2FLogos&data=01%7C01%7CMor.Shabi%40microsoft.com%7C9b88386118784a0b388108d6d1dd07dc%7C72f988bf86f141af91ab2d7cd011db47%7C1&sdata=9E0lJPZkcw3YqWz44Lh%2BiyuuATwrswZhGqv23LJzWAs%3D&reserved=0)) repo, the logo must be in SVG format (make sure the file name is in the format: text_text.svg).

3. (Optional) Capture two or more screenshots of the dashboard, where at least one is in the white theme and another in the dark theme. Upload the screenshots to [Azure-Sentinel/Dashboards/Images/Preview/]([https://github.com/Azure/Azure-Sentinel/tree/master/Dashboards/Images/Preview](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FDashboards%2FImages%2FPreview&data=01%7C01%7CMor.Shabi%40microsoft.com%7C9b88386118784a0b388108d6d1dd07dc%7C72f988bf86f141af91ab2d7cd011db47%7C1&sdata=nrnfuYqHWYG5mO7aQV1Bm3ZOapECYKfMK4Z4qUS%2FQL4%3D&reserved=0)) repo (make sure the name of the files is in the format: text_text_white1.png, text_text_black1.png )

4. Add a short paragraph that describes the purpose of your dashboard in the pull request comment.
