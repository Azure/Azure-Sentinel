using System.Collections.Generic;
using System.IO;

namespace Kqlvalidations.Tests
{
    public class CommonFunctionsYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            return new List<string>() { Path.Combine(basePath, "ASIM", "lib", "functions") };
        }
    }
}