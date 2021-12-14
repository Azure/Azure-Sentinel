using System;
using System.IO;
using System.Reflection;

namespace Kqlvalidations.Tests
{
    public static class DirectoryPathsUtils
    {
        public static string GetTestDirectory(int testFolderDepth = 3)
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            return rootDir.FullName;
        }
        
        private static string GetAssemblyDirectory()
        {
            string codeBase = Assembly.GetExecutingAssembly().CodeBase;
            UriBuilder uri = new UriBuilder(codeBase);
            string path = Uri.UnescapeDataString(uri.Path);
            return Path.GetDirectoryName(path);
        }
    }
}