import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    const ignoreFiles = ["azure-pipelines", "azureDeploy", "host.json", "proxies.json", "azuredeploy", "function.json"]
    const dataFolder = ["/Data/", "/data/"]
    const dataConnectorsFolder = ["/DataConnectors/", "/Data Connectors/"]
    let requiredFolderFiles = [...dataFolder, ...dataConnectorsFolder, "createUiDefinition.json"];

    const hasIgnoredFile = ignoreFiles.filter(item => { return filePath.includes(item)}).length > 0
    const hasRequiredFolderFiles = requiredFolderFiles.filter(item => { return filePath.includes(item)}).length > 0

    if (!hasIgnoredFile && hasRequiredFolderFiles)
    {
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";
        let tagContent = "";
        let tagName = ""

        const hasDataFolder = dataFolder.filter(item => { return filePath.includes(item)}).length > 0
        const hasDataConnectorFolder = dataConnectorsFolder.filter(item => { return filePath.includes(item)}).length > 0

        const jsonTagObj = JSON.parse(fs.readFileSync('./.script/validate-tag.json', "utf8"));
        if (jsonTagObj.hasOwnProperty("createUiDefinition") && filePath.includes('createUiDefinition'))
        {
            tagName = jsonTagObj.createUiDefinition;
            tagContent = GetTagContent(tagName);
        }
        else if (hasDataFolder && jsonTagObj.hasOwnProperty("data"))
        {
            tagName = jsonTagObj.data;
            tagContent = GetTagContent(tagName);
        }
        else if (hasDataConnectorFolder && jsonTagObj.hasOwnProperty("dataConnectors"))
        {
            tagName = jsonTagObj.dataConnectors;
            tagContent = GetTagContent(tagName);
        }

        if (tagContent)
        {
            let hasAzureSentinelText = tagContent.toLowerCase().includes(searchText.toLowerCase());
            if (hasAzureSentinelText) {
                throw new Error(`Please update text from '${searchText}' to '${expectedText}' in '${tagName}' tag in the file '${filePath}'`);
            }
        }
        else
        {
            console.log(`Skipping file ${filePath} from Content Validation as ${searchText} text not found`);
        }
    }
    else
    {
        console.log(`Skipping file ${filePath} from Content Validation as the file is not from folder Data, Data Connector or createUiDefinition file`);
    }

    return ExitCode.SUCCESS;

    function GetTagContent(tagName: any) {
        var fileContentObj = JSON.parse(fs.readFileSync(filePath, "utf8"));

        if (filePath.includes("createUiDefinition.json")) {
            var tagContent = fileContentObj["parameters"]["config"]["basics"][tagName];
            if (tagContent == undefined) {
                //MAKE FIRST LETTER OF THE WORD CAPS
                const firstLetterCapsInTagName = tagName.charAt(0).toUpperCase() + tagName.slice(1)
                var tagContent = fileContentObj["parameters"]["config"]["basics"][firstLetterCapsInTagName];
            }
        }
        else {
            var tagContent = fileContentObj[tagName];
            if (tagContent == undefined) {
                //MAKE FIRST LETTER OF THE WORD CAPS
                const firstLetterCapsInTagName = tagName.charAt(0).toUpperCase() + tagName.slice(1)
                var tagContent = fileContentObj[firstLetterCapsInTagName];
            }
        }
        return tagContent;
    }
}

let fileTypeSuffixes = ["json"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return ValidateFileContent(filePath)
    },
    onExecError: async (e: any) => {
        logger.logError(`Content Validation check Failed: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);