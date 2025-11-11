package bloodhound

import (
    "fmt"
    "io/ioutil"
    "net/http"
    "strings"
    "testing"

    "github.com/SpecterOps/bloodhound-go-sdk/sdk"
)

// MockTransport is a custom RoundTripper
type MockTransport struct {
    RoundTripFunc func(*http.Request) (*http.Response, error)
}

func (m *MockTransport) RoundTrip(req *http.Request) (*http.Response, error) {
    return m.RoundTripFunc(req)
}

func PtrString(s string) *string {
    return &s
}

func TestGetDomainMapping(t *testing.T) {
    mockedJSONResponse := `{
  "data": [
    {
      "type": "active-directory",
      "name": "WRAITH.CORP",
      "id": "S-1-5-21-3702535222-3822678775-2090119576",
      "collected": true,
      "impactValue": 12
    },
    {
      "type": "active-directory",
      "name": "CHILD.WRAITH.CORP",
      "id": "S-1-5-21-720005541-26010935-3948964793",
      "collected": false,
      "impactValue": 0
    },
    {
      "type": "active-directory",
      "name": "PHANTOM.CORP",
      "id": "S-1-5-21-2697957641-2271029196-387917394",
      "collected": true,
      "impactValue": 99
    },
    {
      "type": "active-directory",
      "name": "GHOST.CORP",
      "id": "S-1-5-21-2845847946-3451170323-4261139666",
      "collected": true,
      "impactValue": 0
    },
    {
      "type": "active-directory",
      "name": "REVENANT.CORP",
      "id": "S-1-5-21-1852147331-818484528-1557274963",
      "collected": false,
      "impactValue": 0
    },
    {
      "type": "azure",
      "name": "PHANTOM CORP",
      "id": "6C12B0B0-B2CC-4A73-8252-0B94BFCA2145",
      "collected": true,
      "impactValue": 56
    }
  ]
}`

    mockTransport := &MockTransport{
        RoundTripFunc: func(req *http.Request) (*http.Response, error) {
            if req.URL.Path == "/api/v2/available-domains" && req.Method == http.MethodGet {
				header := http.Header{
					"Content-Type": []string{"application/json"},
				}
                resp := &http.Response{
                    StatusCode: http.StatusOK,
                    Header:     header,
                    Body:       ioutil.NopCloser(strings.NewReader(mockedJSONResponse)),
                }
                return resp, nil
            }
            return nil, fmt.Errorf("unexpected request: %v %v", req.Method, req.URL)
        },
    }

    mockedHTTPClient := &http.Client{
        Transport: mockTransport,
    }

    serverURL := "http://mockedserver.com"

    bloodhoundClient, err := sdk.NewClientWithResponses(serverURL, sdk.WithHTTPClient(mockedHTTPClient))
    if err != nil {
        t.Fatalf("Failed to create client: %v", err)
    }

    mapping, err := GetDomainMapping(bloodhoundClient)
    if err != nil {
        t.Fatalf("GetDomainMapping failed: %v", err)
    }
	if len(*mapping) == 0 {
		t.Fatalf("GetDomainMapping failed: %v", err)
	}

}