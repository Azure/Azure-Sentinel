package activity

import "encoding/json"

type User struct {
	UUID  string `json:"uuid"`
	Email string `json:"email"`
}

type Event struct {
	Type             string          `json:"type"`
	Action           string          `json:"action"`
	Timestamp        int64           `json:"timestamp"`
	OrganizationUUID string          `json:"organization_uuid"`
	User             User            `json:"user"`
	Metadata         json.RawMessage `json:"metadata"` // Use RawMessage to handle any JSON type
	Initiator        string          `json:"initiator"`
}

type APIResponse struct {
	Data     []*Event `json:"data"`
	Metadata struct {
		Total       int `json:"total"`
		PerPage     int `json:"per_page"`
		CurrentPage int `json:"current_page"`
		TotalPages  int `json:"total_pages"`
	} `json:"metadata"`
}
