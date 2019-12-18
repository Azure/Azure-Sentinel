import { getPullRequestDiffFiles } from './utils';
import yaml from 'js-yaml';
import fs from 'fs';

export function IsValidYamlFile(filePath:string): Boolean {
    try {
        yaml.safeLoad(fs.readFileSync(filePath, 'utf8'));
        return true;
    }
    catch (e) {
        console.error(`Incorrect yaml file. Tile path: ${filePath}. Error message: ${e.message}`);
        return false
    }
}

const main = async () => {
    console.log("start  - yamlFileValidetor script");
    const pullRequestDiffFiles = await getPullRequestDiffFiles();
    const changedYamlFiles = pullRequestDiffFiles.filter(filePath => filePath.endsWith('.yaml') || filePath.endsWith('.yml'));

    if (changedYamlFiles.length === 0) {
        console.log("No changes in yaml file");
        return 0;
    }

    let retCode = 0;
    changedYamlFiles.forEach(filePath => {
        if(!IsValidYamlFile(filePath)){
            retCode = -1;
        }
    });

    return retCode;
}

main().then(retCode => {
    if (retCode !== 0) {
        console.error(`ERROR: incorrect yaml files`);
    }
    process.exit(retCode);
});