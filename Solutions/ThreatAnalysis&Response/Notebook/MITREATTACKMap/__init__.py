import csv
import datetime
import glob
import io
import json
import logging
import os
import re
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import azure.functions as func
import IPython
import matplotlib.pyplot as plt
import pandas as pd
import requests
import yaml
from IPython.display import HTML, display
from ipywidgets import Layout, widgets
from pandas import json_normalize
from requests_html import HTMLSession
from msticpy.data.uploaders.loganalytics_uploader import LAUploader


def get_sentinel_queries_from_github(git_url, outputdir):
    logging.info("Downloading from Azure Sentinel Github, may take 2-3 mins..")
    r = requests.get(git_url)

    repo_zip = io.BytesIO(r.content)

    archive = zipfile.ZipFile(repo_zip, mode="r")

    # Only extract Detections and Hunting Queries Folder
    for file in archive.namelist():
        if file.startswith(
            (
                "Azure-Sentinel-master/Detections/",
                "Azure-Sentinel-master/Hunting Queries/",
            )
        ):
            archive.extract(file, path=outputdir)
    logging.info("Downloaded and Extracted Files successfully")


def parse_yaml(parent_dir, child_dir):

    sentinel_repourl = "https://github.com/Azure/Azure-Sentinel/blob/master"

    # Collect list of files recusrively uinder a folder
    yaml_queries = glob.glob(f"{parent_dir}/{child_dir}/**/*.yaml", recursive=True)
    df = pd.DataFrame()

    # Recursively load yaml Files and append to dataframe
    for query in yaml_queries:
        with open(query, "r", encoding="utf-8", errors="ignore") as f:
            parsed_yaml_df = json_normalize(yaml.load(f, Loader=yaml.FullLoader))
            parsed_yaml_df["DetectionURL"] = query.replace(parent_dir, sentinel_repourl)
            df = df.append(parsed_yaml_df, ignore_index=True, sort=True)

    if child_dir == "Detections":
        df["DetectionType"] = "Analytics"
    elif child_dir == "Hunting Queries":
        df["DetectionType"] = "Hunting"

    df["DetectionService"] = "Azure Sentinel Community Github"

    return df


def get_fusion_alerts():
    alerts_url = "https://docs.microsoft.com/azure/sentinel/fusion-scenario-reference"

    session = HTMLSession()

    r = session.get(alerts_url)
    fusion_df = pd.DataFrame(
        re.findall(r"<li><p><strong>(.*)</strong></p>", r.text), columns=["name"]
    )

    fusion_df["tactics"] = "N.A."
    fusion_df["relevantTechniques"] = "N.A."
    fusion_df["connectorId"] = "N.A."
    fusion_df["dataTypes"] = "N.A."

    for i in range(0, 5):
        fusion_df["tactics"][i] = ["InitialAccess", "Impact"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1496"]
    for i in range(5, 10):
        fusion_df["tactics"][i] = ["InitialAccess", "Exfiltration", "Collection"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T114", "T1020"]
    for i in range(10, 15):
        fusion_df["tactics"][i] = ["InitialAccess", "Exfiltration"]
        fusion_df["connectorId"][i] = [
            "MicrosoftCloudAppSecurity",
            "AzureActiveDirectoryIdentityProtection",
        ]
    for i in range(15, 20):
        fusion_df["tactics"][i] = ["Initial Access", "Exfiltration"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1567"]
    for i in range(20, 25):
        fusion_df["tactics"][i] = ["Initial Access", "Lateral Movement", "Exfiltration"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1534"]
    for i in range(25, 30):
        fusion_df["tactics"][i] = ["Initial Access", "Exfiltration"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1567"]
    for i in range(30, 35):
        fusion_df["tactics"][i] = ["InitialAccess", "Exfiltration"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1567"]
    for i in range(35, 40):
        fusion_df["tactics"][i] = ["InitialAccess", "Impact"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1485"]
    for i in range(40, 45):
        fusion_df["tactics"][i] = ["Initial Access", "Impact"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1485"]
    for i in range(45, 50):
        fusion_df["tactics"][i] = ["InitialAccess", "Impact"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1499"]
    for i in range(50, 55):
        fusion_df["tactics"][i] = ["InitialAccess", "LateralMovement"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1534"]
    for i in range(55, 60):
        fusion_df["tactics"][i] = ["InitialAccess", "LateralMovement", "Exfiltration"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1534", "T1020"]
    for i in range(60, 65):
        fusion_df["tactics"][i] = [
            "InitialAccess",
            "Persistence",
            "DefenseEvasion",
            "LateralMovement",
            "Collection",
            "Exfiltration",
            "Impact",
        ]
        fusion_df["relevantTechniques"][i] = ["T1078"]
    for i in range(65, 70):
        fusion_df["tactics"][i] = ["InitialAccess", "Impact"]
        fusion_df["relevantTechniques"][i] = ["T1078", "T1486"]

    for i in range(0, 69):
        fusion_df["connectorId"][i] = [
            "MicrosoftCloudAppSecurity",
            "AzureActiveDirectoryIdentityProtection",
        ]
        fusion_df["dataTypes"][i] = ["SecurityAlert"]

    # Custom dataset for non-standard formatted alerts in the doc. - May need updates to keep it current
    df2 = pd.DataFrame(
        [
            [
                "PowerShell made a suspicious network connection, followed by anomalous traffic flagged by Palo Alto Networks firewall",
                ["Execution"],
                ["T1059"],
                ["MicrosoftDefenderAdvancedThreatProtection", "PaloAltoNetworks"],
                ["SecurityAlert"],
            ],
            [
                "Suspicious remote WMI execution followed by anomalous traffic flagged by Palo Alto Networks firewall",
                ["Execution", "Discovery"],
                ["T1047"],
                ["MicrosoftDefenderAdvancedThreatProtection", "PaloAltoNetworks"],
                ["SecurityAlert"],
            ],
            [
                "Network request to TOR anonymization service followed by anomalous traffic flagged by Palo Alto Networks firewall",
                ["CommandAndControl"],
                ["T1573", "T1090"],
                ["MicrosoftDefenderAdvancedThreatProtection", "PaloAltoNetworks"],
                ["SecurityAlert"],
            ],
            [
                "Outbound connection to IP with a history of unauthorized access attempts followed by anomalous traffic flagged by Palo Alto Networks firewall",
                ["CommandAndControl"],
                ["T1071"],
                ["MicrosoftDefenderAdvancedThreatProtection", "PaloAltoNetworks"],
                ["SecurityAlert"],
            ],
            [
                "Suspected use of attack framework followed by anomalous traffic flagged by Palo Alto Networks firewall",
                [
                    "InitialAccess",
                    "Execution",
                    "LateralMovement",
                    "PrivilegeEscalation",
                ],
                ["T1190", "T1203", "T1210", "T1068"],
                ["MicrosoftDefenderAdvancedThreatProtection", "PaloAltoNetworks"],
                ["SecurityAlert"],
            ],
        ],
        columns=[
            "name",
            "tactics",
            "relevantTechniques",
            "connectorId",
            "dataTypes",
        ],
    )

    result = fusion_df.append(df2, ignore_index=True)
    result["DetectionType"] = "Fusion"
    result["DetectionService"] = "Azure Sentinel"
    result["DetectionURL"] = "https://docs.microsoft.com/azure/sentinel/fusion"

    # Exploding columns to flatten the table
    columns_to_expand = [
        "tactics",
        "relevantTechniques",
        "connectorId",
        "dataTypes",
    ]
    for column in columns_to_expand:
        result = result.explode(column).reset_index(drop=True)

    # Populate new column Platform based on custom mapping
    result["Platform"] = result.connectorId.map(platform_mapping)
    result = result.explode("Platform").reset_index(drop=True)

    result["IngestedDate"] = date.today()

    return result


def clean_and_preprocess_data(df):

    columns = [
        "DetectionType",
        "DetectionService",
        "id",
        "name",
        "description",
        "query",
        "queryFrequency",
        "queryPeriod",
        "triggerOperator",
        "triggerThreshold",
        "tactics",
        "relevantTechniques",
        "requiredDataConnectors",
        "severity",
        "DetectionURL",
        "IngestedDate",
    ]

    # Reording columns
    df = df[columns]

    # Inserting additional columns to list at specific index for later use
    columns.insert(5, "connectorId")
    columns.insert(6, "dataTypes")

    # Ignoring the records with invalid connector values
    df = df[df.requiredDataConnectors.apply(lambda x: x != [{"connectorId": []}])]

    # Handle null values in required data connectors
    isnull = df.requiredDataConnectors.isnull()
    if len(df[isnull]) > 0:
        df.loc[isnull, "requiredDataConnectors"] = [[[]] * isnull.sum()]

    no_of_records_with_emptylist_connectors = len(
        df[df["requiredDataConnectors"].map(lambda d: len(d)) == 0]
    )

    # Separate Null and Not Null requiredDataConnectors
    not_null_df = (
        df[df["requiredDataConnectors"].map(lambda d: len(d)) > 0]
        .reset_index()
        .drop("index", axis=1)
    )
    empty_null_df = (
        df[df.requiredDataConnectors.isnull()].reset_index().drop("index", axis=1)
    )
    null_df = (
        df[df["requiredDataConnectors"].map(lambda d: len(d)) == 0]
        .reset_index()
        .drop("index", axis=1)
    )

    # Exploding columns to flatten the table
    columns_to_expand = ["tactics", "relevantTechniques", "requiredDataConnectors"]
    for column in columns_to_expand:
        not_null_df = not_null_df.explode(column).reset_index(drop=True)

    # #Apply Data wrangling to derive columns from Json response
    final_not_null_df = pd.DataFrame(
        not_null_df["requiredDataConnectors"].values.tolist()
    )

    # Concatenate 2 dataframs vertically
    result_not_null_df = pd.concat([not_null_df, final_not_null_df], axis=1)

    # Exploding dataTypes column
    result_not_null_df = result_not_null_df.explode("dataTypes").reset_index(drop=True)
    new_columns = [
        "DetectionType",
        "DetectionService",
        "id",
        "name",
        "description",
        "connectorId",
        "dataTypes",
        "query",
        "queryFrequency",
        "queryPeriod",
        "triggerOperator",
        "triggerThreshold",
        "tactics",
        "relevantTechniques",
        "severity",
        "DetectionURL",
        "IngestedDate",
    ]
    result_not_null_df = result_not_null_df[new_columns]

    result_not_null_df["Platform"] = result_not_null_df.connectorId.map(
        platform_mapping
    )
    result_not_null_df = result_not_null_df.explode("Platform").reset_index(drop=True)

    # Exploding columns to flatten the table
    columns_to_expand = ["tactics", "relevantTechniques"]
    for column in columns_to_expand:
        null_df = null_df.explode(column).reset_index(drop=True)

    null_df["connectorId"] = "CustomConnector"
    null_df["dataTypes"] = null_df.DetectionURL.apply(
        lambda x: pd.Series(str(x).split("/")[-2] + "_CL")
    )
    null_df["Platform"] = ""

    new_columns.append("Platform")
    result_null_df = null_df[new_columns]

    result = pd.concat([result_not_null_df, result_null_df], axis=0)

    return result




# Custom ConnectorId to Platform Mapping
platform_mapping = {
    "AIVectraDetect": ["Azure", "Windows", "Linux"],
    "AlsidForAD": ["Azure", "Azure AD"],
    "AWS": ["AWS"],
    "AWSS3": ["AWS", "SaaS"],
    "AzureActiveDirectory": ["Azure", "Azure AD"],
    "AzureActiveDirectoryIdentityProtection": ["Azure", "Azure AD"],
    "AzureActivity": ["Azure", "SaaS"],
    "AzureFirewall": ["Azure", "Windows", "Linux"],
    "AzureDevOpsAuditing": ["Azure", "SaaS"],
    "AzureMonitor": ["SaaS"],
    "AzureMonitor(IIS)": ["Azure"],
    "AzureMonitor(Keyvault)": ["Azure"],
    "AzureMonitor(Query Audit)": ["Azure"],
    "AzureMonitor(VMInsights)": ["Azure", "Windows", "Linux"],
    "AzureMonitor(WindowsEventLogs)": ["Azure", "Windows"],
    "AzureMonitor(WireData)": ["Azure", "Windows", "Linux"],
    "AzureNetworkWatcher": ["Azure", "Windows", "Linux"],
    "AzureSecurityCenter": ["Azure", "SaaS"],
    "Barracuda": ["Azure", "Windows", "Linux"],
    "BehaviorAnalytics": ["Azure AD", "Azure", "Windows"],
    "CEF": ["Azure", "Windows", "Linux"],
    "CheckPoint": ["Azure", "Windows", "Linux"],
    "CiscoASA": ["Azure", "Windows", "Linux"],
    "CiscoUmbrellaDataConnector": ["Windows", "Linux"],
    "CognniSentinelDataConnector": ["SaaS"],
    "CyberpionSecurityLogs": ["SaaS"],
    "CustomConnector": ["Unknown"],
    "DNS": ["Azure", "Windows", "Linux"],
    "EsetSMC": ["Azure", "Windows", "Linux"],
    "F5": ["Azure", "Windows", "Linux"],
    "Fortinet": ["Azure", "Windows", "Linux"],
    "GitHub": ["SaaS", "Windows", "Linux"],
    "InfobloxNIOS": ["Azure", "Windows", "Linux"],
    "Microsoft365Defender": ["Azure", "Windows"],
    "MicrosoftCloudAppSecurity": ["Azure", "AWS", "GCP", "SaaS"],
    "MicrosoftDefenderAdvancedThreatProtection": ["Windows", "Linux"],
    "MicrosoftThreatProtection": ["Azure", "Windows"],
    "Office365": ["Office 365"],
    "OfficeATP": ["Office 365"],
    "OktaSSO": ["Azure AD", "AWS", "GCP", "SaaS"],
    "PaloAltoNetworks": ["Azure", "Windows", "Linux"],
    "ProofpointPOD": ["Office 365"],
    "ProofpointTAP": ["Office 365"],
    "PulseConnectSecure": ["Azure", "Windows", "Linux"],
    "QualysVulnerabilityManagement": ["Azure", "Windows", "Linux", "macOS"],
    "SecurityEvents": ["Windows"],
    "SophosXGFirewall": ["Azure", "Windows", "Linux"],
    "SymantecProxySG": ["Azure", "Windows", "Linux"],
    "SymantecVIP": ["Azure", "Windows", "Linux"],
    "Syslog": ["Linux"],
    "ThreatIntelligence": [
        "Windows",
        "Linux",
        "macOS",
        "Azure",
        "AWS",
        "Azure AD",
        "Office 365",
    ],
    "ThreatIntelligenceTaxii": [
        "Windows",
        "Linux",
        "macOS",
        "Azure",
        "AWS",
        "Azure AD",
        "Office 365",
    ],
    "TeamsLogs": ["Windows", "Linux", "macOS"],
    "TrendMicro": ["Windows", "Linux", "macOS"],
    "TrendMicroXDR": ["Windows", "Linux", "macOS"],
    "VMwareCarbonBlack": ["Windows", "Linux", "macOS"],
    "WAF": ["Azure", "SaaS"],
    "WindowsFirewall": ["Windows"],
    "WindowsSecurityEvents": ["Windows"],
    "Zscaler": ["Azure", "Windows", "Linux"],
    "ZoomLogs": ["SaaS"],
}


def get_azure_defender_alerts():
    alerts_url = (
        "https://docs.microsoft.com/azure/security-center/alerts-reference"
    )
    list_of_df = pd.read_html(alerts_url)
    providers = [
        "Windows",
        "Linux",
        "Azure App Service",
        "Azure Kubernetes Service clusters",
        "Containers- Host Level",
        "SQL Database and Synapse Analytics",
        "Open source relational Databases",
        "Azure Resource Manager",
        "Azure DNS",
        "Azure Storage",
        "Azure Cosmos DB (Preview)",
        "Azure Network Layer",
        "Azure Key Vault",
        "Azure DDoS Protection",
        "Security Incident",
    ]
    for i in range(15):
        list_of_df[i]["Provider"] = providers[i]

    # Clean-up dataset by renaming some columns
    list_of_df[0] = list_of_df[0].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[1] = list_of_df[1].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[2] = list_of_df[2].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[3] = list_of_df[3].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[4] = list_of_df[4].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[6] = list_of_df[6].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[7] = list_of_df[7].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[8] = list_of_df[8].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[9] = list_of_df[9].rename(columns={"Alert (alert type)": "Alert"})
    list_of_df[12] = list_of_df[12].rename(columns={"Alert (alert type)": "Alert"})

    # Merge all the tables
    frames = [
        list_of_df[0],
        list_of_df[1],
        list_of_df[2],
        list_of_df[3],
        list_of_df[4],
        list_of_df[5],
        list_of_df[6],
        list_of_df[7],
        list_of_df[8],
        list_of_df[9],
        list_of_df[10],
        list_of_df[11],
        list_of_df[12],
        list_of_df[13],
        list_of_df[14],
    ]

    azdefender_df = pd.concat(frames).reset_index().dropna().drop("index", axis=1)

    # Add and Rename columns
    azdefender_df["Detection Service"] = (
        "Microsoft Defender" + " for " + azdefender_df["Provider"]
    )
    azdefender_df = azdefender_df.rename(
        columns={"MITRE tactics(Learn more)": "Tactic"}
    )
    azdefender_df[["Alert", "Description", "Severity", "Provider", "Tactic"]]
    azdefender_df["DetectionURL"] = alerts_url
    azdefender_df["connectorId"] = "AzureSecurityCenter"
    azdefender_df["dataTypes"] = "SecurityAlert (ASC)"

    return azdefender_df


def get_azure_ipc_alerts():
    alerts_url = "https://docs.microsoft.com/azure/active-directory/identity-protection/concept-identity-protection-risks"
    list_of_df = pd.read_html(alerts_url)

    # Merge All dataframes
    frames = (list_of_df[0], list_of_df[1], list_of_df[2])
    aip_df = pd.concat(frames).dropna().reset_index().drop("index", axis=1)

    # Add and Rename columns
    aip_df["Tactic"] = "N.A."
    aip_df["Severity"] = "N.A."
    aip_df["Provider"] = "N.A."
    aip_df["Detection Service"] = "Azure Identity Protection Center (IPC)"
    aip_df = aip_df.rename(columns={"Risk detection": "Alert"}).drop(
        "Detection type", axis=1
    )

    aip_df["connectorId"] = "AzureActiveDirectoryIdentityProtection"
    aip_df["dataTypes"] = "SecurityAlert (IPC)"
    aip_df["DetectionURL"] = alerts_url

    return aip_df


def get_azure_defender_identity_alerts():
    alerts_url = "https://docs.microsoft.com/azure-advanced-threat-protection/suspicious-activity-guide?tabs=external"

    list_of_df = pd.read_html(alerts_url)
    atp_df = list_of_df[0].reset_index().dropna().drop("index", axis=1)
    atp_df["Description"] = "N.A."
    atp_df["Provider"] = "N.A."

    atp_df = atp_df.rename(
        columns={"Security alert name": "Alert", "MITRE ATT&CK Matrix™": "Tactic"}
    ).drop("Unique external ID", axis=1)
    atp_df["Detection Service"] = "Microsoft Defender for Identity"

    atp_df = atp_df[
        ["Alert", "Description", "Tactic", "Severity", "Provider", "Detection Service"]
    ]

    atp_df["connectorId"] = "AzureAdvancedThreatProtection"
    atp_df["dataTypes"] = "SecurityAlert (AATP)"
    atp_df["DetectionURL"] = alerts_url
    return atp_df


def get_mcas_alerts():
    alerts_url = (
        "https://docs.microsoft.com/cloud-app-security/investigate-anomaly-alerts"
    )

    session = HTMLSession()

    r = session.get(alerts_url)
    mcas_df = pd.DataFrame(
        re.findall(r"<h3 id=.*>(.*)</h3>", r.text), columns=["Alert"]
    )

    mcas_df["Description"] = "N.A."

    mcas_df["Tactic"] = "N.A."

    for i in range(6):
        mcas_df["Tactic"][i] = "InitialAccess"
    for i in range(6, 9):
        mcas_df["Tactic"][i] = "Execution"
    for i in range(9, 13):
        mcas_df["Tactic"][i] = "Persistence"
    mcas_df["Tactic"][13] = "PrivilegeEscalation"
    mcas_df["Tactic"][14] = "CredentialAccess"
    for i in range(15, 18):
        mcas_df["Tactic"][i] = "Collection"
    for i in range(18, 21):
        mcas_df["Tactic"][i] = "Exfiltration"
    for i in range(21, 24):
        mcas_df["Tactic"][i] = "Impact"

    mcas_df["Severity"] = "N.A."
    mcas_df["Provider"] = "N.A."
    mcas_df["Detection Service"] = "Microsoft Defender for Cloud Apps"
    mcas_df["DetectionURL"] = alerts_url
    mcas_df["connectorId"] = "MicrosoftCloudAppSecurity"
    mcas_df["dataTypes"] = "SecurityAlert (MCAS) | McasShadowItReporting"

    return mcas_df


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    try:
        # Download the Azure Sentinel Github repo as ZIP
        tmp_path = str(Path.joinpath(Path(tempfile.gettempdir())))
        azsentinel_git_url = (
            "https://github.com/Azure/Azure-Sentinel/archive/master.zip"
        )
        get_sentinel_queries_from_github(git_url=azsentinel_git_url, outputdir=tmp_path)

        base_dir = tmp_path + "/Azure-Sentinel-master"
        detections_df = parse_yaml(parent_dir=base_dir, child_dir="Detections")
        hunting_df = parse_yaml(parent_dir=base_dir, child_dir="Hunting Queries")

        fusion_df = get_fusion_alerts()

        frames = [detections_df, hunting_df]
        sentinel_github_df = pd.concat(frames).reset_index()
        sentinel_github_df = sentinel_github_df.copy()
        sentinel_github_df["DetectionURL"] = sentinel_github_df[
            "DetectionURL"
        ].str.replace(" ", "%20", regex=True)
        sentinel_github_df["IngestedDate"] = date.today()

        # Displaying basic statistics of yaml files
        logging.info("Azure Sentinel Github Stats...")
        logging.info(
            f"""Total Queries in Azure Sentinel Github:: {len(sentinel_github_df)} 
            No of Detections :: {len(detections_df)} 
            No of Hunting Queries:: {len(hunting_df)}

        Total No of Fusion ML Detections:: {fusion_df["name"].nunique()}
            """
        )

        result = clean_and_preprocess_data(df=sentinel_github_df)

        # Append the Fusion dataset to Pre-procesed result
        result = result.append(fusion_df, ignore_index=True)
        logging.info(f"The no of records in results: {len(result)}")

        # Renaming columns
        result = result.rename(
            columns={
                # "matrix": "MITREMatrix",
                "platform": "Platform",
                "id": "DetectionId",
                "name": "DetectionName",
                "description": "DetectionDescription",
                "connectorId": "ConnectorId",
                "dataTypes": "DataTypes",
                "severity": "DetectionSeverity",
                "tactics": "Tactic",
                "relevantTechniques": "TechniqueId",
                "query": "Query",
                "queryFrequency": "QueryFrequency",
                "queryPeriod": "QueryPeriod",
                "triggerOperator": "TriggerOperator",
                "triggerThreshold": "TriggerThreshold",
                "DetectionURL": "DetectionUrl",
            }
        )

        # Column Seletion and Ordering
        columns = [
            "Tactic",
            "TechniqueId",
            "Platform",
            "DetectionType",
            "DetectionService",
            "DetectionId",
            "DetectionName",
            "DetectionDescription",
            "ConnectorId",
            "DataTypes",
            "Query",
            "QueryFrequency",
            "QueryPeriod",
            "TriggerOperator",
            "TriggerThreshold",
            "DetectionSeverity",
            "DetectionUrl",
            "IngestedDate",
        ]
        result = result[columns]

        # Drop duplicates before exporting
        result = result.loc[result.astype(str).drop_duplicates().index]

        logging.info(f"The no of records in newdf: {len(result)}")

        # Export the whole dataset
        logging.info(f"Writing csv files to temporary directory")
        out_path = tmp_path + "/AzureSentinel.csv"

        az_defender_alerts = get_azure_defender_alerts()
        logging.info(
            f"No of alerts scraped from Azure Defender: {len(az_defender_alerts)}"
        )
        az_ipc_alerts = get_azure_ipc_alerts()
        logging.info(f"No of alerts scraped from Azure IPC: {len(az_ipc_alerts)}")
        az_defender_for_identity_alerts = get_azure_defender_identity_alerts()
        logging.info(
            f"No of alerts scraped from Azure Defender Identity: {len(az_defender_for_identity_alerts)}"
        )
        mcas_df = get_mcas_alerts()
        logging.info(f"No of alerts scraped from MCAS: {len(mcas_df)}")
        frames = [
            az_defender_alerts,
            az_ipc_alerts,
            az_defender_for_identity_alerts,
            mcas_df,
        ]
        msft_df = pd.concat(frames)
        msft_df["platform"] = "Azure"

        columns = [
            "id",
            "relevantTechniques",
            "query",
            "queryFrequency",
            "queryPeriod",
            "triggerOperator",
            "triggerThreshold",
        ]
        for column in columns:
            msft_df[column] = "N.A."

        msft_df["DetectionType"] = "Analytics"
        msft_df["DetectionService"] = "Microsoft Built-in Alerts"
        msft_df["IngestedDate"] = date.today()

        msft_df = msft_df.rename(
            columns={
                "platform": "Platform",
                "id": "DetectionId",
                "Alert": "DetectionName",
                "Description": "DetectionDescription",
                "connectorId": "ConnectorId",
                "dataTypes": "DataTypes",
                "Severity": "DetectionSeverity",
                "Tactic": "Tactic",
                "relevantTechniques": "TechniqueId",
                "query": "Query",
                "queryFrequency": "QueryFrequency",
                "queryPeriod": "QueryPeriod",
                "triggerOperator": "TriggerOperator",
                "triggerThreshold": "TriggerThreshold",
                "DetectionURL": "DetectionUrl",
            }
        )

        columns = [
            "Tactic",
            "TechniqueId",
            "Platform",
            "DetectionType",
            "DetectionService",
            "DetectionId",
            "DetectionName",
            "DetectionDescription",
            "ConnectorId",
            "DataTypes",
            "Query",
            "QueryFrequency",
            "QueryPeriod",
            "TriggerOperator",
            "TriggerThreshold",
            "DetectionSeverity",
            "DetectionUrl",
            "IngestedDate",
        ]

        msft_df = msft_df[columns]
        logging.info(f"No of total MSFT alerts: {len(msft_df)}")

        frames = [result, msft_df]
        final = pd.concat(frames)

        # Export the whole dataset with headers
        final.to_csv(out_path, index=False)

        # Read WorkspaceId and Key
        customer_workspaceid = os.environ.get("WorkspaceID")
        customer_sharedkey = os.environ.get("WorkspaceKey")
        logging.info(
            f"Instantiating LAUploader and writing output to table MITREATTACKmap"
        )
        logging.info(f"No of total records to be sent to Azure Sentinel: {len(final)}")

        # Instanciate our Uploader
        la_up = LAUploader(
            workspace=customer_workspaceid,
            workspace_secret=customer_sharedkey,
            debug=True,
        )
        # Upload files
        la_up.upload_file(file_path=out_path, table_name="MITREATTACKMap")

    except Exception as e:
        logging.error(f"Error Details: {e}")
