using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class JsonFilesTestData : TheoryData<string, string>
    {
        public JsonFilesTestData(JsonFilesLoader jsonFilesLoader, List<string> fileNamesToIgnore = null)
        {
            var files = jsonFilesLoader.GetFilesNames();

            if (files != null)
            {
                files.ForEach(filePath =>
                {
                    if (fileNamesToIgnore == null || !fileNamesToIgnore.Any(fileNameToIgnore => filePath.EndsWith(fileNameToIgnore)))
                    {
                        var fileName = Path.GetFileName(filePath);
                        Add(fileName, Utils.EncodeToBase64(filePath));
                    }
                });
            }
        }

    }
}