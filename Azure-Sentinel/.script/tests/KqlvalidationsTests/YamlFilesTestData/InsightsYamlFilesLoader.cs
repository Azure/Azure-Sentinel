using System.Collections.Generic;
using System.IO;

namespace Kqlvalidations.Tests
{
    public class InsightsYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
           return  new List<string> { Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "Insights")}; 
        }
    }
}