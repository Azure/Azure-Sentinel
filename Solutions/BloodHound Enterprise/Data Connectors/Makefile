.PHONY: build clean package

# Packaging variables
FUNCTION_NAME := function
BINARY_NAME := function
ZIP_NAME := bhe-funcapp.zip

# Go build variables
GOOS := linux
GOARCH := amd64

# Package the function app
package: build
	@echo "Packaging"
	rm -f $(ZIP_NAME)
	zip -r $(ZIP_NAME) AzureFunctionBloodHoundEnterprise/ AzureFunctionBloodHoundEnterprise/function.json function host.json
	@echo "Packaging complete"

# Build binary
build: clean
	@echo "Building $(BINARY_NAME)"
	GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o $(BINARY_NAME) 

# Clean up build artifacts
clean:
	@echo "Clean"
	go clean
	rm -f $(ZIP_NAME)


