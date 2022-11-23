import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";




export async function ValidateHyperlinks(filePath: string): Promise<ExitCode> {

  const content = fs.readFileSync(filePath, "utf8");

  //get http or https links from the content
  //const links = content.match(/https?:\/\/[^\s]+/g);
  const links = content.match(/(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])+/g);
  if (links) {
    console.log(links)
    var invalidLinks = new Array();
    for (var link of links) {
      link = link.replace(/["']/g, "")

      //check if the link is valid
      const isValid = await isValidLink(link);
      if (!isValid) {
        //logger.logError(`Invalid link: ${link}`);
        //throw new Error();
        invalidLinks.push(link)
      }
    }

    console.log(`Total Invalid Links: ${invalidLinks.length}`)
    if (invalidLinks.length > 0) {
      console.log(`Below are the invalid links:`)
      invalidLinks.forEach(l => {
        logger.logError(`\n ${l}`);
      });
      
      throw new Error();
    }
  }

  //create a function to check if the link is valid
  async function isValidLink(link: string): Promise<boolean> {
    try {
      //import XMLHttpRequest from "xmlhttprequest"
      //console.log("link to valid is ", link)
      const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
      const request = new XMLHttpRequest();
      request.open("GET", link, false);
      request.send();

      if (request.status == 404) {
        return false;
      }
      else {
        var responseContent = request.responseText
        if (responseContent != null && (responseContent.includes("404! Not Found!") || responseContent.includes("404 Not Found") || responseContent.includes("404 error"))) {
          return false;
        }
      }

      return true;
    } catch (error) {
      console.log(error);
      return false;
    }
  }    
  return ExitCode.SUCCESS;
}



let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors","Solutions", "Data Connectors"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    console.log(`File path is ${filePath}`)
    return ValidateHyperlinks(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`HyperLink Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);