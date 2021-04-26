using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace NonAsciiValidations.Tests
{
    public abstract class FilesTestData : TheoryData<string,string>
    {
        public FilesTestData()
        {
            string rootPath = GetFilesRootPath();
            var files = Directory.GetFiles(rootPath, FileExtension, SearchOption.AllDirectories).ToList();
            files.ForEach(f => Add(Path.GetFileName(f),f));
        }

        private string GetFilesRootPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 6;
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            var detectionPath = Path.Combine(rootDir.FullName, FolderName);
            return detectionPath;
        }

        public string GetCustomTablesPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 3;
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            var rootPath = Path.Combine(rootDir.FullName, FolderName);
            return rootPath;
        }

        protected abstract string FolderName {get;}
        protected abstract string FileExtension { get; }

        public static string GetSkipTemplatesPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 3;
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
