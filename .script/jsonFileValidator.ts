import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import * as logger from "./utils/logger";

export async function IsValidJsonFile(filePath: string): Promise<ExitCode> {

  if (filePath.includes("mainTemplate.json")) {
    // FOR MAINTEMPLATE CONTAINING WORKBOOKS SERIALIZEDDATA
    let fileContent = fs.readFileSync(filePath, "utf8");
    
    if (fileContent.includes('serializedData')) {
      let mainTemplateJsonObj = JSON.parse(fileContent);

      mainTemplateJsonObj.filter((obj: { type: string; name: string | string[]; properties: { mainTemplate: { resources: any[]; }; }; }) => {
        if ((obj.type == "Microsoft.Resources/templateSpecs/versions" || obj.type == "Microsoft.OperationalInsights/workspaces/providers/contentTemplates") && obj.name.includes("workbook")) {
          obj.properties.mainTemplate.resources.filter((workbookObj: { type: string; properties: { serializedData: any; }; }) => {
            if (workbookObj.type == "Microsoft.Insights/workbooks") {
              JSON.parse(workbookObj.properties.serializedData);
            }
          });
        }
      });
    }

    return ExitCode.SUCCESS;
  } else {
    JSON.parse(fs.readFileSync(filePath, "utf8"));
    return ExitCode.SUCCESS;
  }
}

let fileTypeSuffixes = ["json"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidJsonFile(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Incorrect Json file. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);
