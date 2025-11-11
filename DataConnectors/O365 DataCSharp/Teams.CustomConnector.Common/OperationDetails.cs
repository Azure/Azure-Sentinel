using System;

namespace Teams.CustomConnector.Common
{

    /// <summary></summary>
    public class OperationDetails
    {

        /// <summary>Gets or sets the last run start time.</summary>
        /// <value>The last run start time.</value>
        public DateTime? LastRunStartTime { get; set; }


        /// <summary>Gets or sets the last run end time.</summary>
        /// <value>The last run end time.</value>
        public DateTime? LastRunEndTime { get; set; }


        /// <summary>Gets or sets the total audit records processed.</summary>
        /// <value>The total audit records processed.</value>
        public int TotalAuditRecordsProcessed { get; set; }


        /// <summary>Gets or sets the total records processed in life time.</summary>
        /// <value>The total records processed in life time.</value>
        public long TotalRecordsProcessedInLifeTime { get; set; }


        /// <summary>Gets or sets a value indicating whether this instance is last run successful.</summary>
        /// <value>
        ///   <c>true</c> if this instance is last run successful; otherwise, <c>false</c>.</value>
        public bool IsLastRunSuccessful { get; set; }


        /// <summary>Gets or sets the total fail count since last successful run.</summary>
        /// <value>The total fail count since last successful run.</value>
        public int  TotalFailCountSinceLastSuccessfulRun { get; set; }
    }
}
