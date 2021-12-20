using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class YamlFilesLoader
    {
        protected List<string> DirectoryPaths { get; }

        private const int TestFolderDepth = 6;

        protected YamlFilesLoader(List<string> directoryNames)
        {
            DirectoryPaths = GetYamlFilesPaths(directoryNames);
        }

        public virtual List<string> GetFilesNames()
        {
            return DirectoryPaths.Aggregate(new List<string>(), (accumulator, directoryPath) =>
            {
                var files = Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories).ToList();
                return accumulator.Concat(files).ToList();
            });
        }

        private static List<string> GetYamlFilesPaths(List<string> directoryNames)
        {
            var rootDir = Utils.GetTestDirectory(TestFolderDepth);
            List<string> detectionPaths = new List<string>();
            
            foreach (var dirName in directoryNames)
            {
                detectionPaths.Add(Path.Combine(rootDir, dirName));
            }

            return detectionPaths;
        }
    }
}