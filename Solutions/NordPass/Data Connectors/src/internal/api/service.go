package api

import (
	"encoding/json"
	"project/internal/activity"
	"project/internal/client"
	"project/internal/config"

	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

type Service interface {
	FetchData(ctx echo.Context, lastTimestamp int64, page int) ([]activity.SentinelEvent, error)
}

const (
	PerPageDefault = 100
)

var (
	ErrMarshalRequestPayload = "failed to marshal request payload"
	ErrCreateRequest         = "failed to create request"
	ErrFetchData             = "failed to fetch data"
)

type RequestPayload struct {
	TimestampFrom int64 `json:"timestamp_from"`
	PerPage       int64 `json:"per_page"`
	Page          int   `json:"page"`
}

type service struct {
	HTTPClient *client.HTTPClient
}

func NewAPIService(cfg *config.Configuration) (Service, error) {
	httpClient := client.NewHTTPClient(cfg)

	return &service{
		HTTPClient: httpClient,
	}, nil
}

func (svc *service) FetchData(ctx echo.Context, lastTimestamp int64, page int) ([]activity.SentinelEvent, error) {
	payload := RequestPayload{
		TimestampFrom: lastTimestamp,
		PerPage:       PerPageDefault,
		Page:          page,
	}

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return nil, errors.Wrap(err, ErrMarshalRequestPayload)
	}

	req, err := svc.HTTPClient.NewRequest(ctx, "POST", payloadBytes)
	if err != nil {
		return nil, errors.Wrap(err, ErrCreateRequest)
	}

	apiResp, err := svc.HTTPClient.Do(req)
	if err != nil {
		return nil, errors.Wrap(err, ErrFetchData)
	}

	return activity.MapAPIResponseToMSSentinel(apiResp.Data, ctx), nil
}
