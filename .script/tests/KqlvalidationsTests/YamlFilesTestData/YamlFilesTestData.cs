using System.IO;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, YamlFilesLoader>
    {
        protected YamlFilesTestData(YamlFilesLoader yamlFilesLoader)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(f => Add(Path.GetFileName(f), yamlFilesLoader));
        }
    }
}
