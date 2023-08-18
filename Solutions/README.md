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
  * Parser – yaml file for Kusto Functions Parsers can go in this folder. Use [this](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeReplicatorV2.yaml) as reference.
  
  For example, see the folder structure for our [Cisco ISE solution](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Cisco%20ISE).

3. Store your logo, in SVG format, in the central [Logos](https://github.com/Azure/Azure-Sentinel/tree/master/Logos) folder.

4. Store sample data in the [sample data folder](https://github.com/Azure/Azure-Sentinel/tree/master/Sample%20Data), within the relevant content type folder, depending on your data connector type.


## Step 2 - Prepare for packaging

Solution packages are now auto-created and will be available in the Master branch within the solution folder created in Step 1 after technical reviews are completed. Automated pipelines require certain inputs for creating a solution package in addition to the content created in Step 1. The following guidance will help preparing all requisites.

1. **Get your Publisher ID**.
Microsoft Sentinel solution publishing experience is powered by the [Microsoft Partner Center](https://docs.microsoft.com/partner-center/overview). If you or your company is a first-time app publisher on Azure Marketplace, [follow the steps](https://docs.microsoft.com/azure/marketplace/partner-center-portal/create-account) to register and create a [Commercial Marketplace](https://docs.microsoft.com/azure/marketplace/overview) account in Partner Center. This process provides you with a unique **Publisher ID** and access to the Commercial Marketplace authoring and publishing experience, where you'll create, certify, and publish your solution.

2. **Get your Offer ID**.
[Create an Azure application type offer](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer) and configure the offer setup details as per the relevant  guidance.
> Ensure that the OfferID contains the keyword "sentinel". Consider using the format: `microsoft-sentinel-solution-<productname>`

3. Prepare the Solution Metadata by following the guidance [here](https://github.com/Azure/Azure-Sentinel/blob/d2ee5ef22728fa7feb607a56450400712c8eaee2/Tools/Create-Azure-Sentinel-Solution/pipeline/README.md#create-solution-metadata-file). Use the PublisherID and OfferID created in #1 and #2 above. SolutionMetadata.json must be placed in solution folder created in **Step 1**. 

4. Prepare the input data file based on guidance available [here](https://github.com/Azure/Azure-Sentinel/blob/d2ee5ef22728fa7feb607a56450400712c8eaee2/Tools/Create-Azure-Sentinel-Solution/pipeline/README.md#create-input-file). The file must be placed inside the Data folder within the solution folder created in **Step 1**.


## Step 3 - Create a Pull Request

Submit a Pull Request (PR) with all of your solution content created in Step 1 and Step 2. The PR will go through automated GitHub validation. [Address potential errors](https://github.com/Azure/Azure-Sentinel/wiki#test-your-contribution) as needed.

After your content has been succesfully validated, the Microsoft Sentinel team will review your PR and reply with any feedback as needed. You can expect an initial response within five business days.

The PR will be approved and merged after any/all feedback has been incorportated and the full review is successful. After this PR is merged, a package will be auto-generated and an automated PR is raised for adding the package to the master branch to make it avalable for publishing. The package will then go through quality assurance and depending on the results, the automated PR may or may not be auto-merged.

## Step 4 - Publish your solution

1.	Sign in to [Partner Center](https://partner.microsoft.com/dashboard/home). Search and open the Offer that was created in **Step 2**.

2. [Configure](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-properties) the Offer properties.

3.	Configure the [Offer listing details](https://docs.microsoft.com/azure/marketplace/azure-app-offer-listing), including the title, description, pictures, videos, support information, and so on. 
    * As one of your search keywords, add `f1de974b-f438-4719-b423-8bf704ba2aef` to have your solution appear in the Microsoft Sentinel content hub.
    * Ensure to provide CSP (Cloud Solution Provider) Program contact and relevant CSP information as requested. This will enable you to offer the solution to CSP subscriptions and increased visibility and adoption of your solution. Refer to the [CSP FAQs](#csp-cloud-solution-provider) for further details on why this is recommended for Microsoft Sentinel solutions. 
    * If you want to start your solution in Preview (Public Preview), you can do so by appending "(Preview)" in the solution / offer title. This will ensure your offer  gets tagged with Preview tag in Microsoft Sentinel Content hub. 

4.	[Create a plan](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-plans) and select **Solution Template** as the plan type. 
    * If your offer needs to be available for customers from U.S. federal, state, local, or tribal entities, follow the steps to select the *Azure Government* check box and subsquent guidance.

5.	[Configure](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-solution) the **Solutions template** plan. This is where you’ll upload the zip file that you'd created in step two and set a version for your package. Make sure to follow the versioning guidance described in step 2, above.	

6. [Enable CSP for your offer](https://docs.microsoft.com/azure/marketplace/azure-app-marketing) by going to the *Resell through CSPs* tab in Partner Center and selecting *Any partner in the CSP program*. This will enable you to offer the solution to CSP subscriptions and increased visibility and adoption of your solution. Refer to the [CSP FAQs](#csp-cloud-solution-provider) for further details on why this is recommended for Microsoft Sentinel solutions. 

7.	[Validate and test](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-test-publish) your solution offer.  

8.	After the validation passes, [publish the offer live](https://docs.microsoft.com/azure/marketplace/create-new-azure-apps-offer-test-publish#publish-your-offer-live). This will trigger the certification process, which can take up to 3 business days. 

**Note:** The Microsoft Sentinel team will need to modify your files so that your solution appears in the Microsoft Sentinel content hub. Therefore, before going live, email the  [Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with your solutions offer ID and your **Publisher ID** so that we can make the required changes.

**Note:** You must make the offer public in order for it to show up in the Microsoft Sentinel content hub so that customers can find it.

## Feedback

[Email Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with any feedback on this process, for new scenarios not covered in this guide, or with any constraints you may encounter. 

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
If the customer, who wants to deploy your solution offer, purchased their subscription from a CSP Reseller partner, the solution will not deploy and the customer will get an error message about why. 