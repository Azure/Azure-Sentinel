using Octokit;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class YamlFilesLoader
    {
        protected const int TestFolderDepth = 6;

        protected abstract List<string> GetDirectoryPaths();
        
        public List<string> GetFilesNames()
        {
            var directoryPaths = GetDirectoryPaths();
            return directoryPaths.Aggregate(new List<string>(), (accumulator, directoryPath) =>
            {
                var files = Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories).ToList();
                return accumulator.Concat(files).ToList();
            });
        }
    }
}