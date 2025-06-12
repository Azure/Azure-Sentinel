package config

import (
	"github.com/eschao/config"
)

type Configuration struct {
	Environment string `cli:"environment" default:"production" env:"ENVIRONMENT"`

	Azure struct {
		StorageEndpoint string `cli:"storage-endpoint" env:"STORAGE_ENDPOINT"`
		LogsEndpoint    string `cli:"logs-endpoint"    env:"LOGS_ENDPOINT"`
		DCRUUID         string `cli:"dcr-uuid"         env:"DCR_UUID"`
		DCRStream       string `cli:"dcr-stream"       env:"DCR_STREAM"`
	}

	ActivityCredentials struct {
		Token    string `cli:"nordpass-token"        env:"NORDPASS_TOKEN"`
		Endpoint string `cli:"nordpass-endpoint-url" env:"NORDPASS_ENDPOINT_URL"`
	}

	Logger struct {
		Level string `cli:"level log level" default:"info" env:"LOGGER_LEVEL"`
	}

	Server struct {
		Port       string `cli:"port server port"        default:"8080"        env:"FUNCTIONS_CUSTOMHANDLER_PORT"`
		UnixSocket string `cli:"socket unix socket path" env:"API_UNIX_SOCKET"`
	}
}

func NewConfiguration() *Configuration {
	var configuration = &Configuration{}
	if err := config.ParseDefault(configuration); err != nil {
		panic(err)
	}

	if err := config.ParseEnv(configuration); err != nil {
		panic(err)
	}

	if err := config.ParseCli(configuration); err != nil {
		panic(err)
	}

	return configuration
}
