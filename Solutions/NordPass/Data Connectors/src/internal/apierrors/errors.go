package apierrors

import (
	"encoding/json"

	pkgErrors "github.com/pkg/errors"
)

const (
	InvalidRequestBody       uint = 16001
	InvalidParameterDataType uint = 16002
	GenericValidatorError    uint = 16006
)

type ErrorStackTracer interface {
	StackTrace() pkgErrors.StackTrace
}

type Error interface {
	error
	Code() uint
}

type Errors []Error

func (e Errors) MarshalJSON() ([]byte, error) {
	errors := make([]map[string]interface{}, 0, len(e))

	for _, err := range e {
		errors = append(errors, map[string]interface{}{
			"code":    err.Code(),
			"message": err.Error(),
		})
	}

	if len(errors) == 1 {
		return json.Marshal(errors[0])
	}

	return json.Marshal(errors)
}
