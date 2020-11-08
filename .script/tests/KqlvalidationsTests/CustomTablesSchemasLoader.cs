using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class CustomTablesSchemasLoader : ITableSchemasLoader
    {
        private readonly List<TableSchema> _tableSchemas;
        public CustomTablesSchemasLoader()
        {
            _tableSchemas = new List<TableSchema>();
            var jsonFiles = Directory.GetFiles(DetectionsYamlFilesTestData.GetCustomTablesPath(), "*.json");
            foreach (var jsonFile in jsonFiles)
            {
                var tableSchema = ReadTableSchema(jsonFile);
                if (tableSchema != null)
                {
                    _tableSchemas.Add(tableSchema);
                }
            }
        }

        public IEnumerable<TableSchema> Load()
        {
            return _tableSchemas;
        }

        private TableSchema ReadTableSchema(string jsonFile)
        {
            using (StreamReader r = new StreamReader(jsonFile))
            {
                string json = r.ReadToEnd();
                return JsonConvert.DeserializeObject<TableSchema>(json);
            }
        }
    }
}
