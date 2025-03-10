package bloodhound

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/SpecterOps/bloodhound-go-sdk/sdk"
)

func InitializeBloodhoundClient(apiKey string, apikeyId string, bloodhoundServer string) (*sdk.ClientWithResponses, error) {
	// HMAC Security Provider
	hmacTokenProvider, err := sdk.NewSecurityProviderHMACCredentials(apiKey, apikeyId)

	if !strings.HasPrefix(bloodhoundServer, "https") {
		bloodhoundServer = "https://" + bloodhoundServer
	}
	if err != nil {
		return nil, fmt.Errorf("Error creating bearer token middleware %v", err)
	}

	client, err := sdk.NewClientWithResponses(
		bloodhoundServer,
		sdk.WithRequestEditorFn(hmacTokenProvider.Intercept),
	)
	if err != nil {
		return nil, fmt.Errorf("Error creating client %v", err)
	}

	return client, nil
}

func GetTierZeroGroup(client *sdk.ClientWithResponses) (int32, error) {
	tier0_tag := "eq:admin_tier_0"
	params := sdk.ListAssetGroupsParams {
		Tag: &tier0_tag,
	}
	response, err := client.ListAssetGroupsWithResponse(context.TODO(), &params)
	if err != nil {
		return 0, fmt.Errorf("Error getting tier zero group %v", err)
	}
	if response.StatusCode() != http.StatusOK {
		return 0, fmt.Errorf("Error getting tier zero group %s", response.Status())
	}
	if len(*response.JSON200.Data.AssetGroups) == 1 && (*response.JSON200.Data.AssetGroups)[0].Id != nil {
		return  *((*response.JSON200.Data.AssetGroups)[0].Id), nil
	}
	return 0, fmt.Errorf("Error getting tier zero group. Expected 1 group, got %d", len(*response.JSON200.Data.AssetGroups))
}

func GetTierZeroPrincipals(client *sdk.ClientWithResponses, tierZeroGroup int32) ([]sdk.ModelAssetGroupMember, error) {
	limit := 10000
	params := &sdk.ListAssetGroupMembersParams{
		Limit: &limit,
	}
	response, err := client.ListAssetGroupMembersWithResponse(context.TODO(), tierZeroGroup, params)
	if err != nil {
		return []sdk.ModelAssetGroupMember{}, fmt.Errorf("Error getting tier zero principals in group %d %v", tierZeroGroup, err)
	}
	if response.StatusCode() != http.StatusOK {
		return []sdk.ModelAssetGroupMember{}, fmt.Errorf("Error getting tier zero principals in group %d %s", tierZeroGroup, response.Status())
	}
	return *response.JSON200.Data.Members, nil
}

func GetLastAnalysisTime(client *sdk.ClientWithResponses) (*time.Time, error) {
	response, err := client.GetDatapipeStatusWithResponse(context.TODO(), nil)
	if err != nil {
		return nil, fmt.Errorf("Error getting last analysis run time %v", err)
	}
	if response.StatusCode() != http.StatusOK {
		return nil, fmt.Errorf("Error getting last analysis run time %s", response.HTTPResponse.Status)
	}
	// TODO does LastCompleteAnalysisAt mean successful completion, do I also need to look at Data.Status
	return response.JSON200.Data.LastCompleteAnalysisAt, nil
}

func GetDomainMapping(client *sdk.ClientWithResponses) (*map[string]sdk.ModelDomainSelector, error) {
	response, err := client.GetAvailableDomainsWithResponse(context.TODO(), nil)
	if err != nil {
		return nil, err
	}
	if response.StatusCode() != http.StatusOK {
		return nil, fmt.Errorf("Error getting available domains: %v", response.StatusCode())
	}

	mapIdToInfo := make(map[string]sdk.ModelDomainSelector)

	for _, domainInfo := range *response.JSON200.Data {
		mapIdToInfo[*domainInfo.Id] = domainInfo
	}

	return &mapIdToInfo, nil
}

func GetPostureData(client *sdk.ClientWithResponses, currentState *time.Time) (*[]sdk.ModelRiskPostureStat, error) {
	params := sdk.GetPostureStatsParams{}

	if currentState != nil {
		params.FromDeprecated = currentState
		log.Printf("GetPostureData From param set to %s", currentState.Format(time.RFC3339))
	} else {
		log.Printf("GetPostureData No currentState we are not setting From parameter")
	}
	response, err := client.GetPostureStatsWithResponse(context.TODO(), &params)

	if err != nil {
		return nil, err
	}
	if response.StatusCode() != http.StatusOK {
		return nil, fmt.Errorf("GetPostureData returned error code %d", response.StatusCode())
	}

	return response.JSON200.Data, nil
}

// Note: there is no last time
func GetAttackPathTypesForDomain(client *sdk.ClientWithResponses, domain_ids []string) (map[string][]string, error) {
	m := make(map[string][]string)
	for _, domainId := range domain_ids {
		response, err := client.ListAvailableAttackPathTypesForDomainWithResponse(context.TODO(), domainId, nil)
		if err != nil {
			log.Printf("Error trying to get attack path types")
			return nil, err
		}
		if response.StatusCode() != http.StatusOK {
			return nil, fmt.Errorf("Error trying get attack path for domain %s.  Error %v", domainId, response)
		}
		m[domainId] = *response.JSON200.Data // TODO nil checks empty checks
	}
	return m, nil
}

type AttackPathResponse struct {
	Count int
	Limit int
	Skip  int
	Data  []json.RawMessage
}

func GetAttackPathData(client *sdk.ClientWithResponses, domain_ids []string, findings_per_domain map[string][]string) (map[string]map[string][]json.RawMessage, error) {

	m := make(map[string]map[string][]json.RawMessage)
	for _, domainId := range domain_ids {
		for _, finding := range findings_per_domain[domainId] {
			dm := make(map[string][]json.RawMessage)

			// TODO support pagination using limit and skip, along with returned count
			l := sdk.ApiParamsQueryLimit(600000)
			a := sdk.ApiParamsPredicateFilterString("ModeRelationshipFindingResponse")
			p := sdk.ListDomainAttackPathsDetailsParams{
				Limit:             &l,
				Finding:           &finding,
				FindingDeprecated: &finding,
				Accepted:          &a,
			}
			response, err := client.ListDomainAttackPathsDetailsWithResponse(context.TODO(), domainId, &p)
			if err != nil {
				return nil, err
			}
			if response.StatusCode() != http.StatusOK {
				return nil, fmt.Errorf("Error getting attack path finding %s for domain %s.  Error %v", finding, domainId, response.StatusCode())
			}
			if response.JSON200 == nil {
				return nil, fmt.Errorf("")
			}

			x := AttackPathResponse{}
			json.Unmarshal(response.Body, &x)

			dm[finding] = x.Data
			m[domainId] = dm
		}
	}
	return m, nil
}

func GetAttackPathAggregatorData(client *sdk.ClientWithResponses, lastRun *time.Time, domain_ids []string, findings_per_domain map[string][]string) (map[string]map[string][]sdk.ModelRiskCounts, error) {

	m := make(map[string]map[string][]sdk.ModelRiskCounts)
	for _, domainId := range domain_ids {
		for _, finding := range findings_per_domain[domainId] {
			dm := make(map[string][]sdk.ModelRiskCounts)

			f := sdk.ApiParamsPredicateFilterString(finding)
			var p = sdk.ListAttackPathSparklineValuesParams{
				Finding: f,
			}
			if lastRun != nil {
				p.From = lastRun
			}
			response, err := client.ListAttackPathSparklineValuesWithResponse(context.TODO(), domainId, &p)
			if err != nil {
				return nil, err
			}
			if response.StatusCode() != http.StatusOK {
				// TODO should I skip here
				return nil, fmt.Errorf("Error getting attack path aggregate metrics %s for domain %s.  Error %v", finding, domainId, response)
			}
			if response.JSON200 == nil || response.JSON200.Data == nil {
				// TODO should I skip here
				return nil, fmt.Errorf("Error getting attack path aggregate metrics %s for domain %s.  Error %v", finding, domainId, response)
			}

			dm[finding] = *response.JSON200.Data // TODO do I need copy this in?
			m[domainId] = dm
		}
	}
	return m, nil
}

func GetAuditLog(client *sdk.ClientWithResponses, lastRunTime *time.Time) ([]sdk.ModelAuditLog, error) {

	l := 500000
	params := sdk.ListAuditLogsParams{
		After: lastRunTime,
		Limit: &l,
	}
	response, err := client.ListAuditLogsWithResponse(context.TODO(), &params)
	scrubedLogs := make([]sdk.ModelAuditLog, 0)
	if err != nil {
		log.Printf("Error trying to get audit logs %v", err)
		return scrubedLogs, err
	}
	if response.StatusCode() != http.StatusOK {
		return scrubedLogs, fmt.Errorf("error trying to get audit logs %d", response.StatusCode())
	}

	for _, logEntry := range *response.JSON200.Data.Logs {
		// TODO SCRUB LOG
		scrubedLogs = append(scrubedLogs, logEntry)
	}
	return scrubedLogs, nil
}
