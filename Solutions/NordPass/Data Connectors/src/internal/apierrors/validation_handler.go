package apierrors

import (
	"encoding/json"
	"io"
	"strings"

	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

func FormatValidationErrors(err error) Errors {
	var validationErrs validator.ValidationErrors
	formattedErrors := make(Errors, 0, len(validationErrs))

	if errors.As(err, &validationErrs) {
		for _, validationErr := range validationErrs {
			if formattedErr := resolveValidationError(validationErr); formattedErr != nil {
				formattedErrors = append(formattedErrors, formattedErr)
			}
		}

		return formattedErrors
	}

	if errors.Is(err, io.EOF) || errors.Is(err, io.ErrUnexpectedEOF) {
		return Errors{InvalidBodyError{}}
	}

	var httpErr *echo.HTTPError
	if errors.As(err, &httpErr) && httpErr.Internal != nil {
		jsonErrors := resolveJSONErrors(httpErr.Internal)
		if jsonErrors != nil {
			return jsonErrors
		}
	}

	return nil
}

func resolveValidationError(err validator.FieldError) Error {
	field := removeNamespaceRoot(err.Namespace())

	return ParameterValidatorError{
		Field:     field,
		Validator: err.Tag(),
	}
}

func resolveJSONErrors(err error) Errors {
	//nolint:errorlint // no wrapped errors will be here
	switch err := err.(type) {
	case *json.SyntaxError:
		return Errors{
			InvalidBodyError{},
		}
	case *json.UnmarshalTypeError:
		return Errors{
			InvalidParameterTypeError{
				Field:        err.Field,
				Type:         err.Type.String(),
				RequiredType: err.Value,
			},
		}
	}

	return nil
}

func removeNamespaceRoot(namespace string) string {
	separatorIndex := strings.Index(namespace, ".")

	return strings.ToLower(namespace[separatorIndex+1:])
}
