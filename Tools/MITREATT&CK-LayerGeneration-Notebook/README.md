# MITRE ATT&CK for Microsoft Sentinel

This folder has resources to generate MITRE ATT&CK coverage for Microsoft Sentinel and other Microsoft threat Protection Portfolio solutions.

 **Jupyter Notebook** : Click on nbviewer Badge - [![nbviewer](https://raw.githubusercontent.com/jupyter/design/master/logos/Badges/nbviewer_badge.svg)](https://nbviewer.jupyter.org/github/Azure/Azure-Sentinel/blob/master/Tools/MITREATT%26CK-LayerGeneration-Notebook/MITRE%20ATT%26CK%20for%20Microsoft%20Sentinel.ipynb)


- [Setup](#setup)
- [Data Acquisition - Github](#data-acquisition-github)
- [Data Cleaning and Preprocessing](#data-cleaning-and-preprocessing)
- [Data Scraping](#data-scraping)
- [Data Visualization](#data-visualization)
    - [Jupyter DataFrame Widget](#jupyter-dataframe-widget)
    - [Heatmaps](#heatmaps)
    - [Radar Plots](#radarplots)
    - [ATT&CK Navigator](#attck-navigator)
    - [Donut Charts](#donutcharts)


**Raw Csv file for Microsoft Sentinel Detections and hunting Queries**
 
 ***KQL Query:***
 ```
 let SentinelGithub = (externaldata(Tactic: string, TechniqueId: string, Platform: string, DetectionType: string, DetectionService: string, DetectionId: guid, DetectionName: string, DetectionDescription: string, ConnectorId: string, DataTypes: string, Query: string, QueryFrequency: string, QueryPeriod: string, TriggerOperator: string, TriggerThreshold: real, DetectionSeverity: string, DetectionUrl: string, IngestedDate: datetime)
[@"https://raw.githubusercontent.com/microsoft/mstic/master/PublicFeeds/MITREATT%26CK/MicrosoftSentinel.csv"] with (format="csv", ignoreFirstRecord=True)
);
SentinelGithub
```

**Raw Csv file for Microsoft Threat Protection Portfolio Services**
  
***KQL Query***
```
let MSFTBuiltinAlerts = (externaldata(Alert: string, Description: string, Tactics:string, Severity:string, Provider:string, DetectionService: string)
[@"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/MITREATT%26CK-LayerGeneration-Notebook/MSFT-Builtin-Alerts.csv"] with (format="csv", ignoreFirstRecord=True)
);
MSFTBuiltinAlerts
```

 ## Setup
![Setup](./gif/Part%201%20Setup.gif)

 ## Data Acquisition Github
![](./gif/Part%202%20GitHub%20Download.gif)

 ## Data Cleaning And Preprocessing
![](./gif/Part%203%20Data%20Cleaning.gif)

## Data Scraping
![](./gif/Part%204%20DataScraping.gif)

## Data Visualization
### Jupyter Dataframe Widget
![](./gif/Part%205%20Data%20Viz%20Jupyter%20widget.gif)

### Heatmaps
![](./gif/Part%205%20Data%20Viz%20Heatmap.gif)

### RadarPlots
![](./gif/Part%205%20Data%20Viz%20Radar%20plots.gif)

### ATT&CK Navigator
![](./gif/Part%205%20Data%20Viz%20ATTACK%20Navigator.gif)

### DonutCharts
![](./gif/Part%205%20Data%20Viz%20Donut%20Charts.gif)