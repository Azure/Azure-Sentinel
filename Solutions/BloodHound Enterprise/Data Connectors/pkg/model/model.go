package model

import "time"

type ConnectorState struct {
	LastPullTime		*time.Time 	`json:"audit_log_info"`
}

type BloodhoundEnterpriseData struct {
	TimeGenerated        time.Time  `json:"TimeGenerated"`
	DomainSID            string     `json:"domain_sid"`
	ExposureIndex        float64    `json:"exposure_index"`
	TierZeroCount        float64    `json:"tier_zero_count"`
	DomainID             string     `json:"domain_id"`
	NonTierZeroPrincipal string     `json:"non_tier_zero_principal"`
	TierZeroPrincipal    string     `json:"tier_zero_principal"`
	Group                string     `json:"group"`
	Principal            string     `json:"principal"`
	PathID               string     `json:"path_id"`
	User                 string     `json:"user"`
	FindingID            string     `json:"finding_id"`
	PathTitle            string     `json:"path_title"`
	PathType             string     `json:"path_type"`
	Exposure             float64    `json:"exposure"`
	FindingCount         float64    `json:"finding_count"`
	PrincipalCount       float64    `json:"principal_count"`
	ID                   int64      `json:"id"`
	CreatedAt            time.Time  `json:"created_at"`
	UpdatedAt            time.Time  `json:"updated_at"`
	DeletedAt            *time.Time `json:"deleted_at"` // Pointer to handle null values
	DeletedAtV           bool       `json:"deleted_at_v"`
	Severity             string     `json:"severity"`
	DomainImpactValue    float64    `json:"domain_impact_value"`
	DomainName           string     `json:"domain_name"`
	DomainType           string     `json:"domain_type"`
	DataType             string     `json:"data_type"`
	EventType            string     `json:"event_type"`
	EventDetails         string     `json:"event_details"`
}
