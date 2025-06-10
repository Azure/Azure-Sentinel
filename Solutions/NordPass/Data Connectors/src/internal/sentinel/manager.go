package sentinel

import (
	"project/internal/config"

	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/monitor/ingestion/azlogs"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

type Manager interface {
	Upload(ctx echo.Context, payload []byte) error
}

type manager struct {
	client    *azlogs.Client
	dcrUUID   string
	dcrStream string
}

func NewManager(cfg *config.Configuration, credential *azidentity.DefaultAzureCredential) (Manager, error) {
	client, err := azlogs.NewClient(cfg.Azure.LogsEndpoint, credential, nil)
	if err != nil {
		return nil, err
	}

	return &manager{
		client:    client,
		dcrUUID:   cfg.Azure.DCRUUID,
		dcrStream: cfg.Azure.DCRStream,
	}, nil
}

func (m *manager) Upload(ctx echo.Context, payload []byte) error {
	_, err := m.client.Upload(ctx.Request().Context(), m.dcrUUID, m.dcrStream, payload, nil)

	if err != nil {
		return errors.Wrap(err, "failed to upload logs")
	}

	return nil
}
