using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class InsightsYamlFilesLoader : YamlFilesLoader
    {
        public InsightsYamlFilesLoader() : base(new List<string>() {"Insights"})
        {
        }
    }
}