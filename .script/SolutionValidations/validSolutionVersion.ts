import { MainTemplateDomainVerticalValidationError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";
import axios from "axios";

// Function to get the previous version from the catalog API
async function getPreviousVersion(offerId: string): Promise<string | null> {
    const url = `https://catalogapi.azure.com/offers?api-version=2018-08-01-beta&$filter=(categoryIds/any(cat:+cat+eq+%27AzureSentinelSolution%27)+or+keywords/any(key:+contains(key,%27f1de974b-f438-4719-b423-8bf704ba2aef%27)))+and+(offerId+eq+%27${offerId}%27)`;
    try {
        const response = await axios.get(url);
        const artifacts = response.data?.artifacts;
        const defaultTemplate = artifacts.find(
            (artifact: any) => artifact.name === "DefaultTemplate"
        );
        if (defaultTemplate) {
            const mainTemplateResponse = await axios.get(defaultTemplate.uri);
            const mainTemplate = mainTemplateResponse.data;
            const previousVersion = mainTemplate.properties?.version;
            return previousVersion || null;
        }
    } catch (error) {
        console.error("Failed to retrieve the previous version from the catalog API:", error);
    }
    return null;
}

// Function to check if the version number has been updated
export async function IsValidVersionNumber(filePath: string): Promise<ExitCode> {
    if (filePath.endsWith("mainTemplate.json")) {
        const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        if (
            jsonFile.hasOwnProperty("resources") &&
            Array.isArray(jsonFile.resources) &&
            jsonFile.resources.length > 0
        ) {
            const mainMetadataResource = jsonFile.resources.find((resource: any) => {
                return (
                    resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata" &&
                    resource.hasOwnProperty("properties") &&
                    resource.properties.hasOwnProperty("version") &&
                    resource.properties.hasOwnProperty("kind") &&
                    resource.properties.kind === "Solution"
                );
            });

            if (mainMetadataResource) {
                const currentVersion = mainMetadataResource.properties.version;
                const offerIdMatch = filePath.match(/azuresentinel\.([\w-]+)/);
                if (offerIdMatch) {
                    const offerId = offerIdMatch[1];
                    const previousVersion = await getPreviousVersion(offerId);
                    if (previousVersion && currentVersion !== previousVersion) {
                        console.log(
                            `Version number has been updated. Previous Version: ${previousVersion}, Current Version: ${currentVersion}`
                        );
                    } else if (!previousVersion) {
                        console.log(
                            `Version number could not be determined for the previous version. Current Version: ${currentVersion}`
                        );
                    } else if (previousVersion === currentVersion) {
                        throw new MainTemplateDomainVerticalValidationError(
                            `Solution version number is the same as the previous version. Version: ${currentVersion}`
                        );
                    }
                } else {
                    console.warn(`Could not extract offerId from the mainTemplate file path: ${filePath}`);
                }
            } else {
                throw new MainTemplateDomainVerticalValidationError(
                    `No main metadata resource with kind 'Solution' or version number found in the main template file: ${filePath}`
                );
            }
        } else {
            throw new MainTemplateDomainVerticalValidationError(
                `No resources found in the main template file: ${filePath}`
            );
        }
    } else {
        console.warn(`Could not identify JSON file as a main template. Skipping file path: ${filePath}`);
    }
    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}
