package connector

import (
	"context"
	"encoding/json"
	"fmt"
	"function/pkg/bloodhound"
	"log"
	"math"
	"strings"
	"time"

	//	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/monitor/ingestion/azlogs"
	"github.com/SpecterOps/bloodhound-go-sdk/sdk"
)

type BloodhoundEnterpriseData struct {
	TimeGenerated        time.Time  `json:"TimeGenerated"`
	DomainSID            string     `json:"domain_sid"`
	ExposureIndex        float64    `json:"exposure_index"`
	TierZeroCount        float64    `json:"tier_zero_count"`
	DomainID             string     `json:"domain_id"`
	NonTierZeroPrincipal string     `json:"non_tier_zero_principal"`
	TierZeroPrincipal    string     `json:"tier_zero_principal"`
	Group                string     `json:"group"`
	Principal            string     `json:"principal"`
	PathID               string     `json:"path_id"`
	User                 string     `json:"user"`
	FindingID            string     `json:"finding_id"`
	PathTitle            string     `json:"path_title"`
	PathType             string     `json:"path_type"`
	Exposure             float64    `json:"exposure"`
	FindingCount         float64    `json:"finding_count"`
	PrincipalCount       float64    `json:"principal_count"`
	ID                   int64      `json:"id"`
	CreatedAt            time.Time  `json:"created_at"`
	UpdatedAt            time.Time  `json:"updated_at"`
	DeletedAt            *time.Time `json:"deleted_at"` // Pointer to handle null values
	DeletedAtV           bool       `json:"deleted_at_v"`
	Severity             string     `json:"severity"`
	DomainImpactValue    float64    `json:"domain_impact_value"`
	DomainName           string     `json:"domain_name"`
	DomainType           string     `json:"domain_type"`
	DataType             string     `json:"data_type"`
	EventType            string     `json:"event_type"`
	EventDetails         string     `json:"event_details"`
}

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

func transformPostureDataArray(domainMap *map[string]sdk.ModelDomainSelector, data *[]sdk.ModelRiskPostureStat) ([]BloodhoundEnterpriseData, error) {
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

func transformConfigurationFinding(domainMap *map[string]sdk.ModelDomainSelector, domainId string, pathType string, finding MyModelListFinding, findingProps *Props) (*BloodhoundEnterpriseData, error) {
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
		ID:                int64(*finding.Id),
	}
	return bhe_sentinel_data, nil
}

func transformRelationshipFinding(domainMap *map[string]sdk.ModelDomainSelector, domainId string, pathType string, finding MyModelRelationshipFinding, fromProps *FromPrincipalProps, toProps *ToPrincipalProps) (*BloodhoundEnterpriseData, error) {
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
		// DeletedAt: finding.DeletedAt,
		DeletedAtV: *finding.DeletedAt.Valid,
		// DeletedAtV: finding.DeletedAt != nil,
		ID: int64(*finding.Id),
	}
	return &bhe_sentinel_data, nil
}

func transformAttackPathData(domainMap *map[string]sdk.ModelDomainSelector, data map[string]map[string][]json.RawMessage) ([]BloodhoundEnterpriseData, error) {
	bhd := make([]BloodhoundEnterpriseData, 0)
	for domainId, pathMap := range data {
		for pathType, attackPathDataArray := range pathMap {
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
					d, err := transformRelationshipFinding(domainMap, domainId, pathType, relationshipFinding, fromPrincipalProps, toPrincipalProps)
					if err != nil || d == nil {
						log.Printf("Error transforming relationship finding, skipping", domainId, pathType)
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
					d, err := transformConfigurationFinding(domainMap, domainId, pathType, modelListFinding, props)
					if err != nil || d == nil {
						log.Printf("Error transforming configuration finding, skipping", domainId, pathType)
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

func transformModelRiskCountr(domainMap *map[string]sdk.ModelDomainSelector, domainId string, path_type string, data sdk.ModelRiskCounts) (BloodhoundEnterpriseData, error) {

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
		return "", fmt.Errorf("Error marshaling JSON:", err)
	}

	// Unmarshal JSON into a map
	var m map[string]interface{}
	if err := json.Unmarshal(jsonData, &m); err != nil {
		return "", fmt.Errorf("Error unmarshaling JSON:", err)
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
			log.Printf("failed to parse created at time %s Error: %v", data.CreatedAt, err)
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
		if selector == nil {
			sid, ok := props["domainsid"].(string)
			if ok == true {
				s, ok := (*domainMap)[sid]
				if ok == true {
					selector = &s
				}
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

func MakeConnectorCallback(bloodhoundClient *sdk.ClientWithResponses, azLogsClient *azlogs.Client, ruleId string, maxUploadSize int64) func() ([]string, error) {
	return func() ([]string, error) {
		return UploadLogsCallback(bloodhoundClient, azLogsClient, ruleId, maxUploadSize)
	}
}

// UploadLogsCallback returns a curried function that can be used as a callback
func UploadLogsCallback(bloodhoundClient *sdk.ClientWithResponses, azLogsClient *azlogs.Client, ruleId string, maxUploadSize int64) ([]string, error) {
	// TODO is there a generic sdk client type

	log.Print("Starting log processing")
	var logs = make([]string, 0)

	bloodhound.GetDomainMapping(bloodhoundClient)
	mapping, err := bloodhound.GetDomainMapping(bloodhoundClient)
	if err != nil {
		logs = append(logs, fmt.Sprintf("failed to get domain mapping %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("got %d domain mappings", len(*mapping)))

	domainIds := make([]string, 0, len(*mapping))
	for k, _ := range *mapping {
		domainIds = append(domainIds, k)
	}

	bloodhoundRecordData := make(map[string][]BloodhoundEnterpriseData)

	if false {
		// Get Audit lgos
		auditLogData, err := bloodhound.GetAuditLog(bloodhoundClient)
		if err != nil {
			return logs, err
		}
		log.Printf("Received %d audit log rows.", len(auditLogData))

		// Transform audit logs to BHE sentinel records
		auditLogBHERecords, err := transformAudiLogs(auditLogData)
		if err != nil {
			return logs, err
		}
		log.Printf("Transformed %d audit log records.", len(auditLogBHERecords))

		bloodhoundRecordData["auditLogs"] = auditLogBHERecords
	}

	// Posture Data
	// Get postureData from Bloodhound using bloodhoundClient
	postureData, err := bloodhound.GetPostureData(bloodhoundClient)
	if err != nil {
		logs = append(logs, fmt.Sprint("failed to getposture postureData %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("got %d posture records", len(*postureData)))

	// Transform postureData
	postureBHERecords, err := transformPostureDataArray(mapping, postureData)
	if err != nil {
		logs = append(logs, fmt.Sprintf("failed to transform postureData %v", err))
		return logs, err
	}
	logs = append(logs, "transformed posture data")

	bloodhoundRecordData["postureData"] = postureBHERecords

	// Attack Path

	// Supporting finding data for paths
	findingsPerDomain, err := bloodhound.GetAttackPathTypesForDomain(bloodhoundClient, domainIds)
	if err != nil {
		logs = append(logs, fmt.Sprintf("error getting attack path types %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("got %d attack path types", len(findingsPerDomain)))

	// Get Attack Path Data
	attackPathData, err := bloodhound.GetAttackPathData(bloodhoundClient, domainIds, findingsPerDomain)
	if err != nil {
		logs = append(logs, fmt.Sprintf("error getting attack path data %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("got %d attack path data", len(attackPathData)))
	// Transform attack path data
	attackPathBHERecords, err := transformAttackPathData(mapping, attackPathData)
	if err != nil {
		logs = append(logs, fmt.Sprintf("error transforming attack path data %v", err))
		return logs, err
	}
	bloodhoundRecordData["attackPathData"] = attackPathBHERecords

	// Get Attack Path Aggregate Data
	aggregatorData, err := bloodhound.GetAttackPathAggregatorData(bloodhoundClient, domainIds, findingsPerDomain)
	if err != nil {
		logs = append(logs, fmt.Sprintf("Error getting attack path aggregator data %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("got %d attack path aggregator records", len(aggregatorData)))

	attackPathAggregateBHERecords, err := transformAttackAggregator(mapping, aggregatorData)
	if err != nil {
		logs = append(logs, fmt.Sprintf("Error transforming attack path aggregator data %v", err))
		return logs, err
	}
	bloodhoundRecordData["attackPathAggregateData"] = attackPathAggregateBHERecords

	tierZeroData, err := bloodhound.GetTierZeroPrincipal(bloodhoundClient)
	if err != nil {
		logs = append(logs, fmt.Sprintf("Error getting tier zero principals %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("Got %d cypher query graph nodes", len(*tierZeroData.Nodes)))

	tier0BHERecords, err := transformTierZeroPrincipal(tierZeroData, mapping)
	if err != nil {
		logs = append(logs, fmt.Sprintf("Error transforming tier zero principal data %v", err))
		return logs, err
	}
	logs = append(logs, fmt.Sprintf("Got %d tier zero principals", len(tier0BHERecords)))

	bloodhoundRecordData["tier0"] = tier0BHERecords

	var lastError error = nil
	for kind, recordList := range bloodhoundRecordData {
		log.Printf("About to upload %s data %d records ", kind, len(recordList))

		recordsJSON, err := json.Marshal(recordList)
		if err != nil {
			logs = append(logs, fmt.Sprintf("failed to marshal %s data Error: %v", kind, err))
			return logs, err
		}

		if int64(len(recordsJSON)) > maxUploadSize {
			logs = append(logs, fmt.Sprintf("Marshaled data of %s data size(bytes): %d is over the upload limit %d", kind, len(recordsJSON), maxUploadSize))
			return logs, err
		}

		_, err = azLogsClient.Upload(context.TODO(), ruleId, "Custom-BloodHoundLogs_CL", recordsJSON, nil)
		if err != nil {
			logs = append(logs, fmt.Sprintf("failed to upload %s data Error: %v", kind, err))
			lastError = err
			continue
		}
		logs = append(logs, fmt.Sprintf("Uploaded %s data size(bytes): %d", kind, len(recordsJSON)))

	}

	return logs, lastError
}
