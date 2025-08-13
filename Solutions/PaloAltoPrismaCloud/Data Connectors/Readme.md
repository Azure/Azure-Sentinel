# Integrating Palo Alto Prisma Cloud CSPM into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#step2)
- [Steps to get the Access Key & Secret Key from the PrismaCloudCSPM](#Key)
- [Steps to get the Base URL](#url)

## Introduction

The Palo Alto Prisma Cloud CSPM data connector enables seamless integration between your Prisma Cloud CSPM instance and Microsoft Sentinel, eliminating the need for custom code. Built on the Codeless Connector Framework (CCF), this connector streamlines the collection and ingestion of alert and audit logs from Prisma Cloud CSPM into Microsoft Sentinel.

<a name="step2">

## Prerequisites
The below mentioned resources are required to connect Palo Alto Prisma Cloud CSPM with Sentinel.
- Access Key
- Secret Key
- Base URL

<a name="Access & Secret Key">

## Steps to get the Access Key & Secret Key from the PrismaCloudCSPM
- Log in to the Palo Alto Prisma Cloud CSPM console.
- Navigate to the Settings section.
- Click on Access Control from the left-hand menu.
- Click the Add button and Select Access Key.
- Enter a name of your choice for the access key.
- The Access Key and Secret Key will be generated.
- Copy and securely save both keys, as they will not be shown again.
- When connecting to Microsoft Sentinel, Please enter access Key and secret Key.

<a name="Base URL">

## Steps to get the Base URL
- When connecting to Microsoft Sentinel, make sure to enter the Base URL that corresponds to your region. Find the appropriate Base URL by visiting this page(https://pan.dev/prisma-cloud/api/cspm/api-urls/).