package apierrors

type InvalidBodyError struct{}

func (InvalidBodyError) Error() string {
	return "invalid request body"
}

func (InvalidBodyError) Code() uint {
	return InvalidRequestBody
}
