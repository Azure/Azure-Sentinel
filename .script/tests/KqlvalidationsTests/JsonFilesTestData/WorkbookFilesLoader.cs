using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Schema.Generation;
using Newtonsoft.Json.Schema;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class WorkbookFilesLoader : JsonFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var dataconnectorDir = Directory.GetDirectories(solutionDirectories, "Workbooks", SearchOption.AllDirectories);

            return dataconnectorDir.ToList();
        }
    }
}
