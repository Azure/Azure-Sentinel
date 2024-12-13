# Module 7 - Threat Intelligence

#### 🎓 Level: 300 (Intermediate)
#### ⌛ Estimated time to complete this lab: 20 minutes

This module will demonstrate how to use Microsoft Sentinel Threat Intelligence (TI) features and product integration points.
During this module we rely on TI data that we ingested in [Module 2](Module-2-Data-Connectors.md), so please make sure you have completed that module.
In this module we will also discover how to visualize and use this data as part of investigation and detection.


#### Prerequisites
This module assumes that you completed [Module 1](Module-1-Setting-up-the-environment.md), and [Module 2](Module-2-Data-Connectors.md) exercise 3 which enables the Microsoft Defender Threat Intelligence (Preview) connector.


### Exercise 1: Threat Intelligence data connectors

#### Task 1 : Microsoft Defender Threat Intelligence (Preview)

This connector is currently in public preview and ingests Microsoft Threat Intelligence indicators automatically into the ThreatIntelligenceIndicator table. MDTI provides a set of indicators and access to the https://ti.defender.microsoft.com portal at no additional cost, with the premium features of the MDTI portal and API requiring licensing.

1. On the left navigation open the connector page and search **Microsoft Defender Threat Intelligence (Preview)**

2. On the bottom right pane press **Open connector page**

![ti](../Images/TI1.png)

3. Review the data received and confirm that the connector is already ingesting indicators.

 ![ti](../Images/TI9.png)

### Exercise 2: Explore the Threat Intelligence menu

As we discussed in the previous exercise, we have several ways to ingest TI data into Microsoft Sentinel. You can use one of the many available integrated Threat Intelligence Platform (TIP) products or you can connect to TAXII servers to take advantage of any STIX-compatible threat intelligence feed.

The ingested Indicators of Compromise (IOC) coming from any of these TI feeds, is stored in a dedicated table called **ThreatIntelligenceIndicator**, and visible on the Threat Intelligence menu on the left navigation menu.

#### Task 1: Review the TI data into Microsoft Sentinel Logs interface.

1. On the left navigation click on **Logs**, this will redirect you to the Log Analytics query interface. On the query interface we can see on the left side the tables with the relevant fields.

2. Microsoft Sentinel built-in tables have a predefined schema, to be able to see the **ThreatIntelligenceIndicator** schema, run the following query: 

 ```powershell
 ThreatIntelligenceIndicator
| getschema
   ```

![schema](../Images/TI-schema.png)

3.	Let's explore and delve into the TI table. Run the following query which takes 10 records from the table:

 ```powershell
ThreatIntelligenceIndicator
| take 10
   ```

To understand if a specific IOC is active, we need to have a closer look at the following columns:

- **ExpirationDateTime [UTC]**
- **Acitve** 

On our example, we can see that the IOC is an IP that is active with future Expiration date. This means that our matching detection rules (which we will review in the next exercise) will take this IOC into consideration when correlating with data sources. 

![Acitve](../Images/TI-active.png)


#### Task 2: Review and manage TI IOC's in Microsoft Sentinel Threat intelligence menu.

After we ingested our TI data into the ThreatIntelligenceIndicator table, our mission is to review how our SOC can leverage and manage the TI menu to allow us to search, tag and manage the lifecycle of IOCs.

 
1. On the Microsoft Sentinel left menu press on the Threat intelligence (Preview)
This menu is a visual representation of the ThreatIntelligenceIndicator table.

![Acitve](../Images/m7-Tiblade.png)


2. Select one IOC from the main pane and notice that the right  pane changed accordingly and present the metadata of the selected IOC.

![Acitve](../Images/m7-Tiblade1.png)
	
3. On the top area of the main blade, we can filter the list of the IOC's based on a specific parameters. In our case, we only ingested one type of IOC (IP), but the **Type** filter allow us to filter based on different types. If we ingested IOC's from multiple TI data sources, the **source** filter allows us to slice it.

![Acitve](../Images/m7-ITbladeFilter.png)


#### Task 3: add new TI IOC manually in Microsoft Sentinel Threat intelligence menu
	
Part of the SOC analyst's job is to manually add an IOC into the TI index from time to time. This allows other data sources and detections to correlate and detect interaction with this IOC.

1. On the **Threat intelligence (Preview)** top menu, click on **Add new**, this will open the **New indicator** dialog:

2. In the drop down, select **url** and add this url: *http://phishing.com*.

![Acitve](../Images/TI2.png)

3. Add **tags** that will help us to add metadata on this IOC. In our example, we want to tag this IOC with its associated incident ID. On the add tag pop-up write **Incident 4326** and press **OK**.
	 
![Acitve](../Images/m7-tibladeaddtag.png)

4. On the **Thread types** select **malicious-activity**
	
5. Add a **Description** and set the **Confidence** level to 80, set up the **Valid from** date to today and the **Valid until** to two weeks from now.

6. Press **Apply**

![Acitve](../Images/m7-fullnewIOC.png)

7. Notice to the newly created IOC on the TI menu.

8. Be aware that every new IOC added in the TI menu, will be automatically added to the ThreatIntelligenceIndicator table. You can validate it by opening the **Logs** menu and run the query below.

```kusto
ThreatIntelligenceIndicator
| search "http://phishing.com"
```

9. As we want to view the description column, we need to modify the column order for the menu by select the **column** button on the top bar. 

![Acitve](../Images/m7-tibladecolumnorder.png)

10. Once the **Choose columns** opened in the right side, select **Description** and click **Apply**.

After couple of days we got a new information from our internal TI team that this new IOC is not relevant anymore and we need to delete it.

12. Select the newly created manual IOC and press delete

![Acitve](../Images/m7-deleteTI.png)


### Exercise 3: Analytics Rules based on Threat Intelligence data

One of the main values of the TI data is on Analytics rules. In this exercise we will review the analytics rules types we have in Microsoft Sentinel that correlate with our ingested TI.

#### Task 1: Review and enable TI mapping analytics rules

1. From the Microsoft Sentinel portal, click on **Analytics** and then switch to **Rule Templates** tab.

2. Click on the **Add Filter** and choose **Data Sources** from the dropdown, then select **Microsoft Defender Threat Intelligence (Preview)**. Click **Apply** to apply the filter.

![TImapping](../Images/TI10.png)

3. As you can see, there is a long list of resulting alert templates. These all will correlate your different data sources with the IOCs present in your TI table (ThreatIntelligenceIndicator), to detect any trace of malicious indicators of compromise in your organization's logs. You can see more information about these rules [here](https://docs.microsoft.com/azure/sentinel/work-with-threat-indicators#detect-threats-with-threat-indicator-based-analytics).

4. As you may know, it is free to enable analytics rules in Microsoft Sentinel, so the best practice is to enable all the ones that apply to data sources that you are ingesting.

#### Task 2: Review and enable Threat Intelligence Matching Analytics rule

1. From the Microsoft Sentinel portal, click on **Analytics** and then switch to **Rule Templates** tab.

2. Click on the **Rule Type** filter and select **Threat Intelligence**. The resulting rule template matches Microsoft-generated threat intelligence data with the logs you have ingested into Microsoft Sentinel. The alerts are very high fidelity and are turned ON by default. Visit [this link](https://docs.microsoft.com/azure/sentinel/tutorial-detect-threats-built-in#use-built-in-analytics-rules) for more information about this type of rule.

3. Select the rule template and notice the different data sources that are supported (at the time of writing, these are CEF, Syslog and DNS). Click on **Create rule**.

![TImatching](../Images/TI3.png)

4. In the wizard, click on **Review** and **Create**.


### Exercise 5: Treat Intelligence workbook

Workbooks provide powerful interactive dashboards that give you insights into all aspects of Microsoft Sentinel, and threat intelligence is no exception. In this exercise you will explore a purpose-built workbook to visualize key information about your threat intelligence in Microsoft Sentinel.

1. Select **Workbooks** from the Threat management section of the Microsoft Sentinel menu.

2. Find the workbook titled **Threat Intelligence** and verify there's a green check mark next to the **ThreatIntelligenceIndicator** table as shown below.

3. Select the **Save** button and choose an Azure location to store the workbook. This step is required if you are going to modify the workbook in any way and save your changes.

![TImatching](../Images/TI5.png)

4. Now select the **View saved workbook** button to open the workbook for viewing and editing. 

5. You will find some pre-built visualizations that show you the indicators imported into Sentinel over time, by type and provider. To modify or add a new chart, select the **Edit** button at the top of the page to enter editing mode for the workbook.

![TIworkbook](../Images/TI6.png)

6. Let's now add a new chart of threat indicators by threat type. To do this, scroll to the very bottom of the page and select **Add Query**.

![TIworkbook](../Images/TI7.png)

7. Add the following text to the Log Analytics workspace Log Query text box:

```kusto
ThreatIntelligenceIndicator
| summarize count() by ThreatType
```

8. In the Visualization drop-down, select **Bar chart**.

![TIworkbook](../Images/TI8.png)

9. Select the Done editing button. You’ve created a new chart for your workbook 😀.

**Congratulations, you have completed Module 7!**. You can now continue to **[Module 8 - Microsoft Sentinel Solutions](./Module-8-Sentinel-Solutions.md)**
