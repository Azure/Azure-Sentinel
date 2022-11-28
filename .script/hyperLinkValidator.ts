import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateHyperlinks(filePath: string): Promise<ExitCode> 
{
  let splitPath = filePath.split("/")
  if (splitPath[0] === "Solutions")
  {
    let dataFolderName = splitPath[2] === "Data" || splitPath[2] === "data" ? splitPath[2] : null
    let dataConnectorFolderName = splitPath[2] === "DataConnectors" || splitPath[2] === "Data Connectors" ? splitPath[2] : null
    if (dataFolderName == null && dataConnectorFolderName == null) 
    {
      console.log(`Skipping Hyperlink validation for file path : '${filePath}' as change is not in 'Data' and/or 'Data Connectors' folder`)
      return ExitCode.SUCCESS;
    }
    
    const content = fs.readFileSync(filePath, "utf8");
  
    //get http or https links from the content
    //const links = content.match(/https?:\/\/[^\s]+/g);
    const links = content.match(/(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])+/g);
    if (links) 
    {
      //console.log(`List of all Links in given File ${filePath} are:`)
      //console.log(links)
      var invalidLinks = new Array();
      for (var link of links) 
      {
        link = link.replace(/["']/g, "")

        //check if the link is valid
        const isValid = await isValidLink(link);
        if (!isValid) {
          invalidLinks.push(link)
        }
      }

      if (invalidLinks.length > 0)
      {
        console.log(`File: '${link}' has Total Invalid Links: ${invalidLinks.length}`)
        console.log(`Below are the invalid links:`)
        invalidLinks.forEach(l => {
          logger.logError(`\n ${l}`);
        });

        throw new Error(`Total Invalid Links Count '${invalidLinks.length}'. Invalid Links in given file path '${filePath}' are as below: \n ${invalidLinks}`);
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
  async function isValidLink(link: string): Promise<boolean> {
    try {
      //import XMLHttpRequest from "xmlhttprequest"
      const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
      const request = new XMLHttpRequest();
      request.open("GET", link, false);
      request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
      request.timeout = 5000;
      request.ontimeout = function () { return false; }
      request.send();

      if (request.status == 404)
      {
        return false;
      }
      else if(request.status == 302)
      {
        var redirectResponse = request.getResponseHeader("Location")
        // if (redirectResponse.includes("www.google.com") || redirectResponse.includes("www.bing.com"))
        // {
        //   logger.logWarning(`Warning: Given link '${link}' seems to be searching in www.Google.com or www.Bing.com and possibly an invalid link.`)
        // }
        // return true;
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

        if (responseContent != null && (responseContent.includes("404! Not Found!") || responseContent.includes("404 Not Found") || responseContent.includes("404 error") || responseContent.includes("404 - Page not found"))) {
          return false;
        }
      }

      return true;
    } catch (error) {
      console.log(error);
      return false;
    }
  }
}

let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors", "Data Connectors", "Solutions"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return ValidateHyperlinks(filePath)
  },
  onExecError: async () => {
    logger.logError(`HyperLink Validation Failed.`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);