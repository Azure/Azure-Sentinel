package container

import (
	"os"
	"project/internal/config"

	"bucket.digitalarsenal.net/gorphans/golang/libs/logger/v2"
)

func newLogger(cfg *config.Configuration) (logger.Logger, error) {
	options := logger.Options{
		LogLevel: cfg.Logger.Level,
	}

	loggerInstance := logger.Init(&options)
	loggerInstance.Logger().SetOutput(os.Stdout)

	return loggerInstance, nil
}
