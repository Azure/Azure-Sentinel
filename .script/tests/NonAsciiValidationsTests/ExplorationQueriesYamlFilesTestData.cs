using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace NonAsciiValidations.Tests
{
    public class ExplorationQueriesYamlFilesTestData : FilesTestData
    {
        protected override string FolderName => "Exploration Queries";
        protected override string FileExtension => "*.yaml";
    }
}
