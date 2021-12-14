using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;

namespace Kqlvalidations.Tests
{
    public class DetectionsYamlFilesLoader : YamlFilesLoader
    {
        public DetectionsYamlFilesLoader() : base(new List<string>() { "Detections", "Solutions"})
        {
        }

        public override string GetFilePath(string fileName)
        {
            try
            {
                return Directory.GetFiles(DirectoryPaths[0], fileName, SearchOption.AllDirectories).Single();
            }
            catch
            {
                return  Directory.GetFiles(DirectoryPaths[1], fileName, SearchOption.AllDirectories).Single(s => s.Contains("Analytic Rules"));
            }
        }

        public override List<string> GetFilesNames()
        {
            var files = Directory.GetFiles(DirectoryPaths[0], "*.yaml", SearchOption.AllDirectories).ToList();
            files.AddRange(Directory.GetFiles(DirectoryPaths[1], "*.yaml", SearchOption.AllDirectories).ToList().Where(s => s.Contains("Analytic Rules")));

            return files;
        }
    }
}