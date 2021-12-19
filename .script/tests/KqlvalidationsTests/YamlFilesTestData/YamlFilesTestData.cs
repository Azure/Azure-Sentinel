using System.IO;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, string>
    {
        public YamlFilesTestData(YamlFilesLoader yamlFilesLoader)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(f =>
            {
                var fileName = Path.GetFileName(f);
                Add(fileName, f);
            });
        }
    }
}
