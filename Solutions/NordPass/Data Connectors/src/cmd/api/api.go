package main

import (
	"project/internal/api"
	"project/internal/apierrors"
	"project/internal/config"
	"project/internal/container"
	"project/internal/controller"
	"project/internal/router"
	"project/internal/sentinel"
	"project/internal/storage"
	"project/internal/utils"

	echoLib "bucket.digitalarsenal.net/gorphans/golang/libs/echo"
	"bucket.digitalarsenal.net/gorphans/golang/libs/logger/v2"

	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

type RootRouter struct {
	routers []container.Router
}

func NewRootRouter(
	activityRouter router.Router,
) *RootRouter {
	return &RootRouter{routers: []container.Router{
		activityRouter,
	}}
}

func (rootRouter *RootRouter) getRouteConfiguration() echoLib.RouteConfigurator {
	return func(engine *echo.Echo) {
		rootGroup := engine.Group("")

		for _, singleRouter := range rootRouter.routers {
			singleRouter.Register(rootGroup)
		}
	}
}

func main() {
	container.Register(
		storage.NewManager,
		sentinel.NewManager,
		controller.NewIngestController,
		router.NewRouter,
		api.NewAPIService,
		utils.NewCursorManager,

		NewRootRouter,
	)

	serviceContainer := container.Bootstrap()
	defer container.RecoverPanic(serviceContainer)

	if err := serviceContainer.Invoke(run); err != nil {
		panic(err)
	}
}

func run(cfg *config.Configuration, log logger.Logger, rootRouter *RootRouter, errorHandler *apierrors.APIErrorHandler) error {
	engine, err := echoLib.New(&echoLib.Config{
		Environment:  cfg.Environment,
		UnixSocket:   cfg.Server.UnixSocket,
		Router:       rootRouter.getRouteConfiguration(),
		ErrorHandler: errorHandler.ErrorHandler,
		Logger:       echoLib.WrapLogger(log),
		Port:         cfg.Server.Port,
	})
	if err != nil {
		return errors.Wrap(err, "initializing api")
	}

	engine.Echo().Logger.SetLevel(99)

	engine.Echo().HideBanner = true
	engine.Echo().HidePort = false

	return engine.Run()
}
