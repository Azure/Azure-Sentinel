package connector

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"strings"
	"time"

	//	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"function/pkg/bloodhound"
	. "function/pkg/model"

	"github.com/Azure/azure-sdk-for-go/sdk/monitor/ingestion/azlogs"
	"github.com/SpecterOps/bloodhound-go-sdk/sdk"
)

// TODO: hax
type FromPrincipalProps struct {
	Collected         bool      `json:"collected"`
	Distinguishedname string    `json:"distinguishedname"`
	Domain            string    `json:"domain"`
	Domainsid         string    `json:"domainsid"`
	Functionallevel   string    `json:"functionallevel"`
	Isaclprotected    bool      `json:"isaclprotected"`
	Lastseen          time.Time `json:"lastseen"`
	Name              string    `json:"name"`
	Objectid          string    `json:"objectid"`
	SystemTags        string    `json:"system_tags"`
	Whencreated       int       `json:"whencreated"`
}
type ToPrincipalProps struct {
	Admincount        bool      `json:"admincount"`
	Description       string    `json:"description"`
	Distinguishedname string    `json:"distinguishedname"`
	Domain            string    `json:"domain"`
	Domainsid         string    `json:"domainsid"`
	Isaclprotected    bool      `json:"isaclprotected"`
	Lastseen          time.Time `json:"lastseen"`
	Name              string    `json:"name"`
	Objectid          string    `json:"objectid"`
	Samaccountname    string    `json:"samaccountname"`
	Whencreated       int       `json:"whencreated"`
}
type Props struct {
	Distinguishedname *string `json:"distinguishedname,omitempty"`
	Name              *string `json:"name,omitempty"`
	Objectid          *string `json:"objectid,omitempty"`
	SystemTags        *string `json:"system_tags,omitempty"`
	Type              *string `json:"type,omitempty"`
}

type AttackFindingProperties struct {
	ToPrincipalProps   *ToPrincipalProps
	FromPrincipalProps *FromPrincipalProps
	Props              *Props
}

type MyModelListFinding struct {
	DomainSID     *string                 `json:"DomainSID,omitempty"`
	Finding       *string                 `json:"Finding,omitempty"`
	Principal     *string                 `json:"Principal,omitempty"`
	PrincipalKind *string                 `json:"PrincipalKind,omitempty"`
	Props         *map[string]interface{} `json:"Props,omitempty"`
	AcceptedUntil *time.Time              `json:"accepted_until,omitempty"`
	CreatedAt     *time.Time              `json:"created_at,omitempty"`
	DeletedAt     *sdk.NullTime           `json:"deleted_at,omitempty"`
	// DeletedAt *time.Time `json:"deleted_at,omitempty"`

	// Id This is the unique identifier for this object.
	Id        *int32     `json:"id,omitempty"`
	UpdatedAt *time.Time `json:"updated_at,omitempty"`
}

type MyModelRelationshipFinding struct {
	AcceptedUntil *time.Time `json:"AcceptedUntil,omitempty"`
	//	ComboGraphRelationID *sdk.NullInt64          `json:"ComboGraphRelationID,omitempty"`
	ComboGraphRelationID *int64                  `json:"ComboGraphRelationID,omitempty"`
	DomainSID            *string                 `json:"DomainSID,omitempty"`
	Finding              *string                 `json:"Finding,omitempty"`
	FromPrincipal        *string                 `json:"FromPrincipal,omitempty"`
	FromPrincipalKind    *string                 `json:"FromPrincipalKind,omitempty"`
	FromPrincipalProps   *map[string]interface{} `json:"FromPrincipalProps,omitempty"`
	PrincipalHash        *string                 `json:"PrincipalHash,omitempty"`
	RelProps             *map[string]interface{} `json:"RelProps,omitempty"`
	ToPrincipal          *string                 `json:"ToPrincipal,omitempty"`
	ToPrincipalKind      *string                 `json:"ToPrincipalKind,omitempty"`
	ToPrincipalProps     *map[string]interface{} `json:"ToPrincipalProps,omitempty"`
	CreatedAt            *time.Time              `json:"created_at,omitempty"`
	DeletedAt            *sdk.NullTime           `json:"deleted_at,omitempty"`
	// DeletedAtV *sdk.NullTime `json:"deleted_at_v,omitempty"`
	// Id This is the unique identifier for this object.
	Id        *int32     `json:"id,omitempty"`
	UpdatedAt *time.Time `json:"updated_at,omitempty"`
}

func transformPostureData(domainMap *map[string]sdk.ModelDomainSelector, postureStat *sdk.ModelRiskPostureStat) (BloodhoundEnterpriseData, error) {
	// TODO: Validate and return error
	selector, ok := (*domainMap)[*postureStat.DomainSid]
	if !ok {
		return BloodhoundEnterpriseData{}, fmt.Errorf("domain id %s not found in domain selector", *postureStat.DomainSid)
	}

	bhe_sentinel_data := BloodhoundEnterpriseData{
		DataType:      "posture",
		TimeGenerated: *postureStat.CreatedAt,
		DomainSID:     *postureStat.DomainSid,
		DomainName:    *selector.Name,
		DomainType:    *selector.Type,
		DomainID:      *selector.Id,
		ExposureIndex: math.Round(*postureStat.ExposureIndex * 100),
		FindingCount:  float64(*postureStat.CriticalRiskCount), // TODO: wrong
		TierZeroCount: float64(*postureStat.TierZeroCount),     // TODO: wrong
		UpdatedAt:     *postureStat.UpdatedAt,
		CreatedAt:     *postureStat.CreatedAt,
		DeletedAt:     postureStat.DeletedAt.Time,
		DeletedAtV:    *postureStat.DeletedAt.Valid,
		ID:            *postureStat.Id,
	}
	return bhe_sentinel_data, nil
}

// I pass last Time just in case we need to filter here
func transformPostureDataArray(domainMap *map[string]sdk.ModelDomainSelector, data *[]sdk.ModelRiskPostureStat, currentState *time.Time) ([]BloodhoundEnterpriseData, error) {
	logs := make([]BloodhoundEnterpriseData, 0)

	for _, postureStat := range *data {
		bh_sentinel_record, err := transformPostureData(domainMap, &postureStat)
		if err != nil {
			continue
		}
		logs = append(logs, bh_sentinel_record)
	}

	return logs, nil
}

func transformConfigurationFinding(domainMap *map[string]sdk.ModelDomainSelector, _ string, pathType string, pathTitle string, finding MyModelListFinding, findingProps *Props) (*BloodhoundEnterpriseData, error) {
	selector := (*domainMap)[*finding.DomainSID]

	bhe_sentinel_data := &BloodhoundEnterpriseData{
		DataType:          "posture_path",
		TimeGenerated:     *finding.CreatedAt,
		DomainSID:         *finding.DomainSID,
		DomainName:        *selector.Name,
		DomainType:        *selector.Type,
		DomainID:          *selector.Id,
		UpdatedAt:         *finding.UpdatedAt,
		CreatedAt:         *finding.CreatedAt,
		DeletedAt:         finding.DeletedAt.Time,
		DeletedAtV:        *finding.DeletedAt.Valid,
		Principal:         *findingProps.Name,
		TierZeroPrincipal: *findingProps.Name,
		PathType:          pathType,
		PathTitle:		   pathTitle,
		EventDetails: 	   pathTitle, 
		ID:                int64(*finding.Id),
	}
	return bhe_sentinel_data, nil
}

func transformRelationshipFinding(domainMap *map[string]sdk.ModelDomainSelector, _ string, pathType string, pathTitle string, finding MyModelRelationshipFinding, fromProps *FromPrincipalProps, toProps *ToPrincipalProps) (*BloodhoundEnterpriseData, error) {
	selector := (*domainMap)[*finding.DomainSID]
	bhe_sentinel_data := BloodhoundEnterpriseData{
		DataType:             "posture_path",
		TimeGenerated:        *finding.CreatedAt,
		DomainSID:            *finding.DomainSID,
		DomainName:           *selector.Name,
		DomainType:           *selector.Type,
		DomainID:             *selector.Id,
		UpdatedAt:            *finding.UpdatedAt,
		CreatedAt:            *finding.CreatedAt,
		DeletedAt:            finding.DeletedAt.Time,
		TierZeroPrincipal:    toProps.Name,
		NonTierZeroPrincipal: fromProps.Name,
		PathType:             pathType,
		PathTitle: 			  pathTitle,
		EventDetails:		  pathTitle,
		// DeletedAt: finding.DeletedAt,
		DeletedAtV: *finding.DeletedAt.Valid,
		// DeletedAtV: finding.DeletedAt != nil,
		ID: int64(*finding.Id),
	}
	return &bhe_sentinel_data, nil
}

func transformAttackPathData(domainMap *map[string]sdk.ModelDomainSelector, data map[string]map[string][]json.RawMessage, pathTypeMap map[string]string) ([]BloodhoundEnterpriseData, error) {
	bhd := make([]BloodhoundEnterpriseData, 0)
	for domainId, pathMap := range data {
		for pathType, attackPathDataArray := range pathMap {
			var pathTitle, ok = pathTypeMap[pathType]
			if !ok {
				pathTitle = "Unknown"
				log.Printf("Error path title not found for %s", pathType)
			} else {
				log.Printf("Found path title for %s", pathTitle)
			}
			for _, attackPathJson := range attackPathDataArray {
				x := AttackFindingProperties{}
				json.Unmarshal(attackPathJson, &x)

				var isRelationshipFinding bool = true
				if x.ToPrincipalProps == nil {
					isRelationshipFinding = false
				}
				if x.FromPrincipalProps == nil {
					isRelationshipFinding = false
				}
				if !isRelationshipFinding {
					if x.Props == nil {
						return nil, fmt.Errorf("Error attack path is not a relation attack path, Principal key expect")
					}
				}
				if isRelationshipFinding {
					relationshipFinding := MyModelRelationshipFinding{}
					err := json.Unmarshal(attackPathJson, &relationshipFinding)
					if err != nil {
						return nil, err
					}
					toPrincipalProps := x.ToPrincipalProps
					fromPrincipalProps := x.FromPrincipalProps
					d, err := transformRelationshipFinding(domainMap, domainId, pathType, pathTitle, relationshipFinding, fromPrincipalProps, toPrincipalProps)
					if err != nil || d == nil {
						log.Printf("Error transforming relationship finding, skipping %s, %s", domainId, pathType)
						continue
					} else {
						bhd = append(bhd, *d)
					}
				} else {
					modelListFinding := MyModelListFinding{}
					err := json.Unmarshal(attackPathJson, &modelListFinding)
					if err != nil {
						return nil, err
					}
					props := x.Props
					d, err := transformConfigurationFinding(domainMap, domainId, pathType, pathTitle, modelListFinding, props)
					if err != nil || d == nil {
						log.Printf("Error transforming configuration finding, skipping %s %s", domainId, pathType)
						continue
					} else {
						bhd = append(bhd, *d)
					}
				}
			}
		}
	}
	return bhd, nil
}

func transformAttackAggregator(domainMap *map[string]sdk.ModelDomainSelector, data map[string]map[string][]sdk.ModelRiskCounts) ([]BloodhoundEnterpriseData, error) {
	bhd := make([]BloodhoundEnterpriseData, 0)
	for domainId, pathMap := range data {
		for pathType, riskArray := range pathMap {
			for _, risk := range riskArray {
				data, err := transformModelRiskCountr(domainMap, domainId, pathType, risk)
				if err != nil {
					log.Printf("Error transforming risk counter, skipping record: %v", err)
					continue
				}
				bhd = append(bhd, data) // TODO is this correct, capacity
			}
		}
	}
	return bhd, nil
}

func transformModelRiskCountr(domainMap *map[string]sdk.ModelDomainSelector, _ string, path_type string, data sdk.ModelRiskCounts) (BloodhoundEnterpriseData, error) {

	selector := (*domainMap)[*data.DomainSID]
	bhe_sentinel_data := BloodhoundEnterpriseData{
		DataType:          "finding_export",
		TimeGenerated:     *data.CreatedAt,
		DomainSID:         *data.DomainSID,
		DomainName:        *selector.Name,
		DomainType:        *selector.Type,
		DomainID:          *selector.Id,
		ExposureIndex:     math.Round(*data.CompositeRisk * 100),
		Exposure:          *data.CompositeRisk,
		FindingCount:      float64(*data.FindingCount),
		DomainImpactValue: float64(*data.ImpactedAssetCount),
		UpdatedAt:         *data.UpdatedAt,
		CreatedAt:         *data.CreatedAt,
		DeletedAt:         data.DeletedAt.Time,
		DeletedAtV:        *data.DeletedAt.Valid,
		ID:                *data.Id,
		PathType:          path_type,
	}
	return bhe_sentinel_data, nil

}

// little hackish but it means I don't need to deal with introspection edge cases
func structToFieldListUsingJSON(theStruct interface{}, ignore map[string]bool) (string, error) {
	// Marshal to JSON
	jsonData, err := json.Marshal(theStruct)
	if err != nil {
		return "", fmt.Errorf("Error marshaling JSON: %v", err)
	}

	// Unmarshal JSON into a map
	var m map[string]interface{}
	if err := json.Unmarshal(jsonData, &m); err != nil {
		return "", fmt.Errorf("Error unmarshaling JSON: %v", err)
	}

	// Build the "key=value" string
	var parts []string
	for key, value := range m {
		if _, ok := ignore[key]; ok {
			continue
		}
		parts = append(parts, fmt.Sprintf("%s=%v", key, value))
	}
	s := strings.Join(parts, ",")
	return s, nil
}

func transformAudiLogs(logs []sdk.ModelAuditLog) ([]BloodhoundEnterpriseData, error) {
	ignore := map[string]bool{"request_id": true, "actor_id": true}

	records := make([]BloodhoundEnterpriseData, 0)
	for _, data := range logs {
		createdAt, err := time.Parse(time.RFC3339Nano, *data.CreatedAt)
		if err != nil {
			log.Printf("failed to parse created at time %s Error: %v", *data.CreatedAt, err)
		}

		// Format the log data into fields excluding request_id and actor_id
		fieldListString, err := structToFieldListUsingJSON(data, ignore)
		if err != nil {
			log.Printf("failed to convert struct to field list skipping : %v", err)
			continue
		}
		record := BloodhoundEnterpriseData{
			DataType: "audit_log",

			TimeGenerated: time.Now(),
			CreatedAt:     createdAt,
			ID:            *data.Id,
			EventDetails:  fieldListString,
			EventType:     *data.Action,
		}
		records = append(records, record)
	}
	return records, nil
}

func transformTierZeroPrincipal(graph *sdk.ModelUnifiedGraphGraph, domainMap *map[string]sdk.ModelDomainSelector) ([]BloodhoundEnterpriseData, error) {
	records := make([]BloodhoundEnterpriseData, 0)
	nodes := graph.Nodes
	for _, node := range *nodes {
		if *node.IsTierZero == false {
			continue
		}
		props := (*node.Properties)
		var selector *sdk.ModelDomainSelector = nil

		if *node.Kind == "Meta" {
			continue
		}
		if *node.Kind == "Base" {
			continue
		}

		sid, ok := props["domainsid"].(string)
		if ok == true {
			s, ok := (*domainMap)[sid]
			if ok == true {
				selector = &s
			}
		}

		if selector == nil {
			sid, ok := props["tenantid"].(string)
			if ok == true {
				s, ok := (*domainMap)[sid]
				if ok == true {
					selector = &s
				}
			}
		}
		if selector == nil {
			s, ok := (*domainMap)[*node.ObjectId]
			if ok == true {
				selector = &s
			}
		}
		if selector == nil {
			continue
		}

		var domainType = selector.Name
		if strings.HasPrefix(*domainType, "AZ") {
			s := strings.ReplaceAll(*domainType, "AZ", "")
			domainType = &s
		}
		bheRecord := BloodhoundEnterpriseData{
			DataType:          "t0_export",
			TimeGenerated:     time.Now(),
			DomainSID:         *node.ObjectId,
			DomainName:        *selector.Name,
			DomainType:        *selector.Type,
			DomainID:          *selector.Id,
			CreatedAt:         time.Now(),
			EventDetails:      *node.Kind,
			TierZeroPrincipal: *node.Label,
			// TODO update updated time
		}
		records = append(records, bheRecord)
	}
	return records, nil
}

func CreateBatches(records []BloodhoundEnterpriseData, maxUploadSize int64) ([][]BloodhoundEnterpriseData, error) {
	if len(records) == 0 {
		return make([][]BloodhoundEnterpriseData, 0), nil
	}

	// We test a single record for size
	// Get size of record list
	singleRecordJson, err := json.Marshal(records[0])
	if err != nil {
		return nil, fmt.Errorf("Error marshaling the data %v", err)
	}
	n := int64(len(singleRecordJson))

	if n >= maxUploadSize {
		return nil, fmt.Errorf("Error marshalling the data.  A single record[bytes] %d is too large to upload. maxUploadSize[bytes] %d. ", n, maxUploadSize)
	}

	// We limit ourselves to maxUploadSize and then we are conservative and reduce the number of records per batch
	recordsPerBatch := int(maxUploadSize / n)
	if recordsPerBatch > 2 {
		recordsPerBatch -= 2
	}

	var batchedRecords = make([][]BloodhoundEnterpriseData, 0)

	for i := 0; i < len(records); i += recordsPerBatch {
		end := i + recordsPerBatch

		if end > len(records) {
			end = len(records)
		}
		batchedRecords = append(batchedRecords, records[i:end])
	}

	return batchedRecords, nil
}

func printSlice(s [][]BloodhoundEnterpriseData) {
	var ptr *[]BloodhoundEnterpriseData
	if cap(s) >= 1 {
		ptr = &s[:cap(s)][0]
	}
	fmt.Printf("ptr=%p len=%d cap=%d \n", ptr, len(s), cap(s))
}

// Create batches of marshaled json records and gaurantee that they will fix the maxUploadSize
// We take approximate batches generated by CreateBatches and then individually test size and rebatch with
// maxUploadSize reduced by half
func CreateBatchesGauranteedToFit(records []BloodhoundEnterpriseData, maxUploadSize int64) ([][]byte, error) {

	var batchesToMarshal, err = CreateBatches(records, maxUploadSize)
	if err != nil {
		return nil, err
	}

	log.Printf("Original batch size %d", len(batchesToMarshal))
	var jsonBatches = make([][]byte, 0)
	for len(batchesToMarshal) > 0 {
		// POP of a batch, marshal it and then check if it fits
		batch := batchesToMarshal[len(batchesToMarshal)-1]
		batchesToMarshal = batchesToMarshal[:len(batchesToMarshal)-1]
		batchJSON, err := json.Marshal(batch)
		if err != nil {
			return nil, err
		}

		// if a single marshaled JSON is still too big,
		// reduce the maxUploadSize rebatch, adding them back to batchesToMarshal so they will be tested again
		if int64(len(batchJSON)) > maxUploadSize {
			log.Printf("Warning needing redo a large batch %d", len(batchJSON))
			maxUploadSize := maxUploadSize - (int64(len(batchJSON)) - maxUploadSize)
			smallBatches, err := CreateBatches(batch, maxUploadSize)
			if err != nil {
				return nil, err
			}
			batchesToMarshal = append(batchesToMarshal, smallBatches...)
		} else {
			jsonBatches = append(jsonBatches, batchJSON)
		}
	}
	return jsonBatches, nil
}

func ApplyEditors(ctx context.Context, c *sdk.Client, req *http.Request, additionalEditors []sdk.RequestEditorFn) error {
	for _, r := range c.RequestEditors {
		if err := r(ctx, req); err != nil {
			return err
		}
	}
	for _, r := range additionalEditors {
		if err := r(ctx, req); err != nil {
			return err
		}
	}
	return nil
}

// UploadLogsCallback returns a curried function that can be used as a callback
func UploadLogsCallback(bloodhoundClient *sdk.ClientWithResponses, lastRun *time.Time, azLogsClient *azlogs.Client, ruleId string, maxUploadSize int64) ([]string, error) {
	// TODO is there a generic sdk client type

	if lastRun == nil {
		log.Print("Starting log processing lastRun is nil")
	} else {
		log.Printf("Starting log processing lastRun is %v", lastRun)
	}
	var responseLogs = make([]string, 0)

	bloodhoundRecordData := make(map[string][]BloodhoundEnterpriseData)

	// Get attack path type to attack path title mapping
	// TODO: lift this and it really should be defined in the API
	// TODO: Retry?  Handle 429?
	var client = bloodhoundClient.ClientInterface.(*sdk.Client)	
	pathTypes, err := bloodhoundClient.ListAttackPathTypesWithResponse(context.TODO(), nil)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path types %v", err))
		return responseLogs, err
	}
	var pathMap = make(map[string]string)

	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path types", len(*pathTypes.JSON200.Data)))
	for _, pathType := range *pathTypes.JSON200.Data {
		// I'm going to get these one at a time TOOD: check if there is a better way
		req, err := http.NewRequest("GET",fmt.Sprintf("https://demo.bloodhoundenterprise.io/api/v2/assets/findings/%s/title.md", pathType), nil)
		if (err != nil) {
			responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path title %v", err))
			return responseLogs, err
		}

		ApplyEditors(context.TODO(), client, req, client.RequestEditors)
		response, err := client.Client.Do(req)
		if (err != nil) {
			responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path title %v", err))
			return responseLogs, err
		}
		if (response.StatusCode != http.StatusOK) {
			responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path title %v", response.Status))
			return responseLogs, err
		}
		var responseBytes = make([]byte, 1024)
		count, err := response.Body.Read(responseBytes) 
		pathMap[pathType] = string(responseBytes[:count])
	}

	lastAnalysisTime, err := bloodhound.GetLastAnalysisTime(bloodhoundClient)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get last analysis time %v", err))
		return responseLogs, err
	}

	if lastRun != nil {
		if lastRun.Compare(*lastAnalysisTime) == +1 {
			responseLogs = append(responseLogs, fmt.Sprintf("last ingest time %v after last analysis time %v.  We will skip ingest", lastRun, lastAnalysisTime))
			return responseLogs, nil
		} else {
			responseLogs = append(responseLogs, fmt.Sprintf("last ingest time %v before last analysis time %v.  We will continue", lastRun, lastAnalysisTime))
		}
	} else {
		log.Printf("UploadLogsCallback lastRun is nil, not doing compare")
	}

	mapping, err := bloodhound.GetDomainMapping(bloodhoundClient)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get domain mapping %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d domain mappings", len(*mapping)))

	domainIds := make([]string, 0, len(*mapping))
	for k, _ := range *mapping {
		domainIds = append(domainIds, k)
	}

	// Posture Data
	// Get postureData from Bloodhound using bloodhoundClient
	postureData, err := bloodhound.GetPostureData(bloodhoundClient, lastRun)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to getposture postureData %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d posture records", len(*postureData)))

	// Transform postureData
	postureBHERecords, err := transformPostureDataArray(mapping, postureData, lastRun)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to transform postureData %v", err))
		return responseLogs, err
	}

	bloodhoundRecordData["postureData"] = postureBHERecords

	// Get Audit lgos
	auditLogData, err := bloodhound.GetAuditLog(bloodhoundClient, lastRun)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get audit logs, skipping %v", err))
	}
	log.Printf("Received %d audit log rows.", len(auditLogData))

	// Transform audit logs to BHE sentinel records
	auditLogBHERecords, err := transformAudiLogs(auditLogData)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get audit logs, skipping %v", err))
	}
	log.Printf("Transformed %d audit log records.", len(auditLogBHERecords))

	bloodhoundRecordData["auditLogs"] = auditLogBHERecords

	// Attack Path

	// Supporting finding data for paths
	findingsPerDomain, err := bloodhound.GetAttackPathTypesForDomain(bloodhoundClient, domainIds)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("error getting attack path types %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path types", len(findingsPerDomain)))

	// Get Attack Path Data
	attackPathData, err := bloodhound.GetAttackPathData(bloodhoundClient, domainIds, findingsPerDomain)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("error getting attack path data %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path data", len(attackPathData)))
	// Transform attack path data
	attackPathBHERecords, err := transformAttackPathData(mapping, attackPathData, pathMap)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("error transforming attack path data %v", err))
	} else {
		bloodhoundRecordData["attackPathData"] = attackPathBHERecords
	}

	// Get Attack Path Aggregate Data
	aggregatorData, err := bloodhound.GetAttackPathAggregatorData(bloodhoundClient, lastRun, domainIds, findingsPerDomain)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error getting attack path aggregator data %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path aggregator records", len(aggregatorData)))

	attackPathAggregateBHERecords, err := transformAttackAggregator(mapping, aggregatorData)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error transforming attack path aggregator data %v", err))
		return responseLogs, err
	}
	bloodhoundRecordData["attackPathAggregateData"] = attackPathAggregateBHERecords

	tierZeroData, err := bloodhound.GetTierZeroPrincipal(bloodhoundClient)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error getting tier zero principals %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("Got %d cypher query graph nodes", len(*tierZeroData.Nodes)))

	tier0BHERecords, err := transformTierZeroPrincipal(tierZeroData, mapping)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error transforming tier zero principal data %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("Got %d tier zero principals", len(tier0BHERecords)))

	bloodhoundRecordData["tier0"] = tier0BHERecords

	var lastError error
	for kind, recordList := range bloodhoundRecordData {
		log.Printf("About to upload %s data %d records ", kind, len(recordList))

		recordsJSON, err := CreateBatchesGauranteedToFit(recordList, maxUploadSize)
		if err != nil {
			responseLogs = append(responseLogs, fmt.Sprintf("failed to generate batched json for %s data Error: %v", kind, err))
			lastError = err
			continue
		}
		for _, jsonBatch := range recordsJSON {
			_, err = azLogsClient.Upload(context.TODO(), ruleId, "Custom-BloodHoundLogs_CL", jsonBatch, nil)
			if err != nil {
				responseLogs = append(responseLogs, fmt.Sprintf("failed to upload %s data Error: %v", kind, err))
				lastError = err
				continue
			}
			responseLogs = append(responseLogs, fmt.Sprintf("Uploaded %s data size(bytes): %d", kind, len(jsonBatch)))
		}
	}
	return responseLogs, lastError
}

