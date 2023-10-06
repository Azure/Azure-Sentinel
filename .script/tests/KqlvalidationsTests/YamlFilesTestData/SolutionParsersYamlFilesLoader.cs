using Kqlvalidations.Tests.FunctionSchemasLoaders;
using Kusto.Language.Parsing;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class SolutionParsersYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            return Directory.GetDirectories(solutionDirectories, "Parsers", SearchOption.AllDirectories).ToList();
        }
    }
}