package controller

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"project/internal/activity"
	"project/internal/utils"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"project/internal/api"
	"project/internal/sentinel"
)

func TestIngestController_Ingest(t *testing.T) {
	engine := echo.New()
	request := httptest.NewRequest(http.MethodPost, "/activities-ingest", nil)
	request.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)

	sentinelMock := sentinel.NewMockManager(t)
	sentinelMock.On(
		"Upload",
		mock.AnythingOfType("*echo.context"),
		mock.AnythingOfType("[]uint8"),
	).Return(nil).Once()

	apiServiceMock := api.NewMockService(t)
	apiServiceMock.On(
		"FetchData",
		mock.AnythingOfType("*echo.context"),
		mock.AnythingOfType("int64"),
		1,
	).Return([]activity.SentinelEvent{
		{
			Action: "user_invited",
			Type:   "invites",
			Metadata: map[string]interface{}{
				"emails": []string{"test@gmail.com"},
				"msp": map[string]interface{}{
					"user_email": "denys.kulygin+mspowner@nordsec.com",
					"user_role":  "admin",
					"user_uuid":  "de555f53-5a44-47cd-a3b6-946c8a97b847",
				},
			},
			OrganizationUUID: "101b4232-0688-4599-bca8-4636c91cd687",
			EventTime:        1738255186,
			UserEmail:        "denys.kulygin+mspowner@nordsec.com",
			UserUUID:         "de555f53-5a44-47cd-a3b6-946c8a97b847",
		},
	}, nil).Once()

	apiServiceMock.On(
		"FetchData",
		mock.AnythingOfType("*echo.context"),
		mock.AnythingOfType("int64"),
		2,
	).Return([]activity.SentinelEvent{}, nil).Once()

	cursorManager := utils.NewMockCursor(t)
	cursorManager.On(
		"Get",
		mock.AnythingOfType("*echo.context"),
	).Return(int64(1738848413), nil).Once()

	cursorManager.On(
		"Store",
		mock.AnythingOfType("*echo.context"),
		mock.AnythingOfType("int64"),
	).Return(nil).Once()

	responseRecorder := httptest.NewRecorder()
	context := engine.NewContext(request, responseRecorder)

	controller := NewIngestController(sentinelMock, apiServiceMock, cursorManager)
	err := controller.Ingest(context)

	expectedResponseBody := fmt.Sprintln(`{"status":"success"}`)

	require.NoError(t, err)
	require.Equal(t, http.StatusOK, responseRecorder.Code)
	require.Equal(t, expectedResponseBody, responseRecorder.Body.String())
}
