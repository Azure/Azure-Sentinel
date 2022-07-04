# RecordedFuture - Identity Logic Apps 
# Overview

Recorded Future is the world’s largest provider of intelligence for enterprise security. By combining persistent and pervasive automated data collection and analytics with human analysis, Recorded Future delivers intelligence that is timely, accurate, and actionable.

# Deployment

> **Due to internal Microsoft Logic Apps dependencies, please deploy first the ImportToSentinel playbook before any of the IndicatorProcessor one.**

## ImportToSentinel

This playbooks will serve via the Microsoft Batching mechanism all of the IndicatorProcessor playbooks, for optimizition of the indicator deployment process.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%2FPlaybooks%2FRecordedFuture-ImportToSentinel.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%2FPlaybooks%2FRecordedFuture-ImportToSentinel.json)
