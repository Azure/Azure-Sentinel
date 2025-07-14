# SOC Process Framework Solution for Microsoft Sentinel
## Author: Rin Ure

![SOC Process Framework](./SOCProcessFrameworkSolutionLanding.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Workbooks](#workbooks)
1. [Watchlists](#watchlists)
1. [Playbooks](#playbooks)
1. [Post Deployment Steps](#postdeployment)

<a name="overview">

## Overview
This Solution contains all resources for the SOC Process Framework Microsoft Sentinel Solution.
The SOC Process Framework Solution is built in order to easily integrate with Microsoft Sentinel and build a standard SOC Process and Procedure Framework within your Organization.

By deploying this solution, you'll be able to monitor progress within your SOC Operations and update the SOC CMMI Assessment Score.
This solution consists of the following resources:
- Integrated workbooks interconnected into a single workbook for single pane of glass operation.
- One Playbook for pushing SOC Actions to your Incidents.
- Multiple Watchlists helping you maintain and organize your SOC efforts, including IR Planning, SOC CMMI Assessment Score, and many more.

<a name="workbooks">

## Workbooks
The workbooks contained in this solution have visualizations about the SOC Progress, Procedures, and Activity and provides an overview of the overall SOC Maturity.
These workbooks and their dependances are deployed for you through this solution.

<a name="watchlists">

## Watchlists
The watchlists contained within this solution have information that pertain to Incident Response Planning, the SOC Maturity (CMMI) Scoring, Recommended SOC Actions, and more...
All of these watchlists give the customer ease of access to updating pertanant information regarding their SOC Operations and more.

<a name="playbooks">

## Playbooks
Currently the only Playbook in this solution is the Get-SOCActions Playbook for delivering custom Analyst Actions to take per Incident. This allows Organizations the ability to create/add their own scripted actions they want an Analyst to take. After deploying this Solution, please see the Post-Deployment Instructions before running the Playbook.

<a name="postdeployment">

### Post-Deployment Instructions
**1. After deploying the playbook, you must authorize the connections leveraged and assign permissions**

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.

**2. Assign Microsoft Sentinel Responder Role to Playbook**

This playbook uses a managed identity, which must have the Microsoft Sentinel Responder role assigned in the Sentinel instances to enable adding actions.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your Sentinel Workspace is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder'.
7. Click Save to assign the role.

**Note: If you've deployed the [SOC Process Framework Playbook](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/SOC Process Framework/Playbooks/Get-SOCActions/azuredeploy.json) playbook, you will only need to authorize the Microsoft Sentinel connection.**