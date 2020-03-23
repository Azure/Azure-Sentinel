const git = require('simple-git/promise');
const avocado = require("@azure/avocado");
// const gitWrapper = require("./utils/gitWrapper");
const templateIdRegex = "id: [0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
console.log(process.cwd());

// let fileTypeSuffixes = ["json", "yaml", "yml"];
// const changedFiles = await GetDiffFiles(fileTypeSuffixes);
// console.log("-------Test:    " + changedFiles[0].path);

let a = 5;
let b = 10;
console.log(`Fifteen is ${a + b} and
not ${2 * a + b}.`);


async function getDiff() {
    let diffSummary = null;
    let config = avocado.cli.defaultConfig();
    let workingDir = config.cwd;
    let pr = await avocado.devOps.createPullRequestProperties(config);
    let changedFiles = await pr.diff();
    
    for (const file of changedFiles) {
        var filePath = workingDir + '/' + file.path;
        console.log("-------------------\nFile path: " + filePath + "\n---------------------------------")
        var options = [pr.targetBranch, pr.sourceBranch, filePath];
        diffSummary = await git(workingDir).diff(options, null);
        console.log(diffSummary);
        if (diffSummary.search(templateIdRegex) > 0){
            console.log('File - ' +file.path + "is incorrect. Don't change id please");
            return -1;
        }    
        else {
            console.log("All tests passed successfuly")
        }    
    }    

    return 0;
}

getDiff().then(function(result){
    process.exit(result);
})    


// getDiff().then(function(result){
//     console.log(result);
//     if (result.search(templateIdRegex) > 0){
//         console.log("Some of the files ID has changed")
//     }    
//     else {
//         console.log("All tests passed successfuly")
//     }    
// })    
