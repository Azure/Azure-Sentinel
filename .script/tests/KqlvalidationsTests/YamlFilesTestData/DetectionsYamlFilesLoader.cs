using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class DetectionsYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var detectionsDir = new List<string> { Path.Combine(basePath, "Detections")};
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var analyticsRulesDir  = Directory.GetDirectories(solutionDirectories, "Analytic Rules", SearchOption.AllDirectories);

            return analyticsRulesDir.Concat(detectionsDir).ToList();
        }
    }
}