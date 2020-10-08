# MITRE ATT&CK for Azure Sentinel

This folder has resources to generate MITRE ATT&CK coverage for Azure Sentinel and other Microsoft threat Protection Portfolio solutions.

 **Jupyter Notebook** : Click on nbviewer Badge - [![nbviewer](https://raw.githubusercontent.com/jupyter/design/master/logos/Badges/nbviewer_badge.svg)](https://nbviewer.jupyter.org/github/Azure/Azure-Sentinel/blob/master/Sample%20Data/MITRE%20ATT%26CK/MITRE%20ATT%26CK%20for%20Azure%20Sentinel.ipynb)


- [Setup](##Setup)
- [Data Acquisition - Github](##DataAcquisition-Github)
- [Data Cleaning and Preprocessing](##DataCleaningAndPrprocessing)
- [Data Scraping](##DataScraping)
- [Data Visualization](##DataVisualization)
    - [Jupyter DataFrame Widget](###JupyterDataframerWidget)
    - [Heatmaps](###Heatmaps)
    - [Radar Plots](###RadarPlots)
    - [ATT&CK Navigator](###ATT&CKNavigator)
    - [Donut Charts](###DonutCharts)


**Raw Csv file for Azure Sentinel Detections and hunting Queries**
 
 ***KQL Query:***
 ```
 let SentinelGithub = (externaldata(MITREMatrix: string, Tactic: string, TechniqueId:string, TechniqueName:string, Platform: string , DetectionType: string , DetectionService: string , DetectionId: string, DetectionName: string, DetectionDescription: string, ConnectorId: string, DataTypes: string, Query: string , QueryFrequency: string , QueryPeriod:string , TriggerOperator: string, TriggerThreshold: string, DetectionSeverity: string, DetctionUrl: string, IngestedDate: string )
[@"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Sample%20Data/MITRE%20ATT%26CK/AzureSentinel.csv"]
);
SentinelGithub
```

**Raw Csv file for Microsoft Threat Protection Portfolio Services**
  
***KQL Query***
```
let MSFTServices = (externaldata(Alert: string, Description: string, Tactics:string, Severity:string, Provider:string, DetectionService: string)
[@"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Sample%20Data/MITRE%20ATT%26CK/MSFTAlerts.csv"]
);
MSFTServices
```

 ## Setup
![Setup](./gif/Part%201%20Setup.gif)

 ## DataAcquisition-Github
![](./gif/Part%202%20GitHub%20Download.gif)

 ## DataCleaningAndPrprocessing
![](./gif/Part%203%20Data%20Cleaning.gif)

## DataScraping
![](./gif/Part%204%20DataScraping.gif)

## DataVisualization
### JupyterDataframerWidget
![](./gif/Part%205%20Data%20Viz%20Jupyter%20widget.gif)

### Heatmaps
![](./gif/Part%205%20Data%20Viz%20Heatmap.gif)

### RadarPlots
![](./gif/Part%205%20Data%20Viz%20Radar%20plots.gif)

### ATT&CKNavigator
![](./gif/Part%205%20Data%20Viz%20ATTACK%20Navigator.gif)

### DonutCharts
![](./gif/Part%205%20Data%20Viz%20Donut%20Charts.gif)