using System;
using System.Collections.Generic;

namespace AsimParserValidation.Models
{
    /// <summary>
    /// Represents the overall validation result
    /// </summary>
    public class ValidationResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public List<ParserValidationResult> ParserResults { get; set; } = new();
        public DateTime ExecutedAt { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Represents the validation result for a specific parser
    /// </summary>
    public class ParserValidationResult
    {
        public string ParserPath { get; set; } = string.Empty;
        public string ParserType { get; set; } = string.Empty;
        public string? ParserName { get; set; }
        public bool Success { get; set; }
        public string? ErrorMessage { get; set; }
        public List<ParserTestResult> TestResults { get; set; } = new();
        public DateTime ExecutedAt { get; set; } = DateTime.UtcNow;
    }
}
