import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import * as logger from "./utils/logger";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import { MainTemplateValidationError } from "./utils/validationError";

// initialize arrays to store valid domains and verticals
let validDomains: string[] = [];
let validVerticals: string[] = [];

// read the valid domains and verticals from the JSON file
try {
    const validDomainsVerticals = JSON.parse(fs.readFileSync('./.script/ValidDomainsVerticals.json', "utf8"));
    validDomains = validDomainsVerticals.validDomains;
    validVerticals = validDomainsVerticals.validVerticals;
} catch (error) {
    logger.logError(`Error reading ValidDomainsVerticals.json file: ${error}`);
}

// function to check if the solution is valid
export async function IsValidSolution(filePath: string): Promise<ExitCode> {

    // check if the file is a mainTemplate.json file
    if (filePath.endsWith("mainTemplate.json")) {
        // read the content of the file
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // check if the file has a "resources" field
        if (!jsonFile.hasOwnProperty("resources")) {
            console.warn(`No "resources" field found in the file. Skipping file path: ${filePath}`);
            return ExitCode.SUCCESS;
        }

        // get the resources from the file
        let resources = jsonFile.resources;

        // filter resources that have type "Microsoft.OperationalInsights/workspaces/providers/metadata"
        const filteredResource = resources.filter(function (resource: { type: string; }) {
            return resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata";
        });
        if (filteredResource.length > 0) {
            filteredResource.forEach((element: { hasOwnProperty: (arg0: string) => boolean; properties: { hasOwnProperty: (arg0: string) => boolean; categories: any; }; }) => {
                // check if the resource has a "properties" field
                if (element.hasOwnProperty("properties") === true) {
                    // check if the "properties" field has a "categories" field
                    if (element.properties.hasOwnProperty("categories") === true) {
                        const categories = element.properties.categories;

                        let invalidDomains = [];
                        let invalidVerticals = [];

                        // check if the categories have a "domains" field
                        if (categories.hasOwnProperty("domains")) {
                            let domains = categories.domains;
                            for (const domain of domains) {
                                // check if the domain is valid
                                if (!validDomains.includes(domain)) {
                                    invalidDomains.push(domain);
                                }
                            }
                        }

                        // check if the categories have a "verticals" field
                        if (categories.hasOwnProperty("verticals")) {
                            let verticals = categories.verticals;
                            for (const vertical of verticals) {
                                if (!validVerticals.includes(vertical)) {
                                    invalidVerticals.push(vertical);
                                }
                            }
                        }

                        if (invalidDomains.length > 0 || invalidVerticals.length > 0) {
                            let errorMessage = "Invalid";
                            if (invalidDomains.length > 0) {
                                errorMessage += ` domains: [${invalidDomains.join(", ")}]`;
                            }
                            if (invalidVerticals.length > 0) {
                                errorMessage += ` verticals: [${invalidVerticals.join(", ")}]`;
                            }
                            errorMessage += ` provided.`;
                            throw new MainTemplateValidationError(errorMessage);
                        }
                    }
                }
            });
        }

        // If the file is not identified as a main template, log a warning message
    } else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}





// Array to store file type suffixes for the check
let fileTypeSuffixes = ["json"];

// Array to store file path folder prefixes for the check
let filePathFolderPrefixes = ["Solutions"];

// Array to store file kinds for the check
let fileKinds = ["Added", "Modified"];

// Options object to pass to the runCheckOverChangedFiles function
let CheckOptions = {
    // Callback function to check if a file is valid
    onCheckFile: (filePath: string) => {
        return IsValidSolution(filePath);
    },
    // Callback function to handle errors during execution
    onExecError: async (e: any, filePath: string) => {
        console.log(`Solution Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    // Callback function to handle final failure
    onFinalFailed: async () => {
        logger.logError("Please refer link https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/sentinel/sentinel-solutions.md?msclkid=9a240b52b11411ec99ae6736bd089c4a#categories-for-microsoft-sentinel-out-of-the-box-content-and-solutions for valid Domains and Verticals.");
    },
};

// Function call to start the check process
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
