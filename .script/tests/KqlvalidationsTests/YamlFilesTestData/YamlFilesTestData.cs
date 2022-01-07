using System.IO;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, string>
    {
        public YamlFilesTestData(YamlFilesLoader yamlFilesLoader)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(filePath =>
            {
                var fileName = Path.GetFileName(filePath);
                Add(fileName, Utils.EncodeToBase64(filePath));
            });
        }
    }
}
