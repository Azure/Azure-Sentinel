package connector

import (
	"errors"
	"os"
)

type Config struct {
	BloodhoundAPIKey   string
	BloodhoundAPIKeyId string
	BloodhoundDomain   string
	IngestionEndpoint  string
	RuleId             string
	MAX_UPLOAD_SIZE	   int64
}

func LoadConfigFromEnv() (*Config, error) {

	bloodhoundServer := os.Getenv("BHEDomain")
	if bloodhoundServer == "" {
		return nil, errors.New("BLOODHOUND_SERVER environment variable not set")
	}

	// load bloodhound key information
	bloodhoundApiKey := os.Getenv("BHETokenKey")
	bloodhoundApiKeyId := os.Getenv("BHETokenId")
	if bloodhoundApiKey == "" {
		return nil, errors.New("BHETokenKey is required")
	}
	if bloodhoundApiKeyId == "" {
		return nil, errors.New("BHETokenId is required")
	}

	azureRuleId := os.Getenv("dcrImmutableId")
	if azureRuleId == "" {
		return nil, errors.New("dcrImmutableId is required")
	}

	ingestionEndpoint := os.Getenv("logsIngestionUrl")
	if ingestionEndpoint == "" {
		return nil, errors.New("logsIngestionUrl is required")
	}

	config := &Config{
		BloodhoundAPIKey:   bloodhoundApiKey,
		BloodhoundAPIKeyId: bloodhoundApiKeyId,
		BloodhoundDomain:   bloodhoundServer,
		IngestionEndpoint:  ingestionEndpoint,
		RuleId:             azureRuleId,
		MAX_UPLOAD_SIZE:    900000,
	}

	return config, nil
}
