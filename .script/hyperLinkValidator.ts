import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import { GetPRDetails } from "./utils/gitWrapper";
import * as logger from "./utils/logger";

export async function ValidateHyperlinks(filePath: string): Promise<ExitCode> 
{
    let splitPath = filePath.split("/")
    if (splitPath[0] === "Solutions")
    {
        let dataFolderName = splitPath[2] === "Data" || splitPath[2] === "data" ? splitPath[2] : null
        let dataConnectorFolderName = splitPath[2] === "DataConnectors" || splitPath[2] === "Data Connectors" ? splitPath[2] : null
        let packageFolderName = splitPath[2] === "Package" ? splitPath[2] : null

        if (dataFolderName == null && dataConnectorFolderName == null && packageFolderName == null) 
        {
            console.log(`Skipping Hyperlink validation for file path : '${filePath}' as change is not in 'Data', 'Data Connectors' and/or 'Package' folder`)
            return ExitCode.SUCCESS;
        }

        const content = fs.readFileSync(filePath, "utf8");
        if (filePath.toLocaleLowerCase().includes("azuredeploy"))
        {
            // DATA CONNECTORS FOLDER WILL CONTAIN "azuredeploy" WHICH CONTAINS "WEBSITE_RUN_FROM_PACKAGE" ATTRIBUTE AND ITS VALUE/LINK SHOULD BE VALIDATED
            let jsonObj = JSON.parse(content);

            jsonObj.resources.filter((resourcesProp: { type: string; resources: any[]; }) => {
                if (resourcesProp.type == "Microsoft.Web/sites") {
                    resourcesProp.resources.filter(configProp => {
                        if (configProp.type == "config") {
                            console.log('inside of config');
                            if (configProp.properties.WEBSITE_RUN_FROM_PACKAGE == null)
                            {
                                throw new Error(`Data connector file '${filePath}' is missing attribute 'WEBSITE_RUN_FROM_PACKAGE'. Please add it with a valid hyperlink!`);
                            }
                            else
                            {
                                let websiteRunFromPackageUrl = configProp.properties.WEBSITE_RUN_FROM_PACKAGE;
                                const isShortLinkValid = isValidLink(websiteRunFromPackageUrl);
                                console.log(`websiteRunFromPackageUrl ${websiteRunFromPackageUrl}, isShortLinkValid ${isShortLinkValid}`);
                                if (!isShortLinkValid) {
                                    console.log('inside of false condition');
                                    throw new Error(`Data connector file '${filePath}' has broken hyperlink for attribute  'WEBSITE_RUN_FROM_PACKAGE'. Please review and rectify the hyperlink: ${websiteRunFromPackageUrl}`);
                                }
                            }
                        }
                    })
                }
            });

            console.log(`Skipping Hyperlink validation for file path : '${filePath}'`);
            return ExitCode.SUCCESS;
        }

        //IGNORE BELOW FILES
        let exclusionList = ["host.json", "proxies.json", "function.json", "azuredeploy", "system_generated_metadata.json", "parameters.json"]
        
        let fileName = splitPath[3].toString()
        if (exclusionList.filter(x=>x.includes(fileName)).length > 0)
        {
            console.log(`Skipping Hyperlink validation for file path as file is from exclusion list : '${filePath}'`)
            return ExitCode.SUCCESS;
        }

        const links = content.match(/(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])+/g);
        if (links) 
        {
            var invalidLinks = new Array();
            for (var link of links) 
            {
                link = link.replace(/["']/g, "")
                //check if the link is valid
                const isValid = await isValidLink(link);
                if (!isValid) 
                {
                    // CHECK IF LINK IS A GITHUB LINK
                    var isGithubLink = false;
                    if (link.includes('https://raw.githubusercontent.com') || link.includes('https://github.com'))
                    {
                        isGithubLink = true;
                    }

                    if (link.includes('&&sudo'))
                    {
                        //IGNORE HYPERLINKS WHICH HAS &&SUDO IN IT
                        isGithubLink = false;
                    }

                    if (isGithubLink)
                    {
                        const pr = await GetPRDetails();
                        if (typeof pr === "undefined") 
                        {
                            console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
                            return ExitCode.ERROR;
                        }

                        const changedFiles = await pr.diff();
                        const imageIndex = link.lastIndexOf('/');
                        const imageName = link.substring(imageIndex + 1);                        
                        const searchedFiles = changedFiles.map(change => change.path).filter(changedFilePath => changedFilePath.indexOf(imageName) > 0);
                        var searchedFilesLength = searchedFiles.length;
                        if (searchedFilesLength <= 0)
                        {
                            invalidLinks.push(link);
                        }
                        else
                        {
                            console.log(`Skipping Hyperlink validation for '${link}' in file path : '${filePath}'`);
                        }
                    }
                    else
                    {
                        invalidLinks.push(link);
                    }
                }
            }

            if (invalidLinks.length > 0)
            {
                var distinctInvalidLinks = invalidLinks.filter((n, i) => invalidLinks.indexOf(n) === i);
                var errorMessage= `File '${filePath}' has a total of '${distinctInvalidLinks.length}' broken hyperlinks. Please review and rectify the following hyperlinks: \n ${distinctInvalidLinks}`
                throw new Error(errorMessage.replace(",", "\n"));
            }
        }

        return ExitCode.SUCCESS
    }
    else
    {
        console.log(`Skipping Hyperlink validation for file path : '${filePath}' as change is not in 'Solutions' folder`)
        return ExitCode.SUCCESS
    }

  //create a function to check if the link is valid
    async function isValidLink(link: string): Promise<boolean> 
    {
        try 
        {
            //import XMLHttpRequest from "xmlhttprequest"
            const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
            const request = new XMLHttpRequest();
            request.open("GET", link, false);
            request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            request.timeout = 5000;
            request.ontimeout = function () { return false; }
            request.send();

            if (link == "https://aka.ms/sentinel-AliCloudAPI-functionapp1234") 
            {
                console.log(`Link: ${link}, Status ${request.status}`);
            }
            if (request.status == 404)
            {
                return false;
            }
            else if(request.status == 302)
            {
                var redirectResponse = request.getResponseHeader("Location")
                if (link == "https://aka.ms/sentinel-AliCloudAPI-functionapp1234") 
                {
                    console.log(`Link: ${link}, redirectResponse ${redirectResponse}`);
                }
                
                return (redirectResponse.includes("www.google.com") || redirectResponse.includes("www.bing.com") || redirectResponse.includes("404 - Page not found")) ? false : true;
            }
            else if (request.status == 0)
            {
                // TIMEOUT STATUS IS 0
                return false;
            }
            else 
            {
                var responseContent = request.responseText
                if (link == "https://aka.ms/sentinel-AliCloudAPI-functionapp1234")
                {
                    console.log(`Link: ${link}, responseContent ${responseContent}`);
                }
                if (responseContent != null && (responseContent.includes("404! Not Found!") || responseContent.includes("404 Not Found") || responseContent.includes("404 error") || responseContent.includes("404 - Page not found"))) {
                    return false;
                }
            }

            return true;
        } catch (error) 
        {
            console.log(error);
            return false;
        }
    }
}

let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors", "Data Connectors", "Solutions", "Package"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return ValidateHyperlinks(filePath)
    },
    onExecError: async (e: any) => {
        logger.logError(`${e}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);