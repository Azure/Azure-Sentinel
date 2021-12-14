using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public class DetectionsYamlFilesLoader : YamlFilesLoader
    {
        public DetectionsYamlFilesLoader() : base(new List<string>() { "Detections", "Solutions"})
        {
        }
        
        public override List<string> GetFilesNames()
        {
            var files = Directory.GetFiles(DirectoryPaths[0], "*.yaml", SearchOption.AllDirectories).ToList();
            files.AddRange(Directory.GetFiles(DirectoryPaths[1], "*.yaml", SearchOption.AllDirectories).ToList().Where(s => s.Contains("Analytic Rules")));

            return files;
        }
    }
}