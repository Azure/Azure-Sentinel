# Unified Connectors: AWS and GCP onboarding

These templates and scripts configure customer-owned cloud resources for AWS S3
and GCP Pub/Sub Unified Connectors in the
[Microsoft Defender portal](https://security.microsoft.com/data-management?tabName=Connectors&connectorSource=unified).
They do not deploy a Microsoft Sentinel CCF connector or create a Defender
connector instance.

| Cloud | Setup instructions | Assets |
| --- | --- | --- |
| AWS | [AWS onboarding](AWS/README.md) | Four CloudFormation templates for new or existing log-source resources, with or without a new OIDC provider |
| GCP | [GCP onboarding](GCP/README.md) | Bash scripts for new or existing Pub/Sub and logging resources |

## Prerequisites

- Access to the intended Unified Connector in your Microsoft Entra tenant.
- An authorized cloud provisioning identity in the target account or project.
  Provisioning permissions differ from the connector's collection permissions.
- The cloud-specific prerequisites and IAM changes described in the linked guide.

These versions support commercial-cloud federation settings and AWS `arn:aws`
resources. No secrets or service-account keys are required as inputs. Cloud
resources and log collection can incur charges.

## Configuration steps

1. Follow the [AWS](AWS/README.md) or [GCP](GCP/README.md) guide to select and
   download the appropriate setup asset.
2. Review its IAM changes and provision the required cloud resources.
3. Use the resulting identifiers in the Defender portal under **Setup &
   configuration > Data & connectors > Connectors > Unified connectors**.
4. Check connector health, then verify recent data for the intended source.
   Successful provisioning or an `OK` status alone does not verify ingestion.
