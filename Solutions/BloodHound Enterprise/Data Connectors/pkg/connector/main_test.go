package connector

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"testing"
	"time"

	"github.com/SpecterOps/bloodhound-go-sdk/sdk"

	. "function/pkg/bloodhound"
	. "function/pkg/model"
)

// Testing some time formatting here
func TestTimeFormatting(testing *testing.T) {
	t := time.Now()
	var s = t.Format("2006-01-02T15:04:05.000Z")
	testing.Logf("Explicit format %s\n", s)
	s = t.Format(time.RFC3339Nano)
	testing.Logf("RFC3339Nano format %s\n", s)
	s = t.UTC().Format(time.RFC3339Nano)
	testing.Logf("UTC RFC3339Nano format %s\n", s)
	testing.Fatalf("")
}

func TestCreateBatches(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	jsonRecords, _ := json.Marshal(testRecords)
	t.Logf("size of record list %d", len(jsonRecords))

	batches, err := CreateJsonBatches(testRecords, 1000000)
	if err != nil {
		t.Fatalf("Error creating batches %v", err)
	}
	var c = 0
	for _, batch := range batches {
		c += len(batch)
	}
	if c != len(testRecords) {
		t.Fatalf("Size of batches %d", len(batches))
		t.Fail()
	}
	type args struct {
		records       []BloodhoundEnterpriseData
		maxUploadSize int64
	}
	if false {
		t.Fail()
	}
}



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

func TestRecordsTooBig(t *testing.T) {
	testRecord := BloodhoundEnterpriseData{
		EventType:    "a;lksdjfa;lskdjf;alskdjf;alsdkjf;alsdkjf;alskdjf;alskdjfa;lsdkjf;alskjdfalskjdfalksdjf",
		EventDetails: "a;lskdfja;sldkfja;sldkfja;sldkfja;lsdkjfa;sldkfja;lsdkjfa;lsdkjfa;lskdjfalskdfjaldkjf",
	}
	var testRecords = make([]BloodhoundEnterpriseData, 50000)
	for i := range 50000 {
		testRecords[i] = testRecord
	}

	maxRecordSize := int64(10)
	_, err := CreateJsonBatches(testRecords, maxRecordSize)
	if err == nil {
		t.Fatal("Error creating batches should fail when single record not fit max record size ")
	} 
}

func TestGetTier0Data(t *testing.T) {
	doomainMockedJSONResponse := `{
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

	assetgroup1MockedJSONResponse := `{
  "count": 169,
  "limit": 100,
  "skip": 0,
  "data": {
    "members": [
      {
        "asset_group_id": 1,
        "object_id": "CN=ENTERPRISE ADMINS,OU=GROUPS,OU=TIER0,DC=PHANTOM,DC=CORP",
        "primary_kind": "Base",
        "kinds": [
          "Base"
        ],
        "environment_id": "",
        "environment_kind": "",
        "name": "",
        "custom_member": false
      },
      {
        "asset_group_id": 1,
        "object_id": "D2C3BD7E-7CEC-4905-B22C-B657C026F638",
        "primary_kind": "AZServicePrincipal",
        "kinds": [
          "AZServicePrincipal",
          "AZBase"
        ],
        "environment_id": "6C12B0B0-B2CC-4A73-8252-0B94BFCA2145",
        "environment_kind": "AZTenant",
        "name": "48AADCF6-PRIVILEGED ROLE ADMINISTRATOR@PHANTOMCORP",
        "custom_member": false
      },
      {
        "asset_group_id": 1,
        "object_id": "S-1-5-21-3702535222-3822678775-2090119576-519",
        "primary_kind": "Group",
        "kinds": [
          "Base",
          "Group"
        ],
        "environment_id": "S-1-5-21-3702535222-3822678775-2090119576",
        "environment_kind": "Domain",
        "name": "ENTERPRISE ADMINS@WRAITH.CORP",
        "custom_member": false
      },
      {
        "asset_group_id": 1,
        "object_id": "S-1-5-21-1852147331-818484528-1557274963",
        "primary_kind": "Domain",
        "kinds": [
          "Domain",
          "Base"
        ],
        "environment_id": "",
        "environment_kind": "",
        "name": "REVENANT.CORP",
        "custom_member": false
	 },
	       {
        "asset_group_id": 1,
        "object_id": "S-1-5-21-1852147331-818484528-1557274963",
        "primary_kind": "Domain",
        "kinds": [
          "Domain",
          "Base"
        ],
        "environment_id": "",
        "environment_kind": "",
        "name": "REVENANT.CORP",
        "custom_member": false
      },
      {
        "asset_group_id": 1,
        "object_id": "315C2B07-E593-474F-BBDC-F3CA5EC52813",
        "primary_kind": "AZApp",
        "kinds": [
          "AZApp",
          "AZBase"
        ],
        "environment_id": "6C12B0B0-B2CC-4A73-8252-0B94BFCA2145",
        "environment_kind": "AZTenant",
        "name": "47795D55-PRIVILEGED ROLE ADMINISTRATOR@PHANTOMCORP.ONMICROSOFT.COM",
        "custom_member": false
      },
      {
        "asset_group_id": 1,
        "object_id": "C68C6ED4-652F-4D39-A9A4-DBDA72B09D50",
        "primary_kind": "AZApp",
        "kinds": [
          "AZApp",
          "AZBase"
        ],
        "environment_id": "6C12B0B0-B2CC-4A73-8252-0B94BFCA2145",
        "environment_kind": "AZTenant",
        "name": "48AADCF6-PRIVILEGED ROLE ADMINISTRATOR@PHANTOMCORP.ONMICROSOFT.COM",
        "custom_member": false
      }
    ]
  }
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
					Body:       ioutil.NopCloser(strings.NewReader(doomainMockedJSONResponse)),
				}
				return resp, nil
			} else if req.URL.Path == "/api/v2/asset-groups/1/members" && req.Method == http.MethodGet {
				header := http.Header{
					"Content-Type": []string{"application/json"},
				}
				resp := &http.Response{
					StatusCode: http.StatusOK,
					Header:     header,
					Body:       ioutil.NopCloser(strings.NewReader(assetgroup1MockedJSONResponse)),
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
		t.Fatalf("Failed to get domain mapping: %v", err)

	}

	tierZeroGroupmembers, err := GetTierZeroPrincipals(bloodhoundClient)
	bheRecords, err := transformTierZeroPrincipal(tierZeroGroupmembers, *mapping)

	if err != nil {
		t.Fatalf("Failed to create client: %v", err)
	}
	if len(tierZeroGroupmembers) != 7 {
		t.Fatalf("Expected 1 record, got %d", len(bheRecords))
	}
	if len(bheRecords) != 6 {
		t.Fatalf("Expected 1 record, got %d", len(bheRecords))
	}
	if bheRecords[0].DataType != "t0_export" {
		t.Fatalf("Expected data_type to be t0_export, got %s", bheRecords[0].DataType)
	}

}
