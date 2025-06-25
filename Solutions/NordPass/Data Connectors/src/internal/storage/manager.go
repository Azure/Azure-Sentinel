package storage

import (
	"project/internal/config"

	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/bloberror"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

type Manager interface {
	CreateContainer(ctx echo.Context, name string) error
	UploadBlob(ctx echo.Context, containerName, name string, data []byte) error
	DownloadBlob(ctx echo.Context, containerName, name string, data []byte) (int64, error)
}

type manager struct {
	client *azblob.Client
}

func NewManager(cfg *config.Configuration, credential *azidentity.DefaultAzureCredential) (Manager, error) {
	client, err := azblob.NewClient(cfg.Azure.StorageEndpoint, credential, nil)
	if err != nil {
		return nil, err
	}

	return &manager{
		client: client,
	}, nil
}

func (m *manager) CreateContainer(ctx echo.Context, name string) error {
	_, err := m.client.CreateContainer(ctx.Request().Context(), name, nil)
	if err != nil {
		if !bloberror.HasCode(err, bloberror.ContainerAlreadyExists) {
			return errors.Wrap(err, "failed to create container")
		}
	}

	return nil
}

func (m *manager) UploadBlob(ctx echo.Context, containerName, name string, data []byte) error {
	_, err := m.client.UploadBuffer(ctx.Request().Context(), containerName, name, data, nil)
	if err != nil {
		return errors.Wrap(err, "failed to upload blob")
	}

	return nil
}

func (m *manager) DownloadBlob(ctx echo.Context, containerName, name string, data []byte) (int64, error) {
	buffer, err := m.client.DownloadBuffer(ctx.Request().Context(), containerName, name, data, nil)
	if err != nil {
		return 0, errors.Wrap(err, "failed to download blob")
	}

	return buffer, nil
}
