package container

import "github.com/Azure/azure-sdk-for-go/sdk/azidentity"

func newAzureCredential() (*azidentity.DefaultAzureCredential, error) {
	return azidentity.NewDefaultAzureCredential(nil)
}
