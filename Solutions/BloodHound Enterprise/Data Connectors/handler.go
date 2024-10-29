package main

// go get github.com/Azure/azure-sdk-for-go/sdk/storage/azblob

import (
	"log"
	"net/http"
	"os"
	"encoding/json"
	"time"
	"fmt"
	"context"
	"bytes"
	"strings"

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
func SetTimeStamp(lastRun, azureWebJobsStorage, storageAccountContainer string) (string, error) {
	if lastRun == "" {
			lastRun = time.Now().UTC().Format(time.RFC3339Nano)
	}

	timestamp := Timestamp{LastRun: lastRun}
	data, err := json.Marshal(timestamp)
	if err != nil {
			return "", fmt.Errorf("failed to marshal timestamp: %v", err)
	}

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
			return SetTimeStamp("", azureWebJobsStorage, storageAccountContainer)
	}

	downloadedData := bytes.Buffer{}
	retryReader := get.NewRetryReader(context.TODO(), &azblob.RetryReaderOptions{})
	_, err = downloadedData.ReadFrom(retryReader)

	if err != nil {
		return "", fmt.Errorf("failed to read the blob data")
	}

	err = retryReader.Close()
	
	if err != nil {
		return "", fmt.Errorf("failed to close the reader")
	}

	var timestamp Timestamp
	err = json.Unmarshal(downloadedData.Bytes(), &timestamp)
	if err != nil {
			return "", fmt.Errorf("failed to unmarshal timestamp: %v", err)
	}

	return timestamp.LastRun, nil
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("Handler was called...\n")

	azureWebJobsStorage, ok := os.LookupEnv("AzureWebJobsStorage")
	if !ok {
		sendResponse(w, "500", "AzureWebJobsStorage env var could not be found")
		return
	}

	// check if we are running locally, if so, use the alternate ENV VAR
	// for the remote blob connection
	if strings.Contains(azureWebJobsStorage, "UseDevelopmentStorage") {
		azureWebJobsStorage, ok = os.LookupEnv("AzureWebJobsStorageExternal")
		if !ok {
			sendResponse(w, "500", "AzureWebJobsStorageExternal env var could not be found")
			return
		}
	}

	// get the last run timestamp
	lastRun, err := GetTimeStamp(azureWebJobsStorage, blobContainerName)

	if err != nil {
		sendResponse(w, "500", fmt.Sprintf("Error getting timestamp: %s", err.Error()))
		return
	} else {
		log.Printf("Last run timestamp: %s", lastRun)
	}

	//
	// do stuff here
  //

	// update the last run timestamp
	lastRun, err = SetTimeStamp("", azureWebJobsStorage, blobContainerName)

	if err != nil {
		sendResponse(w, "500", fmt.Sprintf("Error setting timestamp: %s", err.Error()))
		return
	} else {
		log.Printf("Updated run timestamp: %s", lastRun)
	}

	sendResponse(w, "200", "Successfully processed BloodHound Enterprise events.")
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
	listenAddr := ":8080"
	if val, ok := os.LookupEnv("FUNCTIONS_CUSTOMHANDLER_PORT"); ok {
		listenAddr = ":" + val
	}
	http.HandleFunc("/AzureFunctionBloodHoundEnterprise", helloHandler)
	log.Printf("About to listen on %s. Go to https://127.0.0.1%s/", listenAddr, listenAddr)
	log.Fatal(http.ListenAndServe(listenAddr, nil))
}
