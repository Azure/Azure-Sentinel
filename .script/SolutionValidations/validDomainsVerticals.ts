import { MainTemplateDomainVerticalValidationError } from "./../utils/validationError";
import * as logger from "./../utils/logger";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

// initialize arrays to store valid domains and verticals
let validDomains: string[] = [];
let validVerticals: string[] = [];

// read the valid domains and verticals from the JSON file
try {
    const validDomainsVerticals = JSON.parse(fs.readFileSync('./.script/SolutionValidations/ValidDomainsVerticals.json', "utf8"));
    validDomains = validDomainsVerticals.validDomains;
    validVerticals = validDomainsVerticals.validVerticals;
} catch (error) {
    logger.logError(`Error reading ValidDomainsVerticals.json file: ${error}`);
}

// function to check if the solution is valid
export function IsValidSolutionDomainsVerticals(filePath: string): ExitCode {

    // check if the file is a mainTemplate.json file
    if (filePath.endsWith("mainTemplate.json")) {
        // read the content of the file
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // check if the file has a "resources" field
        if (!jsonFile.hasOwnProperty("resources")) {
            throw new MainTemplateDomainVerticalValidationError(`No "resources" field found in the file. File path: ${filePath}`);
        }

        // get the resources from the file
        let resources = jsonFile.resources;

        // filter resources that have type "Microsoft.OperationalInsights/workspaces/providers/metadata"
        const filteredResource = resources.filter(function (resource: { type: string }) {
            return resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata" ||
                resource.type === "Microsoft.OperationalInsights/workspaces/providers/contentPackages";
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
                            if (domains.length === 0) {
                                throw new MainTemplateDomainVerticalValidationError("The solution must include at least one valid domain. Please provide a domain in the 'domains' field of the 'categories' object.");
                            }
                            for (const domain of domains) {
                                // check if the domain is valid
                                if (!validDomains.includes(domain)) {
                                    invalidDomains.push(domain);
                                }
                            }
                        }
                        else {
                            throw new MainTemplateDomainVerticalValidationError("The solution must include at least one valid domain. Please provide a domain in the 'domains' field of the 'categories' object.");
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
                            throw new MainTemplateDomainVerticalValidationError(errorMessage);
                        }
                    }
                }
            });
        }
        else {
            throw new MainTemplateDomainVerticalValidationError(`There are no metadata resoruces found in the file. File path: ${filePath}`);
        }

        // If the file is not identified as a main template, log a warning message
    } else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}

