import { cli, devOps } from '@azure/avocado';
import * as logger from './logger';
import './stringExtenssions'

export async function GetDiffFiles(fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[]){
    const config = cli.defaultConfig();
    const pr = await devOps.createPullRequestProperties(config);
  
    if (pr === undefined) {
      console.log("undifined PR");
      return;
    }

    let changedFiles = await pr.diff();
    console.log(`${changedFiles.length} files changed in current PR`);

    const filterChangedFiles = changedFiles
      .filter((change) => change.kind !== 'Deleted')
      .map(change => change.path)
      .filter(filePath => fileTypeSuffixes === undefined|| filePath.endsWithAny(fileTypeSuffixes))
      .filter(filePath => filePathFolderPreffixes === undefined || filePath.startsWithAny(filePathFolderPreffixes));
    
    if (filterChangedFiles.length === 0) {
      logger.logWarning(`No changed files in current PR after filter. File type filter: ${fileTypeSuffixes ?  fileTypeSuffixes.toString() : null}, file path filter: ${filePathFolderPreffixes ?  filePathFolderPreffixes.toString() : null}`);
      return;
    }

    console.log(`${filterChangedFiles.length} files changed in current PR after filter`);
  
    return filterChangedFiles;
  }


