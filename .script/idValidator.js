const git = require('simple-git/promise');
const avocado = require("@azure/avocado");
// const gitWrapper = require("./utils/gitWrapper");
const templateIdRegex = "id: [0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
console.log(process.cwd());


async function getDiff() {
    let diffSummary = null;
    let config = avocado.cli.defaultConfig();
    let workingDir = config.cwd;
    let pr = await avocado.devOps.createPullRequestProperties(config);
    let changedFiles = await pr.diff();
    console.log(`${changedFiles.length} files changed in current PR`);

    for (const file of changedFiles) {
        let filePath = workingDir + '/' + file.path;
        console.log(`----File path: ${filePath} ----`);
        var options = [pr.targetBranch, pr.sourceBranch, filePath];
        diffSummary = await git(workingDir).diff(options, null);
        if (diffSummary.search(templateIdRegex) > 0){
            console.log(diffSummary);
            console.log(`As you can see, the id of file - "${filePath}" has changed.`);
            return -1;
        }    
    }    

    return 0;
}

getDiff().then(function(result){
    if (result == 0){
        console.log(`${changedFiles.length} files changed in current PR`);
    }
    process.exit(result);
})    
