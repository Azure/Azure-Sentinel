namespace Varonis.Sentinel.Functions.Search.Model
{
    internal enum EmOperator
    {
        In = 1,
        NotIn = 2,
        Between = 3,
        Equals = 4,
        NotEquals = 5,
        Contains = 6,
        NotContains = 7,
        LastDays = 10,
        IncludesAny = 11,
        IncludesAll = 12,
        ExcludesAll = 13,
        GreaterThan = 14,
        LessThan = 0xF,
        QueryId = 0x10,
        NotInQueryId = 17,
        IsEmpty = 20,
        InNestedSearch = 21,
        NotInNestedSearch = 22,
        HasValue = 23
    }
}
