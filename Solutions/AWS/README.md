# ARM templates 
Author: Secugram 
# 1. Project name
Manage secure multi cloud environment with Sentinel

# 2. Elevator pitch
Our attempt to build an end-to-end security solution for Sentinel that is a perfect fit for a secure AWS and Azure multi cloud environment.

# 3. About the project
# Inspiration
Building and utilizing multi cloud environment nowadays is the best choice for most of organization and enterprise when they start their cloud journey. Therefore, in day-to-day work of a Microsoft Sentinel Consulting team, we are often challenged by clients about how to leverage Sentinel as a good-to-go solution for managing the security events in their multi cloud environment, especially AWS and Azure. So when we started this hackathon, we want to solve this problem completely but in a "cloud native" way.

When we looked up existing applications on Sentinel marketplace for connecting Sentinel to AWS environment and AWS security specific services (Security Hub, Inspector) we found that they have some limited

- Common integration is using API, causing many issues when running into high load production environment.
- S3 integration is new upgrade but it is still in preview and support a little of services: VPC Flow Logs, GuardDuty and CloudTrail.

All of these problems inspired us to building an end-to-end security solution to leverage Microsoft Sentinel as a core component for a secure multi cloud environment. We want to use Sentinel to collect security findings in some AWS security services by using S3 bucket for log integration that we call an AWS native approach.

# What it does

- A custom connector ingest security findings from AWS Macie (a DLP service), AWS Inspector (a Vulnerability Manager) and AWS Security Hub to Sentinel by pulling log from S3 buckets - a recommend way from AWS.
- Multiple custom workbook to aggregate and visualize data for AWS Macie and AWS Inspector.
- Custom analytic rules that detect Critical and High CVE on multiple EC2 Instances, EC2 Instance contains multiple High or Critical vulnerabilities, S3 Bucket contains sensitive information and allow public access and S3 Bucket has multiple High or Critical findings.
- The solution is packaged in Sentinel format for deploying automatically. 

# How we built it
- We use AWS Security Hub to ingest AWS Inspector findings and export it into S3 buck for ready integration. AWS Macie is already support S3 bucket export.
- Then we develop a Python custom connector to ingest log file from S3 buckets into Sentinel.
- We develop two separated Sentinel workbook to visualize the data we collect in previous steps.
- We develop four analytic rules to detect need-to-focus assets based on the findings from AWS Inspector and Macie such as Critical and High CVE on multiple EC2 Instances, EC2 Instance contains multiple High or Critical vulnerabilities, S3 Bucket contains sensitive information and allow public access and S3 Bucket has multiple High or Critical findings.
- We use Azure ARM and follow Sentinel build guide to build our solution into a ready to deploy software package.

# Challenges we ran into

- Timeframe: this hackathon is organized in a shorter time so we do not have much time to complete this hackathon. We started with many ideas such as AWS, GCP, but short time is really a challenge. So we must set the priority and pick the most important things and make it happen. Finally, we chose AWS with Inspector and Macie as a good fit in a AWS security landscape.

- Learning about AWS, especially Macie, Security Hub and Inspector for integration. Before starting this hackathon, our team is just strong about Azure and Microsoft Sentinel. AWS knowledge is limited. So, learning AWS in a short time, especially for integration is a tough challenge. 

- Handling with many Preview features from Sentinel. Sentinel is an active development cloud project and at the time to start this project we have many options to go. some is proven features, some is still feature preview. It made us very confuse. Finally, we made a safe decision to choose proven features from Sentinel to complete this hackathon although it could take us longer time with more development efforts.

# Accomplishments that we're proud of

- Solving the client question about using Sentinel to manage AWS security service in a multi cloud environment.
- Completing an end to end solution and ready to deploy.
- Our solution is a perfect fit into a Sentinel solution landscape of managing AWS cloud environment.

# What we learned

- How to use AWS security services like Inspector, Macie, Security Hub, Guard Duty.
- How to use S3 bucket pulling for AWS service integration

# What's next for 
One of the most important thing we want to do next after this hackathon is expanding our solution to support GCP like Cloud IDS, Security Command Center and then is for other cloud service providers. 
