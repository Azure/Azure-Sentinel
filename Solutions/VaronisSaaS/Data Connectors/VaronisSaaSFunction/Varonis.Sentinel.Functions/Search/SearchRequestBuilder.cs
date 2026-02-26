using System.Collections.Generic;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.Search
{
    internal class SearchRequestBuilder
    {
        private readonly SearchRequest _searchRequest;
        public SearchRequestBuilder(SearchQuery query, IReadOnlyCollection<string> attributePaths)
        {
            _searchRequest = new SearchRequest
            {
                Query = query,
                Rows = new RowDataRequest
                {
                    Columns = attributePaths
                },
                RequestParams = new
                {
                    IgnoreCache = true,
                    SearchSource = 1,
                    SearchSourceName = "Alert"
                }
            };
        }

        public SearchRequestBuilder WithOrdering(string column, bool? desc = false)
        {
            if (!string.IsNullOrEmpty(column))
            {
                _searchRequest.Rows.Ordering =
                    new object[]
                    {
                        new
                        {
                            Path = column,
                            SortOrder = desc ?? false ? "Desc" : "Asc"
                        }
                    };
            }

            return this;
        }

        public SearchRequest Build()
        {
            return _searchRequest;
        }
    }
}
