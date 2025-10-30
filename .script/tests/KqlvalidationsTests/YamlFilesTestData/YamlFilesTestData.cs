using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, string>
    {
        public YamlFilesTestData(YamlFilesLoader yamlFilesLoader, List<string> fileNamesToIgnore = null)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(filePath =>
            {
                if (!fileNamesToIgnore?.Any(fileNameToIgnore => filePath.EndsWith(fileNameToIgnore)) ?? true)
                {
                    var fileName = Path.GetFileName(filePath);
                    Add(fileName, Utils.EncodeToBase64(filePath));
                }
            });
        }
    }
}
