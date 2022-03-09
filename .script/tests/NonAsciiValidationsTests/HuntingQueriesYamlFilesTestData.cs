using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace NonAsciiValidations.Tests
{
	public class HuntingQueriesYamlFilesTestData : FilesTestData
	{
		protected override string[] FolderName => new string[2] { "Hunting Queries", "Solutions" };
		protected override string FileExtension => "*.yaml";
	}
}
