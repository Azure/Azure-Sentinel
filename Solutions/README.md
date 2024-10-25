# Guide to building Microsoft Sentinel solutions

This guide provides an overview of Microsoft Sentinel solutions, and how to build and publish a solution for Microsoft Sentinel.

Microsoft Sentinel solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product, domain, and/or vertical scenarios in Microsoft Sentinel. This experience is powered by:

- [Azure Marketplace](https://azuremarketplace.microsoft.com/marketplace/) for solution discoverability, deployment, and enablement
- The [Microsoft Partner Center](https://docs.microsoft.com/partner-center/overview) for solution authoring and publishing

Providers and partners can deliver combined product, domain, or vertical value via solutions in Microsoft Sentinel in order to productize investments. More details are covered in the [Microsoft Sentinel documentation](https://aka.ms/azuresentinelsolutionsdoc). Review the [catalog](https://aka.ms/sentinelsolutionscatalog) for complete list of out-of-the-box Microsoft Sentinel solutions. 

Microsoft Sentinel solutions include packaged content, integrations, or service offerings for Microsoft Sentinel. This guide focuses on how to build packaged content into solutions, including combinations of data connectors, workbooks, analytic rules, playbooks, hunting queries, parsers, watchlists, and more for Microsoft Sentinel. Reach out to the [Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) if you are planning or building another type of integration or service offering, or want to include other types of content in your solution that isn't listed here.

The following image shows the steps in the solution building process, including content creation, packaging, and publishing:

![Microsoft Sentinel solutions build process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/solutions_steps.png)

## Step 1 – Create your content

Start with the [Get started documentation](https://github.com/Azure/Azure-Sentinel/wiki#get-started) on the Microsoft Sentinel GitHub Wiki to identify the content types you plan to include in your solution package. For example, supported content types include data connectors, workbooks, analytic rules, playbooks, hunting queries, and more. Each content type has its own contribution guidance for development and validation.

The guidance for each content type in the Wiki describes how to contribute individual pieces of content. However, you want to contribute your content in a packaged solution. Therefore, **hold off** on submitting your content to the relevant folders as described in the Wiki guidance, and instead place your content in the [Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) folder of the Microsoft Sentinel GitHub repo.

Use the following steps to create your content structure:

1. In the Microsoft Sentinel [Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) folder, create a new folder with your solution name. 

2. In your solution folder, create a blank folder structure as follows to store the content you've developed:
  * Data Connectors – the data connector json files or Azure Functions, etc. goes in this folder.
  * Workbooks – workbook json files and black and white preview images of the workbook goes here.
  * Analytic Rules – yaml file templates of analytic rules goes in this folder.
  * Hunting queries – yaml file templates of hunting queries goes in this folder.
  * Playbooks – json playbook and Azure Logic Apps custom connectors can go in this folder. 
  * Parser – yaml file for Kusto Functions or Parsers can go in this folder. Use [this](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeReplicatorV2.yaml) as reference.
  
  For example, see the folder structure for our [Cisco ISE solution](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Cisco%20ISE).

3. Store your logo, in SVG format, in the central [Logos](https://github.com/Azure/Azure-Sentinel/tree/master/Logos) folder.

4. Store sample data in the [sample data folder](https://github.com/Azure/Azure-Sentinel/tree/master/Sample%20Data), within the relevant content type folder, depending on your data connector type.

5. Submit a PR with all of your solution content. The PR will go through automated GitHub validation. [Address potential errors](https://github.com/Azure/Azure-Sentinel/wiki#test-your-contribution) as needed. 

After your content has been succesfully validated, the Microsoft Sentinel team will review your PR and reply with any feedback as needed. You can expect an initial response within five business days.

The PR will be approved and merged after any feedback has been incorportated and the full review is successful.

## Step 2 – Package your content

The solution content package is called a *solution template*, and has the following files:

* **mainTemplate.json**: The Azure Resource Manager (ARM) template that includes the resources offered by the solution. Each piece of content that you want to package in your solution must first be converted to ARM format. The `mainTemplate` file is the overall ARM template file that combines each invididual ARM content file. 

* **createUIDefinition.json**: The deployment experience definition provided to customers installing your solution. This is a step-by-step wizard experience.

For more information, see the [solution template documentation](https://docs.microsoft.com/azure/marketplace/plan-azure-app-solution-template) (deployment package).

After creating both the `mainTemplate.json` and the `createUIDefinition.json` files, validate them, and package them into a .zip file that you can upload as part of the publishing process (Step 3).

Use the [package creation tool](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Create-Azure-Sentinel-Solution/V3) to help you create and validate the package, following the [solutions packaging tool guidance](https://github.com/Azure/Azure-Sentinel/blob/master/Tools/Create-Azure-Sentinel-Solution/V3/README.md) to use the tool and package your content.

### Updating your solution

If you already have an Microsoft Sentinel solution and want to update your package, use the package creation tool with updated content to create a new version of the package.

For your solution's versioning format, always use `{Major}.{Minor}.{Revision}` syntax, such as `3.0.1`, to align with the Azure Marketplace recommendation and versioning support.  

When updating your package, make sure to raise the version value, regardless of how small or trivial the change is, including typo fixes in a content or solution definition file.

For example, if your original package version is `3.0.1`, you might update your versions as follows:

* **Major updates** have a new version of 3.0.0 - this is usually reserved for major tooling or package level changes
* **Minor updates**, for changes in content of the package, might have a new version of `3.1.0`
* **Revisions**, such as those scoped to a single piece of content or just metadata or text updates, might have a new version of `3.0.2`

Since solutions use ARM templates, you can customize the solution text as well as tabs as needed to cater to specific scenarios.

## Step 3 – Publish your solution

For a detailed walkthrough of how to publish your solutions, please refer to the following links - 

1. Publish solutions to Microsoft Sentinel - https://learn.microsoft.com/en-us/azure/sentinel/publish-sentinel-solutions
2. Solution tracking after publishing in the Microsoft Partner center - https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions-post-publish-tracking

## Feedback

[Email Azure Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with any feedback on this process, for new scenarios not covered in this guide, or with any constraints you may encounter. 

## FAQs

### CSP (Cloud Solution Provider)

#### What is CSP?
Microsoft Azure Customers may purchase their Azure Subscriptions either directly from Microsoft, or via an Azure Reseller who is part of the Microsoft Cloud Solution Provider (CSP) program.  Microsoft Sentinel Solutions are valid for both subscription purchase paths.   

#### Why is there a “CSP Opt-in” option on Microsoft Sentinel solution offers?
“CSP Opt-in” is a general feature of the Azure Marketplace and applies to multiple offer types, including the Azure App offer type used by Microsoft Sentinel solutions.  For some publishers, there is occasionally a desire to restrict individual offers to only be deployable in subscriptions that were purchased directly through Microsoft.   This is controllable via the “CSP opt-in” flag for each individual offer.  

#### Is Microsoft Sentinel available to customers who purchased their Azure subscription from a CSP Reseller partner?
Yes.  There are many customers purchasing directly from Microsoft, via a CSP Reseller and even some who purchase Azure via both programs.

#### What happens when you enable “CSP opt-in” for your Microsoft Sentinel Solution offer?
Quite simply, it permits your Microsoft Sentinel solution to be deployed into Microsoft Sentinel Workspaces regardless of how the customer acquired it. It is more of a pro-active stance to eliminate an message for your customers who are trying to deploy your Microsoft Sentinel Solution into a CSP purchase subscription.

#### What does **not** happen when you enable “CSP opt-in” for your Microsoft Sentinel solution offer?
You are **not** joining the CSP program.  Each offer is individually enabled or disabled for deployability in CSP sourced subscriptions, and setting this flag for your Microsoft Sentinel solution does not affect any other offer in your Marketplace publishing account.

#### What will happen if you do not enable “CSP opt-in” for your Microsoft Sentinel solution offer?
If the customer who wants to deploy your solution offer, purchased their subscription from a CSP Reseller partner, the solution will not deploy and the customer will get an error message about why. 


