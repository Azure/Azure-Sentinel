import { InvalidFileContentError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

type AttributeConfig = {
    mainTemplateAttributes: string[];
    createUIDefinitionAttributes: string[];
};

const attributeConfig: AttributeConfig = {
    mainTemplateAttributes: ["descriptionMarkdown", "description"],
    createUIDefinitionAttributes: ["text", "description"],
};

export function IsValidBrandingContent(filePath: string): ExitCode {
    // Skip validation if file path contains "SentinelOne"
    if (filePath.includes("SentinelOne")) {
        return ExitCode.SUCCESS;
    }

    const errors: string[] = [];

    // check if the file is mainTemplate.json or createUiDefinition.json
    if (filePath.endsWith("mainTemplate.json")) {
        validateFileContent(filePath, attributeConfig.mainTemplateAttributes, errors);
    } else if (filePath.endsWith("createUiDefinition.json")) {
        validateFileContent(filePath, attributeConfig.createUIDefinitionAttributes, errors);
    } else {
        console.warn(`Could not identify JSON file as mainTemplate.json or createUiDefinition.json. Skipping. File path: ${filePath}`);
    }

    // Throw a single error with all the error messages concatenated
    if (errors.length > 0) {
        throw new InvalidFileContentError(errors.join("\n"));
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}

function validateFileContent(filePath: string, attributeNames: string[], errors: string[]): void {
    const fileContent = fs.readFileSync(filePath, "utf8");
    const jsonContent = JSON.parse(fileContent);

    traverseAttributes(jsonContent, attributeNames, errors);
}

function traverseAttributes(jsonContent: any, attributeNames: string[], errors: string[]): void {
    for (const key in jsonContent) {
        if (jsonContent.hasOwnProperty(key)) {
            const attributeValue = jsonContent[key];
            if (attributeNames.includes(key) && typeof attributeValue === "string") {
                validateAttribute(attributeValue, key, errors);
            }
            if (typeof attributeValue === "object" && attributeValue !== null) {
                traverseAttributes(attributeValue, attributeNames, errors);
            }
        }
    }
}

function validateAttribute(attributeValue: string, attributeName: string, errors: string[]): void {
    const sentinelRegex = /(?<!Microsoft\s)(?<!\S)Sentinel(?!\S)/g;
    const updatedValue = attributeValue.replace(sentinelRegex, "Microsoft Sentinel");

    if (attributeValue !== updatedValue) {
        const error = `Inaccurate product branding used in '${attributeName}' for '${attributeValue}'. Use "Microsoft Sentinel" instead of "Sentinel"`;
        errors.push(error);
    }
}
