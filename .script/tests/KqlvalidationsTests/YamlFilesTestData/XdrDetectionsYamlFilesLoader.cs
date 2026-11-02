using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class XdrDetectionsYamlFilesLoader : YamlFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var solutionsDir = Path.Join(basePath, "Solutions");
            if (!Directory.Exists(solutionsDir))
            {
                return new List<string>();
            }

            return Directory.EnumerateDirectories(solutionsDir)
                .Select(solDir => Path.Combine(solDir, "XDR Detections"))
                .Where(dir => Directory.Exists(dir) && !Utils.IsPrivateSolutionContentPath(dir))
                .ToList();
        }
    }
}
