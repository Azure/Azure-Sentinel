using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class ExplorationQueriesYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            return new List<string> { Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "Exploration Queries") };
        }
    }
}