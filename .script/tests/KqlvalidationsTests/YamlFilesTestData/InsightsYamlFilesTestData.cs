using System.IO;

namespace Kqlvalidations.Tests
{
    public class InsightsYamlFilesTestData : YamlFilesTestData
    {
        public InsightsYamlFilesTestData() : base(new InsightsYamlFilesLoader())
        {
        }
    }
}