using System.IO;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, YamlFileProp>
    {
        public YamlFilesTestData(YamlFilesLoader yamlFilesLoader)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(f =>
            {
                var fileName = Path.GetFileName(f);
                Add(fileName, new YamlFileProp()
                {
                    FullPath = f,
                    FileName = fileName
                });
            });
        }
    }
}
