using System;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Xml;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class RangeTimeSpanIsoFormatAttribute : RangeAttribute
    {
        private readonly TimeSpan _minimum;
        private readonly TimeSpan _maximum;

        public RangeTimeSpanIsoFormatAttribute(string minimum, string maximum)
            : base(typeof(TimeSpan), minimum, maximum)
        {
            _minimum = TimeSpan.Parse(minimum);
            _maximum = TimeSpan.Parse(maximum);
        }

        public override string FormatErrorMessage(string name)
        {
            base.FormatErrorMessage(name);
            return string.Format(CultureInfo.CurrentCulture, base.ErrorMessageString, new object[] {
                name,
                XmlConvert.ToString(_minimum),
                XmlConvert.ToString(_maximum)
            });
        }
    }
}
