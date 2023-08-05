# Content Hub Solutions Release Notes Guidance

The following guidelines are defined toward adding release notes across solution commits (new and updates) to ensure customers have visibility on the changes introduced allowing them to plan for solution updates:

1.  This must be a markdown (md) with the file name as ***ReleaseNotes.md***.

2.  If the release notes do not exist, please create a new markdown file. The file must be located within the individual solutions' folder (Azure-Sentinel/Solutions/\<Name of Solution\>/ReleaseNotes.md)

3.  A link to the ReleaseNotes.md file must be included in the solution description in Marketplace offer for the solution. Sample below:

![Azure Marketplace listing description](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/ReleaseNotes_OfferListing.png)

This can be added by navigating to the offer in Azure Marketplace and clicking on **Offer listing**. Add a link to the Release Notes in the Description to make it available with the offer in Content Hub.

4.  Every content commit toward a solution (new or existing) MUST also include addition or update of the release notes.

5.  Use plain, customer-centric language: Eliminate technical jargons that can potentially be unfamiliar to the customer. Make it obvious and easy for customers to zero in on what the changes are along with potential impact.

        Example -- Use "updated parser to extract EventID, EventType & Owner from the AdditionalDetails field" instead of "Added transformation to parse AdditionalDetails and extend EventID, EventType, Owner fields".

6.  Keep it short: Use descriptions about changes that are concise and quickly digestible.

7.  Include ALL changes and ensure these are identifiable by content type.

8.  Release notes must have all the updates appropriately called out:

    a.  Addition of new capabilities to the solution. These will be enrichments in the form of new content items added to the solution package.

    b.  Any updates to existing content in the solution. Some examples are:

        i.  Analytic Rule/Hunting Query/Parser logic optimization
        ii. Bug fixes to any content item
        iii. New fields or API endpoints added to Data Connector for ingestion.
        iv. New visualization added to workbooks.

    c.  Removal of any content items from the solution package.

9.  Each update note must also include the updated version of the content template.

        Example -- Data Connector UI-only update with improved onboarding instructions \| **v 1.0.1**
## Sample

The following sample can be used as reference for writing and publishing release notes:

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 2.0.1       | 01-03-2023                     | **Data Connector** UI-only update with improved onboarding instructions \| v 1.0.1
|             |                                | Modified rule logic for **Analytic Rule** \"Successful Brute Force attempt\" for better query performance \| v 1.0.2|
| 2.0.0       | 10-12-2022                     | Initial solution release |

A markdown-formatted sample is available [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReleaseNotesSample.md) that can be copied to your solution's folder. Ensure the file is renamed to ***ReleaseNotes.md***.
