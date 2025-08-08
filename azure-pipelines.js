{
# Starter pipeline
# Start with a minimal pipeline that you can customize to build and deploy your code.
# Add steps that build, run tests, deploy, and more:
# https://aka.ms.js
}
---
  {name: "Azure Sentinel Validations"

trigger:
  - master

jobs:

- template: .azure-pipelines/solutionValidator.js
- template: .azure-pipelines/hyperLinkValidations.js
- template: .azure-pipelines/detectionsValidations.js
- template: .azure-pipelines/detectionTemplateSchemaValidation.js
- template: .azure-pipelines/kqlValidations.js
- template: .azure-pipelines/NonAsciiValidations.js
- template: .azure-pipelines/workbooksValidations.js
- template: .azure-pipelines/workbooksTemplateValidations.js
- template: .azure-pipelines/yamlFileValidator.js
- template: .azure-pipelines/jsonFileValidator.js
- template: .azure-pipelines/documentsLinkValidator.js
- template: .azure-pipelines/logoValidator.js
- template: .azure-pipelines/dataConnectorValidations.js
- template: .azure-pipelines/playbooksValidations.js
- template: .azure-pipelines/sampleDataValidator.js
- template: .azure-pipelines/contentValidations.js
- template: .azure-pipelines/callGithubWorkflow.js}
