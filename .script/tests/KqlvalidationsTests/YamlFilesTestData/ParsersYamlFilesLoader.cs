using Kqlvalidations.Tests.FunctionSchemasLoaders;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class ParsersYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            return ParsersDatabase.Parsers.Select(parser => Path.Combine(basePath, "Parsers", parser.Schema, "Parsers")).ToList();
        }
    }
}