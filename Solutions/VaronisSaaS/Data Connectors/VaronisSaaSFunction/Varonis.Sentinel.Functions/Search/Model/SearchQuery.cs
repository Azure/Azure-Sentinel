namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class SearchQuery
    {
        public string EntityName { get; set; }

        public FilterGroup Filter { get; set; }

        public string TimeZone { get; set; }
    }
}
