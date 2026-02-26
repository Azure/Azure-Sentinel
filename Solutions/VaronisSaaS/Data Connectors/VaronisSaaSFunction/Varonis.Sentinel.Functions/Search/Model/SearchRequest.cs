using System.Collections.Generic;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class SearchRequest
    {
        public SearchQuery Query { get; set; }

        public RowDataRequest Rows { get; set; }

        public List<object> Facets { get; set; }

        public object RequestParams { get; set; }
    }
}
