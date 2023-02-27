
var message = 'Hello World';
console.log(message);

        const fileContent = fs.readFileSync('C:\Github\Azure-Sentinel\Solutions\Alibaba Cloud\Package\createUiDefinition.json', "utf8");
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";
        var filePath = "Solutions/Alibaba Cloud/Package/createUiDefinition.json"
        // Read skip text from a file
        const skipTextFile = fs.readFileSync('./.script/validate-tag-text.txt', "utf8");
        const validTags = skipTextFile.split("\n").filter(tag => tag.length > 0);

        // SEARCH & CHECK IF SKIP TEXT EXIST IN THE FILE
        //var fileContentObj = JSON.parse(fileContent.replace(/\\/g, '\\\\'));
        var fileContentStringify = JSON.stringify(fileContent);
        console.log(fileContentStringify)
        var fileContentObj = JSON.parse(fileContentStringify);

        for (const tagName of validTags) 
        {
            if (filePath.includes("createUiDefinition.json"))
            {
                var tagContent = fileContentObj["parameters"]["config"]["basics"]["description"];
            }
            else
            {
                var tagContent = fileContentObj[tagName];
            }

            if (tagContent)
            {
                let hasAzureSentinelText = tagContent.toLowerCase().includes(searchText.toLowerCase());
                console.log("inside of if");
                if (hasAzureSentinelText) {
                    throw new Error(`Please update text from '${searchText}' to '${expectedText}' in '${tagName}' tag in the file '${filePath}'`);
                }
            }
        }