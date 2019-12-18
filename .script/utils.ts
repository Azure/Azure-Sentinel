
import { devOps, cli } from '@azure/avocado'; //TODO: use different way to get PR diff files

export async function getPullRequestDiffFiles() {
    const config = cli.defaultConfig();
    const pr = await devOps.createPullRequestProperties(config);

    if (pr === undefined) {
        console.log(`pr is undefined`);
        return null;
    }

    const changedFiles = await pr.structuralDiff().toArray();
    console.log(`diff files in current PR: ${changedFiles.length}`);
    return changedFiles;
}

getPullRequestDiffFiles();