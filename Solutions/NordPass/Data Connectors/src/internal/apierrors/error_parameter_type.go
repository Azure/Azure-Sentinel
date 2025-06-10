package apierrors

import "fmt"

type InvalidParameterTypeError struct {
	Field        string
	Type         string
	RequiredType string
}

func (i InvalidParameterTypeError) Error() string {
	return fmt.Sprintf(
		"parameter %q value must be of type %q, %q given", i.Field, i.RequiredType, i.Type,
	)
}

func (i InvalidParameterTypeError) Code() uint {
	return InvalidParameterDataType
}
