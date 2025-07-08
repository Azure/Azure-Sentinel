package utils

import (
	"bytes"
	"encoding/binary"
	"time"

	"project/internal/storage"

	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

const (
	ContainerName                = "nordpass-function-container"
	BlobName                     = "nordpass-activities-cursor"
	DefaultHistoricalMaxDataDays = -7
)

type Cursor interface {
	Get(ctx echo.Context) (int64, error)
	Store(ctx echo.Context, timestamp int64) error
}

type cursor struct {
	Storage storage.Manager
}

func NewCursorManager(storageManager storage.Manager) Cursor {
	return &cursor{
		Storage: storageManager,
	}
}

func (c *cursor) Get(ctx echo.Context) (int64, error) {
	// Create the container
	ctx.Logger().Printf("Creating a container named %s", ContainerName)

	if err := c.Storage.CreateContainer(ctx, ContainerName); err != nil {
		return 0, err
	}

	byteCursor := make([]byte, 8)

	downloadBlob, _ := c.Storage.DownloadBlob(ctx, ContainerName, BlobName, byteCursor)

	if downloadBlob == 0 {
		ctx.Logger().Printf("Blob is empty. Generating activities cursor.")

		return time.Now().AddDate(0, 0, DefaultHistoricalMaxDataDays).Unix(), nil
	}

	storageCursor := int64(binary.BigEndian.Uint64(byteCursor)) // #nosec G115: ignore integer overflow warning

	ctx.Logger().Printf("Downloaded coursor %d", storageCursor)

	return storageCursor, nil
}

func (c *cursor) Store(ctx echo.Context, timestamp int64) error {
	var buf bytes.Buffer
	err := binary.Write(&buf, binary.BigEndian, timestamp)

	if err != nil {
		return errors.Wrap(err, "Error writing binary")
	}

	ctx.Logger().Printf("Uploading a blob named %s\n", BlobName)

	if err := c.Storage.UploadBlob(ctx, ContainerName, BlobName, buf.Bytes()); err != nil {
		return err
	}

	ctx.Logger().Printf("Uploaded!")

	return nil
}
