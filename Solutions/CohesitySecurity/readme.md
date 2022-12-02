# Cohesity SIEM/SOAR Integration with Sentinel

This code integrates Cohesity Helios Cloud solution with MS Sentinel

### Build Instructions
1. Follow Tools/Create-Azure-Sentinel-Solution/V2/README.md:7 to setup build prerequisites
2. Edit cohesity.config to replace these values with your owm
* your_email_for_playbook@your_domain.com
* your_support_email@your_domain.com
* 11111111-2222-3333-4444-555555555555
3. Run build.sh from anywhere
4. Follow Tools/Create-Azure-Sentinel-Solution/V2/README.md:273 to do post-build manually validation

## Prerequisites for deploying Custom Connector
1. API key. To get API Key, login into your Helios cloud instance dashboard and navigate to Settings --> Access Management -> API Keys --> Add API key.

## Deployment instructions
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)
