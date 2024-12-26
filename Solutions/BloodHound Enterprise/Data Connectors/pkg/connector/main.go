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
		DomainSID:     *postureStat.DomainSid,
		DomainName:    *selector.Name,
		DomainType:    *selector.Type,
		DomainID:      *selector.Id,
		ExposureIndex: math.Round(*postureStat.ExposureIndex * 100),
		Exposure:	   *postureStat.ExposureIndex,
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
		PathTitle:         pathTitle,
		EventDetails:      pathTitle,
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
		PathTitle:            pathTitle,
		EventDetails:         pathTitle,
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

func transformAttackAggregator(domainMap *map[string]sdk.ModelDomainSelector, data map[string]map[string][]sdk.ModelRiskCounts, pathTypeMap *map[string]string) ([]BloodhoundEnterpriseData, error) {
	bhd := make([]BloodhoundEnterpriseData, 0)
	for domainId, pathMap := range data {
		for pathType, riskArray := range pathMap {
			for _, risk := range riskArray {
				pathTitle, ok := (*pathTypeMap)[pathType]
				if !ok || pathTitle == "" {
					pathTitle = "Unknown"
					log.Printf("Error path title not found for %s", pathType)
				} 
				data, err := transformModelRiskCountr(domainMap, domainId, pathType, pathTitle, risk)
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

func transformModelRiskCountr(domainMap *map[string]sdk.ModelDomainSelector, _ string, path_type string, path_title string, data sdk.ModelRiskCounts) (BloodhoundEnterpriseData, error) {

	selector := (*domainMap)[*data.DomainSID]
	bhe_sentinel_data := BloodhoundEnterpriseData{
		DataType:          "finding_export",
		TimeGenerated:     *data.CreatedAt,
		DomainSID:         *data.DomainSID,
		DomainName:        *selector.Name,
		DomainType:        *selector.Type,
		DomainID:          *selector.Id,
		Exposure:          *data.CompositeRisk,
		FindingCount:      float64(*data.FindingCount),
		DomainImpactValue: float64(*data.ImpactedAssetCount),
		UpdatedAt:         *data.UpdatedAt,
		CreatedAt:         *data.CreatedAt,
		DeletedAt:         data.DeletedAt.Time,
		DeletedAtV:        *data.DeletedAt.Valid,
		ID:                *data.Id,
		PathType:          path_type,
		PathTitle:         path_title,
		EventDetails:      path_title,
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

func memberOf(elem *string, set map[string]bool) bool {
	_, ok := set[string(*elem)]
	return ok
}

func in(elem string, set map[string]bool) bool {
	_, ok := set[elem]
	return ok
}

func transformTierZeroPrincipal(tierZeroGroupmembers []sdk.ModelAssetGroupMember, domainMap map[string]sdk.ModelDomainSelector) ([]BloodhoundEnterpriseData, error) {
	ENVIRONMENT_KINDS := map[string]bool{"Domain": true, "AZTenant": true}
	records := make([]BloodhoundEnterpriseData, 0)
	for _, groupMember := range tierZeroGroupmembers {
		var environment_sid = groupMember.EnvironmentId
		if groupMember.PrimaryKind != nil && memberOf(groupMember.PrimaryKind, ENVIRONMENT_KINDS) {
			environment_sid = groupMember.ObjectId		
		}
		if environment_sid == nil || *environment_sid == "" {
			log.Printf("Error tier zero principal missing environment sid skipping %s", *groupMember.Name)
			continue
		}

		// Use the SID to lookup the name, id and type
		selector, ok := domainMap[*environment_sid]
		if !ok {
			log.Printf("Error tier zero principal could not find domain record for sid %s skipping %s", *environment_sid, *groupMember.Name)
			continue
		}
		environment_name := *selector.Name
		environment_id := selector.Id
		environment_kind := selector.Type

		record := BloodhoundEnterpriseData{
			TierZeroPrincipal: *groupMember.Name,
			FindingID:         *groupMember.ObjectId,    // TODO: move this to a new field called ObjectID (backfill required for other data_types??)
			EventDetails:      *groupMember.PrimaryKind, // TODO: move this to a new field called ObjectKind (backfill required for other data_types??)
			DomainSID:         *environment_sid,
			DomainID:		  *environment_id,			// TODO: DomainSID and DomainID seem redundant
			DomainType:        *environment_kind,
			DomainName:        environment_name,
			DataType:          "t0_export",
			TimeGenerated:     time.Now(),
		}
		records = append(records, record)
	}
	return records, nil
}

func CreateJsonBatches(records []BloodhoundEnterpriseData, maxUploadSize int64) ([][]byte, error) {
	if len(records) == 0 {
		return make([][]byte, 0), nil
	}

	var jsonRecords = make([][]byte, len(records))
	for i, record := range records {
		jsonRecord, err := json.Marshal(record)
		if err != nil {
			// TODO maybe skip
			return nil, fmt.Errorf("Error marshaling the data %v", err)			
		}
		jsonRecords[i] = jsonRecord
	}

	batches := make([][]byte, 1)
	batches = batches[:0]

	batchRecordCounts := make([]int, 0)

	batch := make([]byte, maxUploadSize)
	batch = batch[:0]
	batch = append(batch, "["...)
	joinSeparator := []byte("")
	batchRecordCount := 0
	i := 0
	for i < len(jsonRecords) {
		jsonRecord := jsonRecords[i]
		bytesToAppend := len(joinSeparator) + len(jsonRecord) + len("]")
		recordFits := len(batch) + bytesToAppend + len("]") < cap(batch)
		lastRecord := i == len(jsonRecords)-1
		if recordFits {
			batch = append(batch, joinSeparator...)
			batch = append(batch, jsonRecord...)
			batchRecordCount++
			joinSeparator = []byte(",")
		} else if batchRecordCount == 0 {
			// Error case, a single record is too large to fit in a batch
			return nil, fmt.Errorf("Error marshaling the data.  A single record is too large to upload. maxUploadSize[bytes] %d. ", maxUploadSize)
		}
		if !recordFits || lastRecord {
			// cap it off
			batch = append(batch, "]"...)
			batches = append(batches, batch)
			batchRecordCounts = append(batchRecordCounts, batchRecordCount)
			batch = make([]byte, maxUploadSize)
			batch = batch[:0]
			batch = append(batch, "["...)
			joinSeparator = []byte("")
			batchRecordCount = 0
		}
		if recordFits {
			i ++
		}
	}
	return batches, nil
}

func printSlice(s [][]BloodhoundEnterpriseData) {
	var ptr *[]BloodhoundEnterpriseData
	if cap(s) >= 1 {
		ptr = &s[:cap(s)][0]
	}
	fmt.Printf("ptr=%p len=%d cap=%d \n", ptr, len(s), cap(s))
}

func ApplyEditors(ctx context.Context, c *sdk.Client, req *http.Request, additionalEditors []sdk.RequestEditorFn) error {
	for _, editor := range c.RequestEditors {
		if err := editor(ctx, req); err != nil {
			return err
		}
	}
	for _, editor := range additionalEditors {
		if err := editor(ctx, req); err != nil {
			return err
		}
	}
	return nil
}

func getAssetData(bloodhoundServer string, bloodhoundClient *sdk.ClientWithResponses, uri string) (*http.Response, error) {
	// TODO Better error / retry handling
	if !strings.HasPrefix(bloodhoundServer, "https") {
		bloodhoundServer = "https://" + bloodhoundServer
	}
	var client = bloodhoundClient.ClientInterface.(*sdk.Client)

	req, err := http.NewRequest("GET", fmt.Sprintf("%s/%s", bloodhoundServer, uri), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to build request %v", err)
	}

	err = ApplyEditors(context.TODO(), client, req, client.RequestEditors)
	if err != nil {
		return nil, fmt.Errorf("failed to apply request editors %v", err)
	}
	response, err := client.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request %v", err)
	}
	if response.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed request with status %v", response.Status)
	}

	return response, nil
}

func getAttackPathTitles(bloodhoundServer string, bloodhoundClient *sdk.ClientWithResponses, responseLogs []string) (map[string]string, error) {
	pathTypes, err := bloodhoundClient.ListAttackPathTypesWithResponse(context.TODO(), nil)
	var pathMap = make(map[string]string)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path types %v", err))
		return pathMap, err
	}

	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path types", len(*pathTypes.JSON200.Data)))
	for _, pathType := range *pathTypes.JSON200.Data {
		// I'm going to get these one at a time TOOD: check if there is a better way
		uri := fmt.Sprintf("api/v2/assets/findings/%s/title.md", pathType)
		response, err := getAssetData(bloodhoundServer, bloodhoundClient, uri)
		if err != nil {
			log.Printf("Error getting attack path title for path type %s so skipping %v", pathType, err)
			continue
		}

		var responseBytes = make([]byte, 1024) // TODO check if this is a good size or will expand
		count, err := response.Body.Read(responseBytes)
		pathMap[pathType] = string(responseBytes[:count])
	}
	return pathMap, nil
}

// UploadLogsCallback returns a curried function that can be used as a callback
// hack passing the bh domain / config.  Wont be needed when bloodhoundClient handles assset retrieval.  Need to modify the sdk.
func UploadLogsCallback(bloodhoundClient *sdk.ClientWithResponses, bloodhoundServer string, lastRun *time.Time, azLogsClient *azlogs.Client, ruleId string, maxUploadSize int64) ([]string, error) {
	// TODO is there a generic sdk client type

	if lastRun == nil {
		log.Print("Starting log processing lastRun is nil")
	} else {
		log.Printf("Starting log processing lastRun is %v", lastRun)
	}
	var responseLogs = make([]string, 0)

	bloodhoundRecordData := make(map[string][]BloodhoundEnterpriseData)

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
	}

	mapping, err := bloodhound.GetDomainMapping(bloodhoundClient)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get domain mapping %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d domain mappings", len(*mapping)))

	pathMap, err := getAttackPathTitles(bloodhoundServer, bloodhoundClient, responseLogs)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("failed to get attack path titles %v", err))
		// We will continue without the path titles
	}
	responseLogs = append(responseLogs, fmt.Sprintf("got %d attack path titles", len(pathMap)))

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

	attackPathAggregateBHERecords, err := transformAttackAggregator(mapping, aggregatorData, &pathMap)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error transforming attack path aggregator data %v", err))
		return responseLogs, err
	}

	if len(attackPathAggregateBHERecords) > 0 {
		responseLogs = append(responseLogs, fmt.Sprintf("Got %d attack path aggregator records PathTitle of first is %s", len(attackPathAggregateBHERecords), attackPathAggregateBHERecords[0].PathTitle))
	} else {
		responseLogs = append(responseLogs, fmt.Sprintf("Got 0 attack path aggregator records"))
	}

	bloodhoundRecordData["attackPathAggregateData"] = attackPathAggregateBHERecords

	var tierZeroData []sdk.ModelAssetGroupMember = make([]sdk.ModelAssetGroupMember, 0)

	// Get Tier Zero asset group and then its members
	tierZeroGroup, err := bloodhound.GetTierZeroGroup(bloodhoundClient)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error getting tier zero group skipping %v", err))
	} else {
		tierZeroData, err = bloodhound.GetTierZeroPrincipals(bloodhoundClient, tierZeroGroup)
		if err != nil {
			responseLogs = append(responseLogs, fmt.Sprintf("Error getting tier zero principals skipping %v", err))
		}
		responseLogs = append(responseLogs, fmt.Sprintf("Got %d cypher query graph nodes", len(tierZeroData)))	
	}


	tier0BHERecords, err := transformTierZeroPrincipal(tierZeroData, *mapping)
	if err != nil {
		responseLogs = append(responseLogs, fmt.Sprintf("Error transforming tier zero principal data %v", err))
		return responseLogs, err
	}
	responseLogs = append(responseLogs, fmt.Sprintf("Got %d tier zero principals", len(tier0BHERecords)))

	bloodhoundRecordData["tier0"] = tier0BHERecords

	var lastError error
	for kind, recordList := range bloodhoundRecordData {
		log.Printf("About to upload %s data %d records ", kind, len(recordList))

		recordsJSON, err := CreateJsonBatches(recordList, maxUploadSize)
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
