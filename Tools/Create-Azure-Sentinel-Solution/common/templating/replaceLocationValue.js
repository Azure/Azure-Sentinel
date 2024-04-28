/** replacePlaybookVarNames.js
 * This small script is utilized to perform a global replacement of playbook variables within a string.
 * This is necessary due to PowerShell not providing global match/replacement capability.
 */
const regexStr = /(resourceGroup\(\)\.location)/g;
const inputString = process.argv[2];
const playbookNum = process.argv[3];

if (inputString.match(regexStr)) {
    console.log(inputString.replace(regexStr, "parameters('workspace-location')"))
} else {
    console.log(inputString);
}