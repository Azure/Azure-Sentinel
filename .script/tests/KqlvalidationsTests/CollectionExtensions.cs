using System.Collections.Generic;

namespace Kqlvalidations.Tests
{
    public static class CollectionExtensions
    {
        public static TValue GetValueOrDefault<TKey, TValue>(this Dictionary<TKey, TValue> dictionary, TKey key) where TKey : notnull
        {
            return dictionary.TryGetValue(key, out TValue value) ? value : default(TValue);
        }
    }
}