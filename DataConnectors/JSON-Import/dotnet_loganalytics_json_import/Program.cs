// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.
using Newtonsoft.Json;
using System;
using System.IO;

namespace UploadToLogAnalytics
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length != 4)
            {
                Console.WriteLine("USAGE");
                Console.WriteLine("UploadToLogAnalytics.exe [workspaceId] [workspaceKey] [tableName] [jsonFileName]");
                return;
            }

            var workspaceId = args[0];
            var workspaceKey = args[1];
            var tableName = args[2];
            var jsonFilename = args[3];

            var collector = new HTTPDataCollectorAPI.Collector(workspaceId, workspaceKey);

            dynamic lookups = JsonConvert.DeserializeObject(File.ReadAllText(jsonFilename));

            uint count = 0;
            foreach (var entry in lookups)
            {
                try
                {
                    var t = collector.Collect(tableName, JsonConvert.SerializeObject(entry));
                    t.Wait();
                    count++;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                }

                if (count % 5000 == 0)
                {
                    Console.WriteLine(count);
                }
            }
        }
    }
}
