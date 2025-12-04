import { GetDiffFiles, GetPRDetails } from "../gitHubWrapper.js";
import gitP from 'simple-git';
import { WorkbookValidationError } from "../validationError.js";
const workingDir = process.cwd();
const git = gitP(workingDir);
const fileTypeSuffixes = [".json"];
const filePathFolderPrefixes = ["Workbooks"];
const fileKinds = ["Modified"];
const workbooksDirectoryPath = "Workbooks";
const gitDiffFileFullContentOption = "-W"; // -W option to get the full file content
// Checks that the version of a workbook template is incremented if modified
export async function isVersionIncrementedOnModification(items) {
    const pr = await GetPRDetails();
    if (pr) { // pr may return undefined
        const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
        if (changedFiles && changedFiles.length > 0) {
            // Fetch the base and head branches before running the diff
            const branches = await git.branch();
            if (!branches.all.includes(pr.base.ref)) {
                try {
                    await git.fetch(['--no-tags', '--prune', '--no-recurse-submodules', '--depth=1', pr.base.repo.clone_url, pr.base.ref + ':' + pr.base.ref]);
                }
                catch (e) {
                    console.error(`Error fetching branch ${pr.base.ref} from git:`, e);
                    return -1 /* ExitCode.ERROR */;
                }
            }
            if (!branches.all.includes(pr.head.ref)) {
                try {
                    await git.fetch(['--no-tags', '--prune', '--no-recurse-submodules', '--depth=1', pr.head.repo.clone_url, pr.head.ref + ':' + pr.head.ref]);
                }
                catch (e) {
                    console.error(`Error fetching branch ${pr.head.ref} from git:`, e);
                    return -1 /* ExitCode.ERROR */;
                }
            }
            const options = [pr.base.ref, pr.head.ref, gitDiffFileFullContentOption, `${workbooksDirectoryPath}/WorkbooksMetadata.json`];
            const diffSummary = await git.diff(options);
            const diffLinesArray = diffSummary.split('\n').map((l) => l.trim());
            const versionChanges = extractVersionChangesByWorkbook(diffLinesArray);
            items
                .filter((workbookMetadata) => changedFiles.includes(`${workbooksDirectoryPath}/${workbookMetadata.templateRelativePath}`))
                .forEach((workbookMetadata) => {
                const templateRelativePath = workbookMetadata.templateRelativePath;
                if (versionChanges[templateRelativePath] == null) {
                    // If the workbook has changed but the version was not updated (a matching key was not found in the versionChanges dictionary) - throw error
                    throw new WorkbookValidationError(`The workbook ${workbookMetadata.templateRelativePath} has been modified but the version has not been incremented in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
                }
                else {
                    const isNewVersionGreaterThanOldVersion = versionChanges[templateRelativePath]["newVersion"] > versionChanges[templateRelativePath]["oldVersion"];
                    if (!isNewVersionGreaterThanOldVersion) { // If the version was updated but the new version is not greater than old version - throw error
                        throw new WorkbookValidationError(`The new updated version (${versionChanges[templateRelativePath]["newVersion"]}) must be greater than the old version (${versionChanges[templateRelativePath]["oldVersion"]}) for workbook ${workbookMetadata.templateRelativePath} in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
                    }
                }
            });
        }
    }
    return 0 /* ExitCode.SUCCESS */;
}
function extractVersionChangesByWorkbook(diffLines) {
    let currentLine = 0;
    const workbookVersionChanges = {};
    const replaceQuotesRegex = /\"/gi;
    while (currentLine < diffLines.length && diffLines[currentLine] !== '[') {
        currentLine++; // Skip to beginning of Workbooks array
    }
    while (currentLine < diffLines.length && diffLines[currentLine] !== ']') {
        if (diffLines[currentLine] === '{') {
            let templateRelativePath = null;
            let newVersion = null;
            let oldVersion = null;
            currentLine++; // Beginning of a workbook metadata object
            while (currentLine < diffLines.length && diffLines[currentLine] !== '}') {
                const line = diffLines[currentLine];
                if (line.trim().startsWith('"templateRelativePath":')) {
                    templateRelativePath = line.split(':')[1].trim().replace(replaceQuotesRegex, "").replace(',', "");
                }
                if ((line.trim().startsWith('+') || line.trim().startsWith('-')) && line.includes('"version":')) {
                    const version = line.split(':')[1].trim().replace(replaceQuotesRegex, "").replace(',', "");
                    if (line.trim().startsWith('+')) {
                        newVersion = version;
                    }
                    else {
                        oldVersion = version;
                    }
                }
                currentLine++;
            }
            if (templateRelativePath && newVersion && oldVersion) {
                workbookVersionChanges[templateRelativePath] = { "newVersion": newVersion, "oldVersion": oldVersion };
            }
        }
        currentLine++;
    }
    return workbookVersionChanges;
}
//# sourceMappingURL=isVersionIncrementedOnModification.js.map