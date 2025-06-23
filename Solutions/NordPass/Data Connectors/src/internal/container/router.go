package container

import (
	"github.com/labstack/echo/v4"
)

type Router interface {
	Register(routeGroup *echo.Group)
}
