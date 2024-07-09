import { InvalidSolutionIDValidationError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

export function IsValidSolutionID(filePath: string): ExitCode {
    // Check if the file path ends with mainTemplate.json
    if (!filePath.endsWith("mainTemplate.json")) {
        return ExitCode.SUCCESS;
    }

    // Parse the JSON content from the file
    const jsonContent = JSON.parse(fs.readFileSync(filePath, "utf8"));

    // Get the 'variables' section from the JSON
    const variables = jsonContent.variables;

    // Check if 'solutionId' attribute is present
    if (variables && "solutionId" in variables) {
        const solutionId = variables.solutionId;

        // Validate if the solution ID is empty
        if (!solutionId) {
            throw new InvalidSolutionIDValidationError(`Empty solution ID. Expected format: publisherID.offerID. and it must be in lowercase. Found empty value.`);
        }

        // Validate the solution ID format
        const regex = /^[^.]+\.[^.]+$/;
        if (!regex.test(solutionId)) {
            throw new InvalidSolutionIDValidationError(`Invalid solution ID format. Expected format: publisherID.offerID. and it must be in lowercase. Found: ${solutionId}`);
        }

        // Validate the solution ID case (lowercase)
        if (solutionId !== solutionId.toLowerCase()) {
            throw new InvalidSolutionIDValidationError(`Invalid solution ID format. Expected format: publisherID.offerID. and it must be in lowercase. Found: ${solutionId}`);
        }
    } else {
        throw new InvalidSolutionIDValidationError(`Missing 'solutionId' attribute in the file. File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}
