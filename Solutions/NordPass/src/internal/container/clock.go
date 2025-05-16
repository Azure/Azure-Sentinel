package container

import "time"

type Clock interface {
	Now() time.Time
}

type clock struct {
}

func newClock() Clock {
	return &clock{}
}

func (c *clock) Now() time.Time {
	return time.Now()
}
