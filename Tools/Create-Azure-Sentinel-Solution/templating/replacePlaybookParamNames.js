/** replacePlaybookParamNames.js
 * This small script is utilized to perform a global replacement of playbook parameter variables within a string.
 * This is necessary due to PowerShell not providing global match/replacement capability.
 */
const regexStr = /parameters\(\'([\w\-\s]+)\'\)/g;
const inputString = process.argv[2];
const playbookNum = process.argv[3];

if (inputString.match(regexStr)) {
    console.log(inputString.replace(regexStr, `parameters('playbook${playbookNum}-$1')`))
} else {
    console.log(inputString);
}