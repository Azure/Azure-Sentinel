using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Kqlvalidations.Tests.TableSchemasLoaders
{
    public class LocalOverrideTablesLoader : ITableSchemasLoader
    {
        private readonly string _customTablesPath;

        public LocalOverrideTablesLoader(string customTablesPath)
        {
            _customTablesPath = customTablesPath;
        }

        public IEnumerable<TableSchema> Load()
        {
            var customTables = new CustomJsonDirectoryTablesLoader(_customTablesPath)
                .Load()
                .ToList();
            var customTableNames = customTables
                .Select(table => table.Name)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);
            var defaultTables = new SentinelDefaultTablesLoader()
                .Load()
                .Where(table => !customTableNames.Contains(table.Name));

            return defaultTables.Concat(customTables);
        }
    }
}
