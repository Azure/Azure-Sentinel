package client

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"time"

	"project/internal/activity"
	"project/internal/config"

	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

type HTTPClient struct {
	Client        *http.Client
	BaseURL       string
	Authorization string
}

func NewHTTPClient(cfg *config.Configuration) *HTTPClient {
	return &HTTPClient{
		Client:        &http.Client{Timeout: 10 * time.Second},
		BaseURL:       cfg.ActivityCredentials.Endpoint,
		Authorization: cfg.ActivityCredentials.Token,
	}
}

var (
	ErrMarshallRequestBody = "failed to marshal request body"
	ErrCreateNewRequest    = "failed to create new request"
	ErrNon200Code          = errors.New("received non-200 response code")
)

func (hc *HTTPClient) NewRequest(ctx echo.Context, method string, body interface{}) (*http.Request, error) {
	url := hc.BaseURL

	var reqBody []byte

	var err error

	// Check if body is already a byte slice; if so, use it directly, otherwise marshal
	switch v := body.(type) {
	case []byte:
		reqBody = v
	case nil:
		reqBody = nil
	default:
		reqBody, err = json.Marshal(body)

		if err != nil {
			return nil, errors.Wrap(err, ErrMarshallRequestBody)
		}
	}

	req, err := http.NewRequestWithContext(ctx.Request().Context(), method, url, bytes.NewBuffer(reqBody))

	if err != nil {
		return nil, errors.Wrap(err, ErrCreateNewRequest)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", hc.Authorization)
	req.Header.Set("X-Source", "MSSentinel")

	return req, nil
}

func (hc *HTTPClient) Do(req *http.Request) (*activity.APIResponse, error) {
	resp, err := hc.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, errors.Wrapf(ErrNon200Code, "status code: %d", resp.StatusCode)
	}

	var apiResp activity.APIResponse
	err = json.Unmarshal(body, &apiResp)

	if err != nil {
		return nil, err
	}

	return &apiResp, nil
}
