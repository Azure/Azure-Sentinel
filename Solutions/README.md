# Guide to Building Microsoft Sentinel Solutions

This guide provides an overview of Microsoft Sentinel Solutions and how one can build and publish a solution for Microsoft Sentinel. 

Microsoft Sentinel Solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Microsoft Sentinel. This experience is powered by [Azure Marketplace](https://azuremarketplace.microsoft.com/marketplace/) for Solutions’ discoverability, deployment and enablement and [Microsoft Partner Center](https://docs.microsoft.com/partner-center/overview) for Solutions’ authoring and publishing. Providers or partners can deliver combined product or domain or vertical value via solutions in Microsoft Sentinel and be able to productize investments. More details are covered in [Azure Sentinel documentation](https://aka.ms/azuresentinelsolutionsdoc) and review the [catalog](https://aka.ms/sentinelsolutionscatalog) for complete list of Microsoft Sentinel solutions. 

Microsoft Sentinel Solutions include packaged content or integrations or service offerings for Microsoft Sentinel. This guide focuses on building packages content type solutions that includes combination of one or many data connectors, workbooks, analytic rules, playbooks, hunting queries, parsers, watchlists, and more for Microsoft Sentinel. Reach out to [Azure Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) if you plan to build an integration type or service offering type or want to build any other type of Solution not covered above.

![Microsoft Sentinel solutions build process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/solutions_steps.png)

## Step 1 – Create Content for Microsoft Sentinel
Start with the [Get started documentation](https://github.com/Azure/Azure-Sentinel/wiki#get-started) on the Microsoft Sentinel GitHub Wiki to identify the content types you plan to include in your Solution package. This includes data connectors, workbooks, analytic rules, playbooks, hunting queries, and more. Each of the content type has its own contribution guidance which you can follow to develop and validate the content. 

**Hold off** on submitting the content to the respective folders as pointed to in the contribution guidance for each contribution. Instead, have your content in the [Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) folder of the GitHub repo.
* Create a folder with your Solution name under [Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) folder.
* Within that create a folder structure within your Solutions folder as follows to submit your content developed above. See [example](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Cisco%20ISE). 
   * Data Connectors – the data connector json files or Azure Functions, etc. goes in this folder.
  * Workbooks – workbook json files and black and white preview images of the workbook goes here.
  * Analytic Rules – yaml file templates of analytic rules goes in this folder.
  * Hunting queries – yaml file templates of hunting queries goes in this folder.
  * Playbooks – json playbook and Azure Logic Apps custom connectors can go in this folder. 
  * Parser – txt file for Kusto Functions or Parsers can go in this folder.
* Logo – SVG format logo can go to the central [Logos](https://github.com/Azure/Azure-Sentinel/tree/master/Logos) folder.
* Sample data – Check this into the [sample data folder](https://github.com/Azure/Azure-Sentinel/tree/master/Sample%20Data) within the respective folder depending on data connector type. 	
* Submit a PR with all of your Solution content.
* The PR will go through automated GitHub validation and [address potential errors](https://github.com/Azure/Azure-Sentinel/wiki#test-your-contribution) as needed. 
* Upon successful content validation, the Microsoft Sentinel team will review your PR and get back with feedback (as needed). Expect an initial response within 5 business days. 
* The PR gets approved and merged upon successful review/feedback incorporation process. 

## Step 2 – Package Content
The Solutions content package is called a Solution template and has two files listed as follows. Refer to the [Solution template documentation](https://docs.microsoft.com/azure/marketplace/plan-azure-app-solution-template) (deployment package) for details on these ARM (Azure Resource Manager) files. 
1.	mainTemplate.json - ARM template of the resources the Solution offer includes.
2.	createUIDefinition.json – Deployment experience definition that the customer installing a Solution goes through - this is a step-by-step wizard experience. 
All the content you plan to package needs to be converted to ARM format and the mainTemplate file is the overall ARM template file combining these individual ARM content files. After you create the two json files for your Solution, validate these. Finally, package these two json files in a .zip file that you can upload as part of the publish process (Step 3).

Use the [package creation tool](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Create-Azure-Sentinel-Solution) to help you create and validate the package - follow the [solutions packaging tool guidance](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Create-Azure-Sentinel-Solution#azure-sentinel-solutions-packaging-tool-guidance) to use the tool and package your content. 
* If you already have an Microsoft Sentinel solution and want to update the package, use the tool with updated content to create a new version of the package using the tool. 
* Versioning format of package - Always use {Major}.{Minor}.{Revision} schematic versioning format (for e.g. 1.0.1) for solutions that aligns with Azure Marketplace recommendation and versioning support.  
* Version for updates - If you update you package, please always remmeber to increment the version value, irrespective of how trivial the change is (could be just fixing a typo in a content or solution definition file). 
For e.g. If original package version is 1.0.1 and you make a:
    * Major update, new version can be 2.0.0
    * Minor update like changes applying to a few content in the package, new version can be 1.1.0
    * Very minor revisions scoped to one content, new version can be 1.0.2
* Since solutions use ARM template, you can customize the solution text as well as tabs if needed for catering to specific scenarios.  

## Step 3 – Publish Solution
Microsoft Sentinel Solutions publish experience is powered by [Microsoft Partner Center](https://docs.microsoft.com/partner-center/overview). 
### Registration (one-time)
If you/your company are a first-time app publisher on Azure Marketplace, [follow the steps](https://docs.microsoft.com/azure/marketplace/partner-center-portal/create-account) to register and create a [Commercial Marketplace](https://docs.microsoft.com/azure/marketplace/overview) account in Partner Center. This process will give you a unique Publisher ID and access to the Commercial Marketplace authoring and publishing experience on Partner Center to create, certify and publish a Solution offer. 
### Author and Publish Solutions Offer
For the following steps we’ll rely on Partner Center’s detailed documentation. 
1.	[Create an Azure application type offer](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer) and configure the offer setup details per guidance. 
2.	[Configure](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-properties) the Offer properties.
3.	Configure the [Offer listing details](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-listing) – this includes the title, description, pictures, videos, support information, etc. aspects. Enter one of the search keywords value as f1de974b-f438-4719-b423-8bf704ba2aef – to display your Solution in the Microsoft Sentinel Solutions gallery. 
4.	[Create a plan](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-plans) and select plan type as Solution Template.
5.	[Configure](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-solution) the Solutions template plan. This is where you’ll upload the Solutions zip created in Step 2 and set a version for the package. Follow versioning guidance mentioned in Step 2.
6.	[Validate and Test](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-test-publish) the offer once done.  
7.	Once you’ve validated the offer, [publish the offer live](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-test-publish#publish-your-offer-live). This will trigger the certification process (can take up to 3 business days). 

**Note:** The Microsoft Sentinel team will need to make a change so that your Solution shows up in the Microsoft Sentinel Solutions gallery, hence before going live, email [Azure Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with your Solutions offer ID and Publisher ID so that we can make the necessary changes.

**Note:** Making the offer public is very important for it to show up in the Microsoft Sentinel Solutions gallery.
 

## Feedback
[Email Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with any feedback on this process or for new scenarios not covered in this guide or with any constraints you may encounter. 


