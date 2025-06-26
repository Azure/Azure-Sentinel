package controller

import (
	"encoding/json"
	"net/http"
	"project/internal/api"
	"project/internal/sentinel"
	"project/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
)

type IngestController struct {
	logsStore     sentinel.Manager
	apiService    api.Service
	cursorManager utils.Cursor
}

func NewIngestController(logsStore sentinel.Manager, apiService api.Service, cursorManager utils.Cursor) *IngestController {
	return &IngestController{
		logsStore:     logsStore,
		apiService:    apiService,
		cursorManager: cursorManager,
	}
}

func (c *IngestController) Ingest(ctx echo.Context) error {
	ctx.Logger().Printf("Ingest request called...")

	cursor, err := c.cursorManager.Get(ctx)
	if err != nil {
		return err
	}

	page := 1

	for {
		ctx.Logger().Printf("Page: %d", page)
		activities, err := c.apiService.FetchData(ctx, cursor, page)

		if err != nil {
			ctx.Logger().Printf("error fetching activities: %v\n", err)

			return err
		}

		ctx.Logger().Printf("Uploading logs: %+v", activities)

		if len(activities) == 0 {
			ctx.Logger().Printf("No more activities")

			break
		}

		logs, err := json.Marshal(activities)
		if err != nil {
			ctx.Logger().Printf("Failed to marshal logs: %v", err)

			return err
		}

		ctx.Logger().Printf("Uploading logs: %s", logs)

		if err := c.logsStore.Upload(ctx, logs); err != nil {
			return err
		}

		page++
	}

	ctx.Logger().Printf("Upload done!")

	cursor = time.Now().Unix()
	err = c.cursorManager.Store(ctx, cursor)

	if err != nil {
		return err
	}

	ctx.Logger().Printf("Cursor updated! Value: %d", cursor)

	return ctx.JSON(http.StatusOK, echo.Map{"status": "success"})
}
