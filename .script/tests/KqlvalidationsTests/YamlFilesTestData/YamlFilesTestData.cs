using System.IO;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<YamlFileProp>
    {
        protected YamlFilesTestData(YamlFilesLoader yamlFilesLoader)
        {
            var files = yamlFilesLoader.GetFilesNames();
            files.ForEach(f => Add(new YamlFileProp()
            {
                FullPath = f, 
                FileName = Path.GetFileName(f)
            }));
        }
    }
}
