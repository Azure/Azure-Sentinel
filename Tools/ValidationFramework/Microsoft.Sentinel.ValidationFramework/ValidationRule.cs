using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Microsoft.Sentinel.ValidationFramework
{
    public abstract class ValidationRule
    {
        public Regex ContentPathRegex { get; set; }

        public abstract bool Validate(string contentPath);
    }
}
