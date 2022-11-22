using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class DataConnectorFilesLoader : JsonFilesLoader
    {
        protected override List<string> GetDirectoryPaths()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            //var detectionsDir = new List<string> { Path.Combine(basePath, "Detections")};
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var dataconnectorDir = Directory.GetDirectories(solutionDirectories, "Data Connectors", SearchOption.AllDirectories);

            return dataconnectorDir.ToList();
        }
    }
}
