# THIS FILE CONTAIN FUNCTIONS THAT LOGS DATA TO AZURE APPLICATION INSIGHTS FOR GIVEN INSTRUMENTATION KEY
# =================START: APPLICATION INSIGHTS CODE=====================
function global:Convert-ExceptionToAiExceptionDetails
{
    <#
    .SYNOPSIS
        Converts an exception class object into an Application Insights formatted exception details record.

    .DESCRIPTION
        Converts an exception class object into an Application Insights formatted exception details record.

    .PARAMETER Exception
        Specify the actual exception object to send.

    .EXAMPLE
        C:\> Convert-ExceptionToAiExceptionDetails -Exception $Error[0].Exception
        Converts the specified Exception object into an ExceptionDetails record.
    #>
    [CmdletBinding()]
    Param
    (
		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the exception object to send. This should be an actual Exception class and not a PowerShell ErrorRecord.')]
		[System.Exception]
		[ValidateNotNull()]
		$Exception
    )
    Process
    {
        $ExceptionDetails = New-Object -TypeName 'System.Collections.Generic.List[PSCustomObject]';
        $ParentExceptionId = 0;
        while ($true)
        {
            $CurrentExceptionId = $Exception.GetHashCode();

            $exInfo = [PSCustomObject]@{
                'id' = $CurrentExceptionId
                'outerId' = $ParentExceptionId
                'typeName' = ($Exception.GetType().FullName)
                'message' = $Exception.Message
            };

            if( $Exception.TargetSite -and $Exception.TargetSite.Module -and $Exception.TargetSite.Module.Assembly ) {
                $ParsedStack = Convert-StackTraceToAiStackFrames -Assembly $Exception.TargetSite.Module.Assembly.ToString() -StackTrace $Exception.StackTrace;
            } else {
                $ParsedStack = Convert-StackTraceToAiStackFrames -Assembly "Unknown Assembly" -StackTrace "at Missing stack trace";
            }         

            if ($ParsedStack -and $ParsedStack.Count -gt 0)
            {
                $exInfo | Add-Member -MemberType NoteProperty -Name 'hasFullStack' -Value $true;
                #$exInfo | Add-Member -MemberType NoteProperty -Name 'parsedStack' -Value $ParsedStack;
                if ($ParsedStack.GetType().baseType.Name -eq 'Object')
                {
                    $ParsedStackArray = @()
                    $ParsedStackArray += $ParsedStack

                    $exInfo | Add-Member -MemberType NoteProperty -Name 'parsedStack' -Value $ParsedStackArray;
                }
                else 
                {
                    $exInfo | Add-Member -MemberType NoteProperty -Name 'parsedStack' -Value $ParsedStack;
                }
            }

            $ExceptionDetails.Add($exInfo);

            # advance to the next exception in the tree
            if ($Exception.InnerException)
            {
                $Exception = $Exception.InnerException;
                $ParentExceptionId = $CurrentExceptionId;
            }
            else
            {
                break;
            }
        }
        Write-Output -InputObject $ExceptionDetails[0];
    }
}

function global:Convert-StackTraceToAiStackFrames
{
    <#
    .SYNOPSIS
        Converts a strack trace string into an Application Insights formatted stack frame collection.

    .DESCRIPTION
        Converts a strack trace string into an Application Insights formatted stack frame collection.

    .PARAMETER Assembly
        Provide the name and version of the assembly.

    .PARAMETER StackTrace
        Specify the stack trace as a string.

    .EXAMPLE
        C:\> Convert-StackTraceToAiStackFrames -Assembly $Error[0].Exception.TargetSite.Module.Assembly.ToString() -StackTrace $Error[0].Exception.StackTrace
        Converts the stack trace into a stack frame collection.
    #>
    [CmdletBinding()]
    Param
    (
        [Parameter(
            Mandatory=$true,
            HelpMessage="Provide the name and version of the assembly.")]
        [System.String]
        $Assembly,

		[Parameter(Mandatory=$false)]
		[System.String]
		$StackTrace
    )
    Process
    {
        $frames = New-Object -TypeName 'System.Collections.Generic.List[PSCustomObject]';

        if (![System.String]::IsNullOrWhiteSpace($StackTrace))
        {
            $splitStack = $StackTrace.Split([System.Environment]::NewLine);
            $currentLevel = 0;

            foreach ($line in $splitStack)
            {
                if (![System.String]::IsNullOrWhiteSpace($line))
                {
                    $trimmedLine = $line.Trim();

                    if ($trimmedLine.StartsWith("at "))
                    {
                        $frame = [PSCustomObject]@{
                            'level' = $currentLevel
                            'method' = $trimmedLine.Substring(3)
                            'assembly' = $Assembly
                            'line' = 0
                        };

                        $frames.Add($frame);
                        $currentLevel++;
                    }
                }
            }
        }

        Write-Output -InputObject $frames;
    }
}

function global:Send-AppInsightsTraceTelemetry
{
    <#
    .SYNOPSIS
        Sends trace telemetry to an Azure Application Insights instance.
    .DESCRIPTION
        Sends trace telemetry to an Azure Application Insights instance. This function uses the Azure Application Insights REST API instead of a compiled client library, so it works without additional dependencies.
		NOTE: Telemetry ingestion to Azure Application Insights typically has a ~2-3 minute delay due to the eventual-consistency nature of the service.
    .PARAMETER InstrumentationKey
        Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.
    .PARAMETER Message
        Specify the message to log.
    .PARAMETER Severity
        Specify the message severity. Acceptable values are Verbose, Information, Warning, Error, and Critical.
    .PARAMETER CustomProperties
        Optionally specify additional custom properties, in the form of a hashtable (key-value pairs) that should be logged with this telemetry.
    .EXAMPLE
        C:\> Send-AppInsightsTraceTelemetry -InstrumentationKey <guid> -Message 'This is an informational logging message.' -Severity Information
        Sends trace telemetry to application insights.
	.EXAMPLE
        C:\> Send-AppInsightsTraceTelemetry -InstrumentationKey <guid> -Message 'This is a warning logging message.' -Severity Warning -CustomProperties @{ 'CustomProperty1'='abc'; 'CustomProperty2'='xyz' }
        Sends trace telemetry to application insights, with additional custom properties tied to this event.
    #>
    [CmdletBinding()]
    Param
    (
		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.')]
		[System.Guid]
		[ValidateScript({$_ -ne [System.Guid]::Empty})]
		$InstrumentationKey,

		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the message to log.')]
		[System.String]
		[ValidateNotNullOrEmpty()]
		$Message,

        [Parameter(
            Mandatory=$true,
            HelpMessage='Specify the message severity. Acceptable values are Verbose, Information, Warning, Error, and Critical.')]
		[System.String]
		[ValidateSet('Verbose','Information','Warning','Error','Critical')]
		$Severity,

		[Parameter(Mandatory=$false)]
		[Hashtable]
		$CustomProperties
    )
    Process
    {
		# app insights has a single endpoint where all incoming telemetry is processed.
		$AppInsightsIngestionEndpoint = 'https://dc.services.visualstudio.com/v2/track';
		
		# prepare custom properties
		# convert the hashtable to a custom object, if properties were supplied.
		
		if ($PSBoundParameters.ContainsKey('CustomProperties') -and $CustomProperties.Count -gt 0)
		{
			$customPropertiesObj = [PSCustomObject]$CustomProperties;
		}
		else
		{
			$customPropertiesObj = [PSCustomObject]@{};
		}

		# prepare the REST request body schema.
		# NOTE: this schema represents how traces are sent as of the app insights .net client library v2.9.1.
		# newer versions of the library may change the schema over time and this may require an update to match schemas found in newer libraries.
		
		$bodyObject = [PSCustomObject]@{
			'name' = "Microsoft.ApplicationInsights.$InstrumentationKey.Trace"
			'time' = ([System.dateTime]::UtcNow.ToString('o'))
			'iKey' = $InstrumentationKey
			'tags' = [PSCustomObject]@{
				'ai.cloud.roleInstance' = $ENV:COMPUTERNAME
				'ai.internal.sdkVersion' = 'AzurePowerShellPackage'
			}
			'data' = [PSCustomObject]@{
				'baseType' = 'MessageData'
				'baseData' = [PSCustomObject]@{
					'ver' = '2'
					'message' = $Message
                    'severityLevel' = $Severity
					'properties' = $customPropertiesObj
				}
			}
		};

		# convert the body object into a json blob.
		$bodyAsCompressedJson = $bodyObject | ConvertTo-JSON -Depth 10 -Compress;

		# prepare the headers
		$headers = @{
			'Content-Type' = 'application/x-json-stream';
		};

		# send the request
		Invoke-RestMethod -Uri $AppInsightsIngestionEndpoint -Method Post -Headers $headers -Body $bodyAsCompressedJson;
    }
}

function global:Send-AppInsightsEventTelemetry
{
    <#
    .SYNOPSIS
        Sends custom event telemetry to an Azure Application Insights instance.
    .DESCRIPTION
        Sends custom event telemetry to an Azure Application Insights instance. This function uses the Azure Application Insights REST API instead of a compiled client library, so it works without additional dependencies.
		NOTE: Telemetry ingestion to Azure Application Insights typically has a ~2-3 minute delay due to the eventual-consistency nature of the service.
    .PARAMETER InstrumentationKey
        Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.
    .PARAMETER EventName
        Specify the name of your custom event.
    .PARAMETER CustomProperties
        Optionally specify additional custom properties, in the form of a hashtable (key-value pairs) that should be logged with this telemetry.
    .EXAMPLE
        C:\> Send-AppInsightsEventTelemetry -InstrumentationKey <guid> -EventName 'MyEvent1'
        Sends a custom event telemetry to application insights.
	.EXAMPLE
        C:\> Send-AppInsightsEventTelemetry -InstrumentationKey <guid> -EventName 'MyEvent1' -CustomProperties @{ 'CustomProperty1'='abc'; 'CustomProperty2'='xyz' }
        Sends a custom event telemetry to application insights, with additional custom properties tied to this event.
    #>
    [CmdletBinding()]
    Param
    (
		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.')]
		[System.Guid]
		[ValidateScript({$_ -ne [System.Guid]::Empty})]
		$InstrumentationKey,

		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the name of your custom event.')]
		[System.String]
		[ValidateNotNullOrEmpty()]
		$EventName,

		[Parameter(Mandatory=$false)]
		[Hashtable]
		$CustomProperties
    )
    Process
    {
		# app insights has a single endpoint where all incoming telemetry is processed.  
		$AppInsightsIngestionEndpoint = 'https://dc.services.visualstudio.com/v2/track';
		
		# prepare custom properties
		# convert the hashtable to a custom object, if properties were supplied.
		
		if ($PSBoundParameters.ContainsKey('CustomProperties') -and $CustomProperties.Count -gt 0)
		{
			$customPropertiesObj = [PSCustomObject]$CustomProperties;
		}
		else
		{
			$customPropertiesObj = [PSCustomObject]@{};
		}

		$bodyObject = [PSCustomObject]@{
			'name' = "Microsoft.ApplicationInsights.$InstrumentationKey.Event"
			'time' = ([System.dateTime]::UtcNow.ToString('o'))
			'iKey' = $InstrumentationKey
			'tags' = [PSCustomObject]@{
				'ai.cloud.roleInstance' = $ENV:COMPUTERNAME
				'ai.internal.sdkVersion' = 'AzurePowerShellPackage'
			}
			'data' = [PSCustomObject]@{
				'baseType' = 'EventData'
				'baseData' = [PSCustomObject]@{
					'ver' = '2'
					'name' = $EventName
					'properties' = $customPropertiesObj
				}
			}
		};

		# convert the body object into a json blob.
		$bodyAsCompressedJson = $bodyObject | ConvertTo-JSON -Depth 10 -Compress;

		# prepare the headers
		$headers = @{
			'Content-Type' = 'application/x-json-stream';
		};

		# send the request
		Invoke-RestMethod -Uri $AppInsightsIngestionEndpoint -Method Post -Headers $headers -Body $bodyAsCompressedJson;
    }
}

function global:Send-AppInsightsExceptionTelemetry
{
    <#
    .SYNOPSIS
        Sends exception telemetry to an Azure Application Insights instance.
    .DESCRIPTION
        Sends exception telemetry to an Azure Application Insights instance. This function uses the Azure Application Insights REST API instead of a compiled client library, so it works without additional dependencies.
		NOTE: Telemetry ingestion to Azure Application Insights typically has a ~2-3 minute delay due to the eventual-consistency nature of the service.
    .PARAMETER InstrumentationKey
        Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.
    .PARAMETER Exception
        Specify the actual exception object to send.
    .PARAMETER CustomProperties
        Optionally specify additional custom properties, in the form of a hashtable (key-value pairs) that should be logged with this telemetry.
    .EXAMPLE
        C:\> Send-AppInsightsExceptionTelemetry -InstrumentationKey <guid> -Exception $Error[0].Exception
        Sends exception telemetry to application insights for the most recently logged PowerShell Error.
	.EXAMPLE
        C:\> Send-AppInsightsExceptionTelemetry -InstrumentationKey <guid> -Exception $Error[0].Exception -CustomProperties @{ 'CustomProperty1'='abc'; 'CustomProperty2'='xyz' }
        Sends exception telemetry to application insights for the most recently logged PowerShell Error, with additional custom properties.
    #>
    [CmdletBinding()]
    Param
    (
		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the instrumentation key of your Azure Application Insights instance. This determines where the data ends up.')]
		[System.Guid]
		[ValidateScript({$_ -ne [System.Guid]::Empty})]
		$InstrumentationKey,

		[Parameter(
            Mandatory=$true,
            HelpMessage='Specify the exception object to send. This should be an actual Exception class and not a PowerShell ErrorRecord.')]
		[System.Exception]
		[ValidateNotNullOrEmpty()]
		$Exception,

		[Parameter(Mandatory=$false)]
		[Hashtable]
		$CustomProperties
    )
    Process
    {
		$AppInsightsIngestionEndpoint = 'https://dc.services.visualstudio.com/v2/track';
		# prepare custom properties
		# convert the hashtable to a custom object, if properties were supplied.
		if ($PSBoundParameters.ContainsKey('CustomProperties') -and $CustomProperties.Count -gt 0)
		{
			$customPropertiesObj = [PSCustomObject]$CustomProperties;
		}
		else
		{
			$customPropertiesObj = [PSCustomObject]@{};
		}

        # prepare the exceptions info.
        # this parses the exceptions and inner exceptions with stack traces and turns them into a format friendly for app insights.

        $exceptionDetails = Convert-ExceptionToAiExceptionDetails -Exception $Exception;
		$bodyObject = [PSCustomObject]@{
			'name' = "Microsoft.ApplicationInsights.$InstrumentationKey.Exception";
			'time' = ([System.dateTime]::UtcNow.ToString('o'));
			'iKey' = $InstrumentationKey;
			'tags' = [PSCustomObject]@{
				'ai.cloud.roleInstance' = $ENV:COMPUTERNAME
				'ai.internal.sdkVersion' = 'AzurePowerShellPackage';
			}
			'data' = [PSCustomObject]@{
				'baseType' = 'ExceptionData';
				'baseData' = [PSCustomObject]@{
					'ver' = '2';
					'exceptions' = @($exceptionDetails);
					'properties' = $customPropertiesObj;
				}
			}
		};

		# convert the body object into a json blob.
		$bodyAsCompressedJson = $bodyObject | ConvertTo-JSON -Depth 20 -Compress;

		# prepare the headers
		$headers = @{
			'Content-Type' = 'application/x-json-stream';
		};

		# send the request
		Invoke-RestMethod -Uri $AppInsightsIngestionEndpoint -Method Post -Headers $headers -Body $bodyAsCompressedJson;
    }
}


# =================END: APPLICATION INSIGHTS CODE=====================
