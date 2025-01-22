import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { ExitCode } from "./utils/exitCode.js";
import * as logger from "./utils/logger.js";
import { isValidLogoImage } from "./utils/LogoChecker/logoImageChecker.js";
import { isValidLogoImageSVGContent } from "./utils/LogoChecker/logoImageSVGChecker.js";

export async function IsValidLogo(FileName: string): Promise<ExitCode> {
  if(FileName.includes("Logos") || FileName.includes("Data Connectors/Logo") 
    || FileName.includes("Workbooks/Images/Logo")
    || FileName.includes("Workbooks/Images/Logos"))
  {
    isValidLogoImage(FileName);
      const svgContent: string = fs.readFileSync(FileName, { encoding: "utf8", flag: "r" });
      if(svgContent != "undefined")
      {
        isValidLogoImageSVGContent(svgContent)
      }
  }
  
  return ExitCode.SUCCESS;
  }
 
let fileTypeSuffixes;
let filePathFolderPrefixes = ["Logos","Solutions", "Workbooks/Images/Logos"];
let fileKinds = ["Added","Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidLogo(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Logo Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};
runCheckOverChangedFiles(CheckOptions, fileKinds,fileTypeSuffixes,  filePathFolderPrefixes);