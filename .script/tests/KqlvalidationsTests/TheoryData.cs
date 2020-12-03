using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public abstract class TheoryData : IEnumerable<object[]>
    {
        readonly List<object[]> _data = new List<object[]>();

        protected void Add(params object[] values)
        {
            _data.Add(values);
        }

        public IEnumerator<object[]> GetEnumerator()
        {
            return _data.GetEnumerator();
        }

        IEnumerator IEnumerable.GetEnumerator()
        {
            return GetEnumerator();
        }
    }

    public class TheoryData<T> : TheoryData
    {
        /// <summary>
        /// Adds Data to TheoryData
        /// </summary>
        /// <param name="value">first argument</param>
        public void AddData(T value)
        {
            Add(value);
        }
    }

    public class TheoryData<T1, T2> : TheoryData
    {
        /// <summary>
        /// Adds Data to TheoryData
        /// </summary>
        /// <param name="value1">first argument</param>
        /// <param name="value2">second argument</param>
        public void Add(T1 value1, T2 value2)
        {
            Add(value1, (object)value2);
        }
    }

    public class TheoryData<T1, T2, T3> : TheoryData
    {
        /// <summary>
        /// Adds Data to TheoryData
        /// </summary>
        /// <param name="value1">first argument</param>
        /// <param name="value2">second argument</param>
        /// <param name="value3">third argument</param>
        public void Add(T1 value1, T2 value2, T3 value3)
        {
            Add(value1, value2, (object)value3);
        }
    }
}
