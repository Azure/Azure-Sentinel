package activity

import (
	"encoding/json"

	"github.com/labstack/echo/v4"
)

type SentinelEvent struct {
	Action           string      `json:"action"`
	Type             string      `json:"event_type"`
	Initiator        string      `json:"initiator"`
	Metadata         interface{} `json:"metadata"`
	OrganizationUUID string      `json:"organization_uuid"`
	EventTime        int64       `json:"timestamp"`
	UserEmail        string      `json:"user_email"`
	UserUUID         string      `json:"user_uuid"`
}

func MapAPIResponseToMSSentinel(events []*Event, ctx echo.Context) []SentinelEvent {
	sentinelEvents := make([]SentinelEvent, 0, len(events))

	for _, record := range events {
		var metadata interface{}

		if len(record.Metadata) > 0 {
			if err := json.Unmarshal(record.Metadata, &metadata); err != nil {
				ctx.Logger().Printf("Error unmarshalling metadata: %v\n", err)

				metadata = nil
			}
		}

		event := SentinelEvent{
			EventTime:        record.Timestamp,
			Type:             record.Type,
			Action:           record.Action,
			OrganizationUUID: record.OrganizationUUID,
			UserUUID:         record.User.UUID,
			UserEmail:        record.User.Email,
			Metadata:         metadata,
			Initiator:        record.Initiator,
		}

		if mspData, ok := metadata.(map[string]interface{}); ok {
			if msp, ok := (mspData)["msp"].(map[string]interface{}); ok {
				// Check for user_uuid in metadata.msp
				if userUUID, ok := msp["user_uuid"].(string); ok && userUUID != "" {
					event.UserUUID = userUUID
				}
				// Check for user_email in metadata.msp
				if userEmail, ok := msp["user_email"].(string); ok && userEmail != "" {
					event.UserEmail = userEmail
				}
			}
		}

		sentinelEvents = append(sentinelEvents, event)
	}

	return sentinelEvents
}
