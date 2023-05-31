import { MainTemplateDomainVerticalValidationError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";
import { cli, devOps } from "@azure/avocado";
import "./stringExtensions";
import { PullRequestProperties } from '@azure/avocado/dist/dev-ops';

let pullRequestDetails: PullRequestProperties | undefined;

// Function to check if the version number has been updated
export function IsValidVersionNumber(filePath: string): ExitCode {
    if (filePath.endsWith("mainTemplate.json")) {
        const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        if (jsonFile.hasOwnProperty("resources") && Array.isArray(jsonFile.resources) && jsonFile.resources.length > 0) {
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
                const previousVersion = getPreviousVersion(filePath);

                if (previousVersion && currentVersion !== previousVersion) {
                    console.log(`Version number has been updated. Previous Version: ${previousVersion}, Current Version: ${currentVersion}`);
                } else if (!previousVersion) {
                    console.log(`Version number could not be determined for the previous version. Current Version: ${currentVersion}`);
                } else if (previousVersion === currentVersion) {
                    throw new MainTemplateDomainVerticalValidationError(`Solution version number is the same as the previous version. Version: ${currentVersion}`);
                }
            } else {
                throw new MainTemplateDomainVerticalValidationError(`No main metadata resource with kind 'Solution' or version number found in the main template file: ${filePath}`
                );
            }
        } else {
            throw new MainTemplateDomainVerticalValidationError(`No resources found in the main template file: ${filePath}`);
        }
    } else {
        console.warn(`Could not identify JSON file as a main template. Skipping file path: ${filePath}`);
    }
    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}

export async function GetPRDetails() {
    if (typeof pullRequestDetails == "undefined") {
        console.log("Getting PR details");
        const config = cli.defaultConfig();
        pullRequestDetails = await devOps.createPullRequestProperties(config);
    }
    return pullRequestDetails;
}

// New method to get the previous version from git history
export async function getPreviousVersion(filePath: string): Promise<string | undefined> {
    const pr = await GetPRDetails();

    if (typeof pr === "undefined") {
        console.log("Azure DevOps CI for a Pull Request wasn't found. If the issue persists, please open an issue");
        return;
    }

    const commitId = await pr.mergeBase();

    const diffOptions = {
        file: filePath,
        commit: commitId,
        maxCount: 1,
        format: '%H%n%cd%n'
    };

    const gitDiff = await pr.gitDiff(diffOptions);

    if (gitDiff.length > 0) {
        const previousCommitId = gitDiff[0].split('\n')[0];
        const commitDetails = await pr.getCommitDetails(previousCommitId);

        // Find the specific block with "kind: Solution"
        const blockRegex = /"type":\s*"Microsoft\.OperationalInsights\/workspaces\/providers\/metadata"[^}]*"kind":\s*"Solution"[^}]*"properties":\s*{[^}]*"version":\s*"(.*?)"/g;
        let match;
        let previousVersion;

        // Iterate through each matching block and capture the version number
        while ((match = blockRegex.exec(commitDetails)) !== null) {
            if (match.length > 1) {
                previousVersion = match[1];
            }
        }

        if (previousVersion) {
            return previousVersion;
        }
    }

    return undefined;
}
