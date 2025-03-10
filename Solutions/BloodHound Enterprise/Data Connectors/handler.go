package main

// go get github.com/Azure/azure-sdk-for-go/sdk/storage/azblob

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	. "function/pkg/bloodhound"
	"function/pkg/connector"

	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/monitor/ingestion/azlogs"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
)

const blobContainerName string = "cursors"
const blobName string = "cursor.json"

// HTTPResponse is the expected outgoing payload to a HTTP Trigger
// to function host.
// very helpful article: https://www.redeploy.com/post/serverless-with-go-and-azure-functions
type HTTPResponse struct {
	Outputs struct {
		Res struct {
			Body       string `json:"body"`
			StatusCode string `json:"statusCode"`
		} `json:"res"`
	}
	Logs        []string
	ReturnValue interface{}
}

// defines the cursor JSON content
type Timestamp struct {
	LastRun string `json:"lastRun"`
}

// this stores the current run timestamp in an Azure storage blob
func SetTimeStamp(lastRun string, azureWebJobsStorage, storageAccountContainer string) (string, error) {
	timestamp := Timestamp{LastRun: lastRun}
	data, err := json.Marshal(timestamp)
	if err != nil {
		return "", fmt.Errorf("failed to marshal timestamp: %v", err)
	}

	log.Printf("azureWEbJobsStorage connection string %s", azureWebJobsStorage)
	serviceClient, err := azblob.NewClientFromConnectionString(azureWebJobsStorage, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create service client: %v", err)
	}

	_, err = serviceClient.UploadBuffer(context.TODO(), storageAccountContainer, blobName, data, &azblob.UploadBufferOptions{})

	if err != nil {
		return "", fmt.Errorf("failed to upload blob: %v", err)
	}

	return lastRun, nil
}

// gets the current run timestamp in an Azure storage blob,
// otherwise if no blob found will create a new one for the current time
func GetTimeStamp(azureWebJobsStorage, storageAccountContainer string) (string, error) {
	serviceClient, err := azblob.NewClientFromConnectionString(azureWebJobsStorage, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create service client: %v", err)
	}

	get, err := serviceClient.DownloadStream(context.TODO(), storageAccountContainer, blobName, nil)

	if err != nil {
		log.Printf("GetTimeStamp about to return empty lastRunTime")
		return "", nil
	}

	downloadedData := bytes.Buffer{}
	retryReader := get.NewRetryReader(context.TODO(), &azblob.RetryReaderOptions{})
	_, err = downloadedData.ReadFrom(retryReader)

	if err != nil {
		log.Printf("gettimestamp readfrom err %v", err)
		return "", fmt.Errorf("failed to read the blob data")
	}

	err = retryReader.Close()
	if err != nil {
		log.Printf("gettimestamp close err %v", err)
		return "", fmt.Errorf("failed to close the reader")
	}

	var timestamp Timestamp
	bytes := downloadedData.Bytes()
	err = json.Unmarshal(bytes, &timestamp)
	if err != nil {
		log.Printf("gettimestamp unmarshal err %v", err)
		return "", fmt.Errorf("failed to unmarshal timestamp: %v", err)
	}

	log.Printf("gettimestamp returning %v", timestamp.LastRun)
	return timestamp.LastRun, nil
}

func sendError(w http.ResponseWriter, error string) {
	sendResponse(w, "500", error)
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("Handler was called...\n")

	config, err := connector.LoadConfigFromEnv() // TODO
	if err != nil {
		sendError(w, fmt.Sprintf("Configuration initialization error: %v", err))
		return
	}

	// Initialize the Bloodhound Client connection
	// TODO: have our hown bloodhound client type that contains key, domain etc.
	bhClient, err := InitializeBloodhoundClient(config.BloodhoundAPIKey,
		config.BloodhoundAPIKeyId,
		config.BloodhoundDomain)
	if err != nil {
		sendError(w, fmt.Sprintf("Bloodhound client initialization error: %v key: %s, id: %s", err, config.BloodhoundAPIKey, config.BloodhoundAPIKeyId))
		return
	}

	// This tries multiple ways to authenticate.
	cred, err := azidentity.NewDefaultAzureCredential(nil)
	if err != nil {
		sendError(w, fmt.Sprintf("Failed to create credential: %v", err))
		return
	}

	// Initialize the Azure Monitor Logs client
	azureClient, err := azlogs.NewClient(config.IngestionEndpoint, cred, nil)
	if err != nil {
		sendError(w, fmt.Sprintf("Azure Monitor client initialization error: %v", err))
		return
	}

	azureWebJobsStorage, ok := os.LookupEnv("AzureWebJobsStorage")
	if !ok {
		sendError(w, "AzureWebJobsStorage env var could not be found")
		return
	}
	
	// check if we are running locally, if so, use the alternate ENV VAR
	// for the remote blob connection
	if strings.Contains(azureWebJobsStorage, "UseDevelopmentStorage") {
		azureWebJobsStorage, ok = os.LookupEnv("AzureWebJobsStorageExternal")
		if !ok {
			sendError(w, "AzureWebJobsStorageExternal env var could not be found")
			return
		}
	}

	// get the last run timestamp
	lastRun, err := GetTimeStamp(azureWebJobsStorage, blobContainerName)
	log.Printf("We are getting lastRun '%s'", lastRun)
	if err != nil {
		log.Printf("error gettimestamp %v", err)
		sendError(w, fmt.Sprintf("Error getting timestamp: %s", err.Error()))
		return
	}

	var lastRunTime *time.Time = nil
	if lastRun != "" {
		t, err := time.Parse(time.RFC3339Nano, lastRun)
		if err != nil {
			sendError(w, fmt.Sprintf("Error parsing timestamp: %s error: %v", lastRun, err.Error()))
		}
		lastRunTime = &t
	}

	//
	// do stuff here
	//
	logs, err := connector.UploadLogsCallback(bhClient, config.BloodhoundDomain, lastRunTime, azureClient, config.RuleId, config.MAX_UPLOAD_SIZE)
	if err != nil {
		sendError(w, fmt.Sprintf("Error in connector: %s logs: %v key: %s keyId: %s", err.Error(), logs, config.BloodhoundAPIKey, config.BloodhoundAPIKeyId))
		return
	}

	// update the last run timestamp
	formattedTime := time.Now().UTC().Format(time.RFC3339Nano)
	lastRun, err = SetTimeStamp(formattedTime, azureWebJobsStorage, blobContainerName)
	if err != nil {
		sendError(w, fmt.Sprintf("Error setting timestamp: %s", err.Error()))
		return
	} else {
		log.Printf("Updated run timestamp: %s", lastRun)
	}

	sendResponse(w, "200", fmt.Sprintf("Successfully processed BloodHound Enterprise events.  logs: %v", logs))
}

func sendResponse(w http.ResponseWriter, statusCode string, message string) {
	// create the response
	response := HTTPResponse{}
	response.Outputs.Res.StatusCode = statusCode
	response.Logs = []string{message}
	res, err := json.Marshal(response)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(res)
}

func main() {
	os.Setenv("TZ", "UTC")
	listenAddr := ":8080"
	if val, ok := os.LookupEnv("FUNCTIONS_CUSTOMHANDLER_PORT"); ok {
		listenAddr = ":" + val
	}

	http.HandleFunc("/AzureFunctionBloodHoundEnterprise", helloHandler)
	log.Printf("About to listen on %s. Go to https://127.0.0.1%s/", listenAddr, listenAddr)
	log.Fatal(http.ListenAndServe(listenAddr, nil))
}
