package azure

import (
	"github.com/Azure/azure-sdk-for-go/sdk/azcore"
	"github.com/Azure/azure-sdk-for-go/sdk/monitor/ingestion/azlogs"
)

func NewClient(endpoint string, credentials azcore.TokenCredential, opens *azlogs.ClientOptions) (*azlogs.Client, error) {

	client, err := azlogs.NewClient(endpoint, credentials, nil)
	if err != nil {
		return nil, err
	}

	return client, nil
}
