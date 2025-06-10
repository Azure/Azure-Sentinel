package router

import (
	"project/internal/container"
	"project/internal/controller"

	"github.com/labstack/echo/v4"
)

type Router interface {
	container.Router
}

type router struct {
	IngestController *controller.IngestController
}

func NewRouter(
	ingestController *controller.IngestController,
) Router {
	return &router{
		IngestController: ingestController,
	}
}

func (r *router) Register(routeGroup *echo.Group) {
	routeGroup.POST("/activities-ingest", r.IngestController.Ingest)
}
