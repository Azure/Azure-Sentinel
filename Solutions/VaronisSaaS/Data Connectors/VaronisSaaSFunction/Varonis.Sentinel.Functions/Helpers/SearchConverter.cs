using System.Collections.Generic;
using System.Linq;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.Helpers
{
    internal class SearchConverter
    {
        public static IEnumerable<IDictionary<string, string>> ConvertResponseToDictionary(SearchRowsResponse searchResponse)
        {
            var response = new List<Dictionary<string, string>>();

            if (searchResponse.Rows.Any())
            {
                foreach (var row in searchResponse.Rows)
                {
                    var rowsList = row.ToList();
                    var rowDictionary = new Dictionary<string, string>();
                    for (int columnId = 0; columnId < searchResponse.Columns.Length; ++columnId)
                    {
                        string column = searchResponse.Columns[columnId];
                        string value = rowsList[columnId];

                        rowDictionary[column] = value;
                    }
                    response.Add(rowDictionary);
                }
            }

            return response;
        }
    }
}
