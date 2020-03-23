const git = require('simple-git/promise');
var templateIdRegex = "id: [0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
var targetBranch = "master";
var sourceBranch = null;
var workingDir = __dirname


async function getBranch(options) {
    var branchSummary = await git(workingDir).branch(options, null);
    
    return branchSummary;
}

getBranch([]).then(branchs => sourceBranch = branchs.current);

var options = [sourceBranch, targetBranch];
////var options = ["--name-status"];

async function getDiff(options) {
   let diffSummary = null;
   try {
       diffSummary = await git(workingDir).diff(options, null);
   }
   catch (e) {
      console.log("An error occerrued")
   }
   return diffSummary;
}

getDiff(options).then(function(result){
    if (result.search(templateIdRegex) > 0){
        console.log("Some of the files ID has changed")
    }
    else {
        console.log("All tests passed successfuly")
    }
})














