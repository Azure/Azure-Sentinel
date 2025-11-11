package control

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func callbackFunctionHandler(callback func() error) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		go func() {
			err := callback()
			if err != nil {
				w.Header().Set("Error-Msg", err.Error())
			}
		}()

		w.WriteHeader(http.StatusOK)
	}
}

func shutdownHandler(srv *http.Server) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Print("Shutting down control http server ...")
		w.WriteHeader(http.StatusOK)
		err := srv.Shutdown(context.Background())
		if err != nil {
			return
		}
	}
}

func StartHttpControl(listenAddr string, path string, callback func() error) error {
	if path == "" || path == "/" {
		return fmt.Errorf("path can't be empty")
	}
	if path[0] != '/' {
		path = "/" + path
	}

	router := mux.NewRouter()

	srv := &http.Server{
		Addr:    listenAddr,
		Handler: router,
	}

	router.HandleFunc(path, callbackFunctionHandler(callback))
	router.HandleFunc("/shutdown", shutdownHandler(srv))
	return srv.ListenAndServe()
}
