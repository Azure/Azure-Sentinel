package sentinel

import "github.com/go-faker/faker/v4"

type LogEntry struct {
	Action           string `faker:"oneof: item_access_revealed, item_viewed, master_validated" json:"action"`
	EventType        string `faker:"oneof: lock, global_settings, integrations"                 json:"event_type"`
	Initiator        string `faker:"email"                                                      json:"initiator"`
	OrganizationUUID string `faker:"uuid_hyphenated"                                            json:"organization_uuid"`
	Timestamp        int64  `faker:"unix_time"                                                  json:"timestamp"`
	UserEmail        string `faker:"email"                                                      json:"user_email"`
	UserUUID         string `faker:"uuid_hyphenated"                                            json:"user_uuid"`
}

func (e *LogEntry) Fake() error {
	return faker.FakeData(e)
}
