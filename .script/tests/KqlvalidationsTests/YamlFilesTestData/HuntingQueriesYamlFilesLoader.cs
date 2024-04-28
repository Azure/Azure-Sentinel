using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class HuntingQueriesYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var detectionsDir = new List<string> { Path.Combine(basePath, "Hunting Queries") };
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var huntingQueriesRulesDir = Directory.GetDirectories(solutionDirectories, "Hunting Queries", SearchOption.AllDirectories);

            return huntingQueriesRulesDir.Concat(detectionsDir).ToList();
        }
    }
}
