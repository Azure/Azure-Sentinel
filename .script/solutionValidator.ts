import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import * as logger from "./utils/logger";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import { MainTemplateValidationError } from "./utils/validationError";

let validDomains: string[] = [];
let validVerticals: string[] = [];

try {
    const validDomainsVerticals = JSON.parse(fs.readFileSync('./.script/ValidDomainsVerticals.json', "utf8"));
    validDomains = validDomainsVerticals.validDomains;
    validVerticals = validDomainsVerticals.validVerticals;
} catch (error) {
    logger.logError(`Error reading ValidDomainsVerticals.json file: ${error}`);
}

export async function IsValidSolution(filePath: string): Promise<ExitCode> {


    if (filePath.endsWith("mainTemplate.json")) {
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        if (!jsonFile.hasOwnProperty("resources")) {
            console.warn(`No "resources" field found in the file. Skipping file path: ${filePath}`);
            return ExitCode.SUCCESS;
        }

        let resources = jsonFile.resources;

        const filteredResource = resources.filter(function (resource: { type: string; }) {
            return resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata";
        });
        if (filteredResource.length > 0) {
            filteredResource.forEach((element: { hasOwnProperty: (arg0: string) => boolean; properties: { hasOwnProperty: (arg0: string) => boolean; categories: any; }; }) => {
                if (element.hasOwnProperty("properties") === true) {
                    if (element.properties.hasOwnProperty("categories") === true) {
                        const categories = element.properties.categories;

                        if (categories.hasOwnProperty("domains")) {
                            let domains = categories.domains;
                            for (const domain of domains) {
                                if (!validDomains.includes(domain)) {
                                    throw new MainTemplateValidationError(`Invald Domain ${domain} provided`);
                                }
                            }
                        }

                        if (categories.hasOwnProperty("verticals")) {
                            let verticals = categories.verticals;
                            for (const vertical of verticals) {
                                if (!validVerticals.includes(vertical)) {
                                    throw new MainTemplateValidationError(`Invald Vertical ${vertical} provided`);
                                }
                            }
                        }
                    }
                }
            });
        }

    }
    else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    return ExitCode.SUCCESS;
}





let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["Solutions"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return IsValidSolution(filePath);
    },
    onExecError: async (e: any, filePath: string) => {
        console.log(`Main Template Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
