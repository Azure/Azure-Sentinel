package container

import (
	stdLogger "log"

	"project/internal/apierrors"
	"project/internal/config"

	"bucket.digitalarsenal.net/gorphans/golang/libs/logger/v2"

	"go.uber.org/dig"
)

var constructors = []interface{}{
	config.NewConfiguration,
	newLogger,
	newClock,
	newAzureCredential,
	apierrors.NewAPIErrorHandler,
}

func Register(constructs ...interface{}) {
	constructors = append(constructors, constructs...)
}

func Bootstrap() *dig.Container {
	container := dig.New()

	for _, constructor := range constructors {
		if err := container.Provide(constructor); err != nil {
			panic(err)
		}
	}

	return container
}

func RecoverPanic(digContainer *dig.Container) {
	if r := recover(); r != nil {
		err := digContainer.Invoke(func(log logger.Logger) {
			log.Error(r)
		})
		if err != nil {
			stdLogger.Println(r)
			stdLogger.Fatal("Cannot init logger")
		}
	}
}
