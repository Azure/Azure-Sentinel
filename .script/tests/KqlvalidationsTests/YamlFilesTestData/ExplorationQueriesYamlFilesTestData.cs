using System.Collections.Generic;

namespace Kqlvalidations.Tests
{
    public class ExplorationQueriesYamlFilesTestData : YamlFilesTestData
    {
        private static readonly List<string> _fileNamesToIgnore = new List<string> { "ExplorationQueryTemplate.yaml" };

        public ExplorationQueriesYamlFilesTestData() : base(new ExplorationQueriesYamlFilesLoader(), _fileNamesToIgnore)
        {
        }
    }
}
