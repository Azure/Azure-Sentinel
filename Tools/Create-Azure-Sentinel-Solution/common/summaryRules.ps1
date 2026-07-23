
function ValidateSummaryRulesProperties($yamlData) {
  try {
    # Validate that all required properties are present
    $requiredProperties = @(
        'id', 'displayName', 'description', 'requiredDataConnectors', 
        'destinationTable', 'query', 'binSize', 'version'
    )

    foreach ($property in $requiredProperties) {
        if (-not $yamlData.PSObject.Properties.Match($property)) {
            Write-Error "Missing required property: $property"
            exit 1
        }
    }
  }
  catch {
    Write-Host "ERROR: Error occurred in SummaryRules file, ValidateSummaryRulesProperties function. Error Details: $_" -ForegroundColor Red
    exit 1
  }
}

function GenerateSummaryRules($solutionName, $file, $rawData, $contentResourceDetails) {
  try {
    Write-Host "Generating Summary rules for $file"
    # Parse the YAML content
    $yaml = ConvertFrom-Yaml -Yaml $rawData

    ValidateSummaryRulesProperties -yamlData $yaml

    # Extract values from YAML data
    $displayName = $yaml.displayName
    $description = $yaml.description.Trim();
    if($description.StartsWith("'")) {
      $description = $description.substring(1, $description.length-1)
    }

    if($description.EndsWith("'")) {
      $description = $description.substring(0, $description.length-1)
    }

    #$query = $yaml.query -replace "\\n", ""
    $query = $yaml.query
    $destinationTable = $yaml.destinationTable
    $binSize = $yaml.binSize
    $requiredDataConnectors = $yaml.requiredDataConnectors
    $type = 'Microsoft.OperationalInsights/workspaces/summaryLogs'
    $calculatedSummaryRuleVersion = ($null -ne $yaml.version) ? "$($yaml.version)" : "1.0.0"

    $objSummaryRules = [PSCustomObject]@{}
    $objSummaryRules | Add-Member -NotePropertyName "summaryRuleName$global:summaryRuleCounter" -NotePropertyValue "[concat(parameters('workspace'),'/','$($displayName)')]"
    $objSummaryRules | Add-Member -NotePropertyName "summaryRuleVersion$global:summaryRuleCounter" -NotePropertyValue "$calculatedSummaryRuleVersion"
    $objSummaryRules | Add-Member -NotePropertyName "_summaryRuleContentId$global:summaryRuleCounter" -NotePropertyValue "$($yaml.id)"
    $objSummaryRules | Add-Member -NotePropertyName "summaryRuleTemplateSpecName$global:summaryRuleCounter" -NotePropertyValue "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(parameters('workspace'),'-sr-',uniquestring('$($yaml.id)')))]"
    $global:baseMainTemplate.variables | Add-Member -NotePropertyName "summaryRuleObject$global:summaryRuleCounter" -NotePropertyValue $objSummaryRules

    # Generate ARM template for summaryRule content
    $summaryRuleTemplate = [PSCustomObject]@{
        "type" = $type
        "apiVersion" = $contentResourceDetails.summaryRulesApiVersion
        "name" = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleName$global:summaryRuleCounter]";
        "location" = "[parameters('workspace-location')]"
        "properties" = [PSCustomObject]@{
            "displayName" = $displayName
            "ruleType" = "User"
            "description" = $description
            "ruleDefinition" = [PSCustomObject]@{
                "query" = $query
                "binSize" = $binSize
                "destinationTable" = $destinationTable
            }
            "requiredDataConnectors" = $requiredDataConnectors
        }
    }

    $author = $contentToImport.Author.Split(" - ");
    $authorDetails = [PSCustomObject]@{
        name  = $author[0];
    };
    if($null -ne $author[1])
    {
        $authorDetails | Add-Member -NotePropertyName "email" -NotePropertyValue "[variables('_email')]"
    }

    $summaryRuleMetadataDependencies = [PSCustomObject]@{
      operator = "AND";
      criteria = @();
    };

    foreach ($connector in $requiredDataConnectors) {
      foreach ($dataType in $connector.dataTypes) {
          $criteriaMetadataObject = @{
              contentId = $dataType
              kind      = "DataType"
          }
          $summaryRuleMetadataDependencies.criteria += $criteriaMetadataObject
      }
    }

    $metadataDescription = "Description about $displayName - metadata"
    $metadataProperties = [PSCustomObject]@{
        "description" = $metadataDescription
        "parentId" = "[[resourceId('$($type)', parameters('workspace-name'),variables('workspaceResourceId'))]"
        "contentId" = "[variables('summaryRuleObject$global:summaryRuleCounter')._summaryRuleContentId$global:summaryRuleCounter]"
        "kind" = "SummaryRule"
        "version" = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleVersion$global:summaryRuleCounter]"
        "source" = [PSCustomObject]@{
          "kind" = "Solution"
          "name" = "$solutionName"
          "sourceId" = "[variables('_solutionId')]"
        }
        "author" = $authorDetails
        "support" = $baseMetadata.support
    }

    if ($summaryRuleMetadataDependencies.criteria.Count -gt 0) {
        $metadataProperties | Add-Member -NotePropertyName "dependencies" -NotePropertyValue $summaryRuleMetadataDependencies
    }

    # Generate ARM template for metadata
    $summaryRuleMetadata = [PSCustomObject]@{
      "type" = "Microsoft.OperationalInsights/workspaces/providers/metadata"
      "apiVersion" = $contentResourceDetails.commonResourceMetadataApiVersion
      "name" = "[[concat(parameters('workspace-name'),'/Microsoft.SecurityInsights/',concat('SummaryRule-', last(split(resourceId('$($type)', parameters('workspace-name'),variables('workspaceResourceId')) ,'/'))))]"
      "properties" = $metadataProperties
    }

    # merge content and metadata
    $summaryRuleTemplateContent = [PSCustomObject]@{
      type       =  $contentResourceDetails.subtype;
      apiVersion = $contentResourceDetails.templateSpecsVersionApiVersion;
      name       = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleTemplateSpecName$global:summaryRuleCounter]";
      location   = "[parameters('workspace-location')]";
      dependsOn  = @("$($contentResourceDetails.dependsOn)");
      properties = [PSCustomObject]@{
        description  = "Description about $($displayName) - contentTemplate properties";
        mainTemplate = [PSCustomObject]@{
          '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#";
          contentVersion = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleVersion$global:summaryRuleCounter]";
          parameters     = [PSCustomObject]@{};
          variables      = [PSCustomObject]@{};
          resources      = @(
            # Summary Rule Content
            $summaryRuleTemplate,
            # Summary Rule Metadata
            $summaryRuleMetadata
          )
        };
      }
    }

    # set rest of the properties
    $summaryRuleTemplateContent = SetContentTemplateDefaultValuesToProperties -templateSpecResourceObj $summaryRuleTemplateContent
    $summaryRuleTemplateContent.properties.contentId = "[variables('summaryRuleObject$global:summaryRuleCounter')._summaryRuleContentId$global:summaryRuleCounter]"
    $summaryRuleTemplateContent.properties.contentKind = "SummaryRule"
    $summaryRuleTemplateContent.properties.displayName = "$($displayName)"

    $summaryRuleTemplateContentValue = "[concat(take(variables('_solutionId'),50),'-','$($ContentKindDict.ContainsKey("SummaryRule") ? $ContentKindDict["SummaryRule"] : '')','-', uniqueString(concat(variables('_solutionId'),'-','SummaryRule','-',variables('summaryRuleObject$global:summaryRuleCounter')._summaryRuleContentId$global:summaryRuleCounter,'-', '$($calculatedSummaryRuleVersion)')))]"

    $summaryRuleTemplateContent.properties.contentProductId = "$summaryRuleTemplateContentValue"
    $summaryRuleTemplateContent.properties.id = "$summaryRuleTemplateContentValue"
    $summaryRuleTemplateContent.properties.version = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleVersion$global:summaryRuleCounter]"
    $summaryRuleTemplateContent.PSObject.Properties.Remove('tags')

    $summaryRuleTemplateContent.properties | Add-Member -MemberType NoteProperty -Name "isDeprecated" -Value $false

    $summaryRuleDependencies = [PSCustomObject]@{
      operator = "AND";
      criteria = @();
    };

    $criteriaObject = @{
      contentId = "[variables('summaryRuleObject$global:summaryRuleCounter')._summaryRuleContentId$global:summaryRuleCounter]"
      kind      = "SummaryRule"
    }

    $summaryRuleDependencies.criteria += $criteriaObject
    $summaryRuleTemplateContent.properties | Add-Member -MemberType NoteProperty -Name "dependencies" -Value $summaryRuleDependencies

    $global:DependencyCriteria += [PSCustomObject]@{
      kind      = "SummaryRule";
      contentId = "[variables('summaryRuleObject$global:summaryRuleCounter')._summaryRulecontentId$global:summaryRuleCounter]";
      version   = "[variables('summaryRuleObject$global:summaryRuleCounter').summaryRuleVersion$global:summaryRuleCounter]";
    };

    $global:baseMainTemplate.resources += $summaryRuleTemplateContent;
    $global:summaryRuleCounter += 1
  }
  catch {
    Write-Host "Error occurred in SummaryRules file, GenerateSummaryRules function. Error Details: $_" -ForegroundColor Red
    exit 1
  }
}
