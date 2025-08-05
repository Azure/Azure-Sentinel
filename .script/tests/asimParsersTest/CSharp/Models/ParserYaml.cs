using System.Collections.Generic;

namespace AsimParserValidation.Models
{
    /// <summary>
    /// Represents a parser YAML file structure
    /// </summary>
    public class ParserYaml
    {
        /// <summary>
        /// The name of the parser
        /// </summary>
        public string? ParserName { get; set; }

        /// <summary>
        /// The equivalent built-in parser name
        /// </summary>
        public string? EquivalentBuiltInParser { get; set; }

        /// <summary>
        /// The KQL query for the parser
        /// </summary>
        public string? ParserQuery { get; set; }

        /// <summary>
        /// Parser metadata
        /// </summary>
        public ParserMetadata? Parser { get; set; }

        /// <summary>
        /// Normalization information
        /// </summary>
        public NormalizationInfo? Normalization { get; set; }

        /// <summary>
        /// List of reference documentation
        /// </summary>
        public List<ReferenceInfo>? References { get; set; }

        /// <summary>
        /// List of parsers (for union parsers)
        /// </summary>
        public List<string>? Parsers { get; set; }
    }

    /// <summary>
    /// Represents parser metadata
    /// </summary>
    public class ParserMetadata
    {
        /// <summary>
        /// The title of the parser
        /// </summary>
        public string? Title { get; set; }

        /// <summary>
        /// The version of the parser
        /// </summary>
        public string? Version { get; set; }

        /// <summary>
        /// The last updated date
        /// </summary>
        public string? LastUpdated { get; set; }
    }

    /// <summary>
    /// Represents normalization information
    /// </summary>
    public class NormalizationInfo
    {
        /// <summary>
        /// The schema name
        /// </summary>
        public string? Schema { get; set; }

        /// <summary>
        /// The schema version
        /// </summary>
        public string? Version { get; set; }
    }

    /// <summary>
    /// Represents reference information
    /// </summary>
    public class ReferenceInfo
    {
        /// <summary>
        /// The title of the reference
        /// </summary>
        public string? Title { get; set; }

        /// <summary>
        /// The link to the reference
        /// </summary>
        public string? Link { get; set; }
    }
}
