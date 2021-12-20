using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class YamlFilesLoader
    {
        private static List<string> DirectoryNames { get; set; }
        protected List<string> DirectoryPaths { get; }

        protected YamlFilesLoader(List<string> directoryNames)
        {
            DirectoryNames = directoryNames;
            DirectoryPaths = GetYamlFilesPaths();
        }

        public virtual List<string> GetFilesNames()
        {
            return Directory.GetFiles(DirectoryPaths[0], "*.yaml", SearchOption.AllDirectories).ToList();
        }

        private static List<string> GetYamlFilesPaths()
        {
            var rootDir = Utils.GetTestDirectory(6);
            List<string> detectionPaths = new List<string>();
            
            foreach (var dirName in DirectoryNames)
            {
                detectionPaths.Add(Path.Combine(rootDir, dirName));
            }

            return detectionPaths;
        }
    }
}