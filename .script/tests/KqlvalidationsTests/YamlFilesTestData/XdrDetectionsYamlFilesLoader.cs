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
            var solutionsDir = Path.Combine(basePath, "Solutions");
            if (!Directory.Exists(solutionsDir))
            {
                return new List<string>();
            }

            return Directory.GetDirectories(solutionsDir, "XDR Detections", SearchOption.AllDirectories)
                .Where(dir => !Utils.IsPrivateSolutionContentPath(dir))
                .ToList();
        }
    }
}
