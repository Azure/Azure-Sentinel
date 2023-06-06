import { MainTemplateSolutionVersionUpdateValidation } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";
import { GetPRDetails } from "../utils/gitWrapper";
import gitP, { SimpleGit } from 'simple-git/promise';


const workingDir: string = process.cwd();
const git: SimpleGit = gitP(workingDir);

export async function IsVersionUpdated(filePath: string): Promise<ExitCode> {
    if (!filePath.endsWith("mainTemplate.json")) {
        console.warn(`Could not identify JSON file as a main template. Skipping file path: ${filePath}`);
        return ExitCode.SUCCESS;
    }

    const pr = await GetPRDetails();

    if (typeof pr === "undefined") {
        console.log("Azure DevOps CI for a Pull Request wasn't found. If the issue persists, please open an issue.");
        return ExitCode.ERROR;
    }

    const options = [pr.targetBranch, pr.sourceBranch, filePath];
    const diffSummary = await git.diff(options);

    console.log(`Diff summary for file ${filePath}:\n${diffSummary}`);

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
            const previousVersion = mainMetadataResource.properties.version;

            const diffVersionMatch = diffSummary.match(/"version":\s*"(\d+\.\d+\.\d+)"/);
            const currentVersion = diffVersionMatch ? diffVersionMatch[1] : null;

            if (currentVersion && previousVersion && currentVersion !== previousVersion) {
                console.log(`Version number has been updated. Previous Version: ${previousVersion}, Current Version: ${currentVersion}`);
            } else if (currentVersion && !previousVersion) {
                console.log(`Version number could not be determined for the previous version. Current Version: ${currentVersion}`);
            } else if (currentVersion && previousVersion === currentVersion) {
                throw new MainTemplateSolutionVersionUpdateValidation(
                    `Solution version number is the same as the previous version. Version: ${currentVersion}`
                );
            }
        } else {
            throw new MainTemplateSolutionVersionUpdateValidation(
                `No main metadata resource with kind 'Solution' or version number found in the main template file: ${filePath}`
            );
        }
    } else {
        throw new MainTemplateSolutionVersionUpdateValidation(
            `No resources found in the main template file: ${filePath}`
        );
    }

    return ExitCode.SUCCESS;
}
