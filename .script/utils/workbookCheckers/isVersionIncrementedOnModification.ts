import { GetDiffFiles, GetPRDetails } from "../gitHubWrapper.js";
import { WorkbookMetadata } from "../workbookMetadata.js";
import gitP, { SimpleGit } from 'simple-git';
import { WorkbookValidationError } from "../validationError.js";
import { ExitCode } from "../exitCode.js";

const workingDir:string = process.cwd();
const git: SimpleGit = gitP(workingDir);

const fileTypeSuffixes = [".json"];
const filePathFolderPrefixes = ["Workbooks"];
const fileKinds = ["Modified"];

const workbooksDirectoryPath = "Workbooks";
const workbooksMetadataPath = `${workbooksDirectoryPath}/WorkbooksMetadata.json`;

// Checks that the version of a workbook template is incremented if modified
export async function isVersionIncrementedOnModification(items: Array<WorkbookMetadata>) {
  const pr = await GetPRDetails();

  if(pr){ // pr may return undefined
      const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
    if(changedFiles && changedFiles.length > 0){

      // Fetch the base and head branches before running the diff
      const branches = await git.branch();
      if (!branches.all.includes(pr.base.ref)) {
          try {
              await git.fetch(['--no-tags', '--prune', '--no-recurse-submodules', '--depth=1', pr.base.repo.clone_url, pr.base.ref + ':' + pr.base.ref]);
          } catch (e) {
              console.error(`Error fetching branch ${pr.base.ref} from git:`, e);
              return ExitCode.ERROR;
          }
      }
      if (!branches.all.includes(pr.head.ref)) {
          try {
                  await git.fetch(['--no-tags', '--prune', '--no-recurse-submodules', '--depth=1', pr.head.repo.clone_url , pr.head.ref + ':' + pr.head.ref]);
          } catch (e) {
              console.error(`Error fetching branch ${pr.head.ref} from git:`, e);
              return ExitCode.ERROR;
          }
      }

      const baseMetadata = JSON.parse(await git.show([`${pr.base.ref}:${workbooksMetadataPath}`])) as WorkbookMetadata[];
      const headMetadata = JSON.parse(await git.show([`${pr.head.ref}:${workbooksMetadataPath}`])) as WorkbookMetadata[];
      const versionChanges = getVersionChangesByWorkbook(baseMetadata, headMetadata);

      items
      .filter((workbookMetadata: WorkbookMetadata) => changedFiles.includes(`${workbooksDirectoryPath}/${workbookMetadata.templateRelativePath}`))
      .forEach((workbookMetadata: WorkbookMetadata) => {
          const templateRelativePath = workbookMetadata.templateRelativePath;
          if (versionChanges[templateRelativePath] == null) {
          // If the workbook has changed but the version was not updated (a matching key was not found in the versionChanges dictionary) - throw error
          throw new WorkbookValidationError(`The workbook ${workbookMetadata.templateRelativePath} has been modified but the version has not been incremented in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
        }
        else {
          const isNewVersionGreaterThanOldVersion = versionChanges[templateRelativePath]["newVersion"] > versionChanges[templateRelativePath]["oldVersion"];

          if(!isNewVersionGreaterThanOldVersion){ // If the version was updated but the new version is not greater than old version - throw error
            throw new WorkbookValidationError(`The new updated version (${versionChanges[templateRelativePath]["newVersion"]}) must be greater than the old version (${versionChanges[templateRelativePath]["oldVersion"]}) for workbook ${workbookMetadata.templateRelativePath} in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
          }
        }
      });
    }
  }
  return ExitCode.SUCCESS;
}


export function getVersionChangesByWorkbook(
  baseItems: Array<Pick<WorkbookMetadata, "templateRelativePath" | "version">>,
  headItems: Array<Pick<WorkbookMetadata, "templateRelativePath" | "version">>
) {
  const baseVersions = new Map(baseItems.map(({ templateRelativePath, version }) => [templateRelativePath, version]));
  const versionChanges: Record<string, { newVersion: string; oldVersion: string }> = {};

  for (const { templateRelativePath, version: newVersion } of headItems) {
    const oldVersion = baseVersions.get(templateRelativePath);
    if (oldVersion !== undefined && oldVersion !== newVersion) {
      versionChanges[templateRelativePath] = { newVersion, oldVersion };
    }
  }

  return versionChanges;
}



