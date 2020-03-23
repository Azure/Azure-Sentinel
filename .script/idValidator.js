const git = require('simple-git/promise');
const avocado = require("@azure/avocado");
const templateIdRegex = "id: [0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";

async function getDiff() {
    let diffSummary = null;
    let config = avocado.cli.defaultConfig();
    let workingDir = config.cwd;
    let pr = await avocado.devOps.createPullRequestProperties(config);
    let changedFiles = await pr.diff();
    console.log("Changed files:\n" + changedFiles);
    var options = [pr.targetBranch, pr.sourceBranch];

    try {
        diffSummary = await git(workingDir).diff(options, null);
    }
    catch (e) {
        console.log("An error occerrued")
    }
    return diffSummary;
}

getDiff().then(function(result){
    console.log(result);
    if (result.search(templateIdRegex) > 0){
        console.log("Some of the files ID has changed")
    }    
    else {
        console.log("All tests passed successfuly")
    }    
})    
