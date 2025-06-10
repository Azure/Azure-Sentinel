package apierrors

import "fmt"

type ParameterValidatorError struct {
	Field     string
	Validator string
}

func (e ParameterValidatorError) Error() string {
	return fmt.Sprintf("parameter %q failed validator %q", e.Field, e.Validator)
}

func (e ParameterValidatorError) Code() uint {
	return GenericValidatorError
}
