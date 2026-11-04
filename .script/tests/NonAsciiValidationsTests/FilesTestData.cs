using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace NonAsciiValidations.Tests
{
	public abstract class FilesTestData : TheoryData<string[], string>
	{
		public FilesTestData()
		{
			foreach (string folder in FolderName)
			{
				string rootPath = GetFilesRootPath(folder);
				var files = Directory.GetFiles(rootPath, FileExtension, SearchOption.AllDirectories)
					.Where(file => !IsPrivateSolutionContentPath(file))
					.ToList();
				files.ForEach(f => Add(Path.GetFileName(f), f));
			}
		}

		private string GetFilesRootPath(string folderName)
		{
			var contentRoot = Environment.GetEnvironmentVariable("SENTINEL_VALIDATION_CONTENT_ROOT");
			if (!string.IsNullOrWhiteSpace(contentRoot))
			{
				var resolvedRoot = Path.GetFullPath(contentRoot);
				if (!Directory.Exists(resolvedRoot) || !Directory.Exists(Path.Combine(resolvedRoot, "Solutions")))
				{
					throw new DirectoryNotFoundException($"SENTINEL_VALIDATION_CONTENT_ROOT is not a repository root containing Solutions/: {contentRoot}");
				}
				return Path.Combine(resolvedRoot, folderName);
			}

			var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
			var testFolderDepth = 6;
			for (int i = 0; i < testFolderDepth; i++)
			{
				rootDir = rootDir.Parent;
			}
			var detectionPath = Path.Combine(rootDir.FullName, folderName);
			return detectionPath;
		}

		private static bool IsPrivateSolutionContentPath(string filePath)
		{
			var contentRoot = Environment.GetEnvironmentVariable("SENTINEL_VALIDATION_CONTENT_ROOT");
			if (string.IsNullOrWhiteSpace(contentRoot))
			{
				return false;
			}
			var solutionsRoot = Path.GetFullPath(Path.Combine(contentRoot, "Solutions"));
			var relativePath = Path.GetRelativePath(solutionsRoot, Path.GetFullPath(filePath));
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

		public string GetCustomTablesPath(string folderName)
		{
			var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
			var testFolderDepth = 3;
			for (int i = 0; i < testFolderDepth; i++)
			{
				rootDir = rootDir.Parent;
			}
			var rootPath = Path.Combine(rootDir.FullName, folderName);
			return rootPath;
		}

		protected abstract string[] FolderName { get; }
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
