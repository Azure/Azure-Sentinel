using System;
using System.IO;
using System.Linq;
using System.Reflection;

namespace Kqlvalidations.Tests
{
    public static class Utils
    {
        public static string GetTestDirectory(int testFolderDepth)
        {
            if (testFolderDepth == 3)
            {
                return GetToolkitTestDirectory(testFolderDepth);
            }

            var contentRoot = Environment.GetEnvironmentVariable("SENTINEL_VALIDATION_CONTENT_ROOT");
            if (!string.IsNullOrWhiteSpace(contentRoot))
            {
                var resolvedRoot = Path.GetFullPath(contentRoot);
                if (!Directory.Exists(resolvedRoot) || !Directory.Exists(Path.Combine(resolvedRoot, "Solutions")))
                {
                    throw new DirectoryNotFoundException($"SENTINEL_VALIDATION_CONTENT_ROOT is not a repository root containing Solutions/: {contentRoot}");
                }
                return resolvedRoot;
            }

            return GetToolkitTestDirectory(testFolderDepth);
        }

        public static string GetToolkitTestDirectory(int testFolderDepth)
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            return rootDir.FullName;
        }

        public static bool IsPrivateSolutionContentPath(string filePath)
        {
            var contentRoot = GetTestDirectory(6);
            var solutionsRoot = Path.GetFullPath(Path.Combine(contentRoot, "Solutions"));
            var resolvedFile = Path.GetFullPath(filePath);
            var relativePath = Path.GetRelativePath(solutionsRoot, resolvedFile);
            if (relativePath == ".." || relativePath.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal))
            {
                return false;
            }

            return relativePath.Split(new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                    StringSplitOptions.RemoveEmptyEntries)
                .Any(segment => segment.Equals("Logs", StringComparison.OrdinalIgnoreCase)
                    || segment.Equals("Reports", StringComparison.OrdinalIgnoreCase)
                    || segment.Equals("Evidence", StringComparison.OrdinalIgnoreCase));
        }
        
        public static string EncodeToBase64(string plainText) {
            var plainTextBytes = System.Text.Encoding.UTF8.GetBytes(plainText);
            return Convert.ToBase64String(plainTextBytes);
        }
        
        public static string DecodeBase64(string base64EncodedData) {
            var base64EncodedBytes = Convert.FromBase64String(base64EncodedData);
            return System.Text.Encoding.UTF8.GetString(base64EncodedBytes);
        }
        
        private static string GetAssemblyDirectory()
        {
            string location = Assembly.GetExecutingAssembly().Location;
            return Path.GetDirectoryName(location);
        }
    }
}