package apierrors

import (
	"errors"
	"fmt"
	"net/http"

	"bucket.digitalarsenal.net/gorphans/golang/libs/logger/v2"

	"github.com/labstack/echo/v4"
)

type APIErrorHandler struct {
	log logger.Logger
}

func NewAPIErrorHandler(log logger.Logger) *APIErrorHandler {
	return &APIErrorHandler{
		log: log,
	}
}

func (h *APIErrorHandler) ErrorHandler(err error, context echo.Context) {
	if context.Response().Committed {
		return
	}

	if handleErr := h.doHandling(err, context); handleErr != nil {
		context.Logger().Error(handleErr)
	}
}

func (h *APIErrorHandler) doHandling(err error, context echo.Context) error {
	var apiErr Error
	if errors.As(err, &apiErr) {
		return context.JSON(http.StatusBadRequest, echo.Map{
			"errors": Errors{apiErr},
		})
	}

	if errs := FormatValidationErrors(err); errs != nil {
		return context.JSON(http.StatusBadRequest, echo.Map{
			"errors": errs,
		})
	}

	var httpErr *echo.HTTPError
	if errors.As(err, &httpErr) {
		return context.NoContent(httpErr.Code)
	}

	if errorWithStack, ok := err.(ErrorStackTracer); ok {
		h.log.Logger().
			WithField(
				"stack_trace",
				fmt.Sprintf("%v", errorWithStack.StackTrace()),
			).Error(err)
	} else {
		h.log.Logger().Error(err)
	}

	return context.NoContent(http.StatusInternalServerError)
}
