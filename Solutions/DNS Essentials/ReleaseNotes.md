| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 								|
|-------------|--------------------------------|----------------------------------------------------------------------------------------------------|
| 3.0.5       | 02-09-2026                     | Added a DNS summarization playbook that uses the Azure Monitor Logs Ingestion API and creates two new V1 summary tables: DNS_Summarized_Logs_ipV1_CL and DNS_Summarized_Logs_sourceInfoV1_CL, avoiding conflicts with existing tables |
| 3.0.4		  | 02-07-2025					   | Updated new ThreatIntelIndicators table references using **parser**.								|
| 3.0.3       | 28-11-2024                     | Update **Analytic Rule** MultipleErrorsReportedForSameDNSQueryStaticThresholdBased.yaml to fix bug.|
| 3.0.2       | 29-07-2024                     | Update **Hunting Queries** to fix TTP.						        								|
| 3.0.1       | 31-01-2024                     | Updated the solution to fix **Analytic Rules** deployment issue.        							|
