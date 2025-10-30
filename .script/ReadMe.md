# How to add new PR validation

At the time of submitting your Pull Request, automatic GitHub validations using Azure Pipelines is enabled on this repository for basic syntactical checks of the contributions. You can add custom tests as needed based on your scenario following this guidance.

## What is Azure Pipelines  

[Azure Pipelines](https://docs.microsoft.com/azure/devops/pipelines/get-started/what-is-azure-pipelines?view=azure-devops) is a cloud service that you can use to automatically build and test your code project and make it available to other users. It works with just about any language or project type.   


## How to add new PR validation:
1. Install the following extensions, if you use [VS Code](https://code.visualstudio.com/docs/azure/extensions) editor: 
   - [Azure Pipelines](https://marketplace.visualstudio.com/items?itemName=ms-azure-devops.azure-pipelines)
   - [Yaml](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

2. Run "npm install" cmd, in order to install the libraries used in this project.  
The libraries are defined in package.json

3. Create an Azure Pipeline job for the new validation.  
Add new yaml file under [.azure-pipelines](https://github.com/Azure/Azure-Sentinel/blob/master/.azure-pipelines/) folder, see example in [yamlFileValidator.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/.azure-pipelines/yamlFileValidator.yaml) file (note - the script code should be added on another file for clearer code, see in step #5). 
    * Add scripts those are relevant to the specific folder under one yaml file in the same job. The validation infrastructure and the examples are in TypeScript, but you can use other languages if you prefer
    * Azure Pipelines work with many languages such as Python, Java,JavaScript, PHP, Ruby, C#, C++, and Go. Refer to [Azure Pipelines documentation](https://docs.microsoft.com/azure/devops/pipelines/?view=azure-devops) for further information on this. 

4. Add the new job to [azure-pipelines.yml](https://github.com/Azure/Azure-Sentinel/blob/master/azure-pipelines.yml) file as a new template under jobs property

5. Create script file for the new validation. The job from step #3 has reference to this file. See instructions in [How to add script validation](#how-to-add-scipt-validation) section.  
   A step is a failure if it either explicitly reports failure (using a ##vso command) or ends the script with a non-zero exit code

6. Test the new validation. See instruction in [How to test the new validation](#How-to-test-the-new-validation) section

### How to add script validation

**Note**: All script logs are public and display in DevOps pipeline.  
By default, the logs color is white. In case you want another color you can use [logging commands](https://docs.microsoft.com/azure/devops/pipelines/scripts/logging-commands?view=azure-devops&tabs=bash)

1. Create script file under [.script](https://github.com/Azure/Azure-Sentinel/tree/master/.script) folder

2. In case you use TypeScript language, you can use the infrastructure script. See example in [yamlFileValidator.ts](https://github.com/Azure/Azure-Sentinel/blob/master/.script/yamlFileValidator.ts):
   - Create an async validation function that gets the file path.  
   In case the validation pass the function returns success, otherwise throws an exception (don't return an error, this will handle by the infrastructure).
   - Create CheckOptions object with 3 properties:  
     - onCheckFile: the validation validation function that will run on each file (from step one)  
     - onExecError: error behavior in case that the file validation failed  
     - onFinalFailed:  error behavior at the end of the validation, execute in case one of the validation failed
   - Call runCheckOverChangedFiles with properties:
     - checkOptions:  the object you create in the earlier step 2  
     - fileKinds: file kind filter, there are 3 kinds- "Added", "Modified", "Deleted"
     - fileTypeSuffixes : file type filter, example: ["yaml", "yml"]
     - filePathFolderPreffixes: folder path filter, example: ["Detections"]
   - Run prettier command to fix type script files format.  
     - install "npm install -g prettier" if needed
     - Run cmd: prettier --write --print-width 200 ".script/**/*.ts"

### How to test the new validation

1. In case the language script is TypeScript, check the new validation function by local tests. Since most of the code are the same, these tests will help you validate your changes before it gets merged to master.  
See example in [yamlFileValidatorTest](https://github.com/Azure/Azure-Sentinel/tree/master/.script/tests/yamlFileValidatorTest) folder.

   - Create new folder under [.script/test](https://github.com/Azure/Azure-Sentinel/tree/master/.script/tests). folder name format: TestedFileName+Test  
   - Create tests file. File name format: TestedFileName.test.ts  
   - Run the test by execute from  cmd "npm test".  
Since it is run locally you will see "Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue" message. You can ignore it.
   - In order to debug the test file, select "Mocha Current File" option in VSCode  

5. After the code is merged to master, create a Draft PR to test the new validation. Check both options, pass and failed.  
    * (Draft PR marked as "Work in Progress" and cannot be merged, more info [here](https://help.github.com/en/articles/about-pull-requests#draft-pull-requests)).  
    * Remember to delete the draft PR.  

