using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Kqlvalidations.Tests.TableSchemasLoaders
{
    /// <summary>
    /// Loads Sentinel table schemas, allowing local schemas to override defaults with matching names.
    /// </summary>
    public class LocalOverrideTablesLoader : ITableSchemasLoader
    {
        private readonly string _customTablesPath;

        public LocalOverrideTablesLoader(string customTablesPath)
        {
            _customTablesPath = customTablesPath;
        }

        /// <summary>
        /// Returns default and local table schemas after applying local overrides.
        /// </summary>
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
