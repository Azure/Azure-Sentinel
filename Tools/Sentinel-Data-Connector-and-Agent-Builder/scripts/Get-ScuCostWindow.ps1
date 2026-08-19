<#
.SYNOPSIS
    Computes Security Copilot SCU cost-window context for the current clock hour.

.DESCRIPTION
    SCU provisioned-capacity is billed in WHOLE clock-hour blocks aligned to the
    wall clock (9:00-10:00, 10:00-11:00 UTC), NOT rolling 60-min windows. See:
        https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed

    Two laws follow from this billing model:

      (1) HOUR-CROSSING LAW
          Create at 8:40, delete at 9:30 -> spans 2 blocks -> $8 (not $4).
          Create at 9:01, delete at 9:48 -> spans 1 block  -> $4.

      (2) SAME-HOUR RE-CREATE LAW
          Create -> delete -> create within one clock-hour bills TWO SCU-hours
          for the same block ($8 for ~1 hr of wall-clock testing).

    This helper is pure-additive context. It does not create, delete, or modify
    any Azure resource. The agent chat calls it BEFORE every SCU
    create/delete decision and surfaces its `recommendation` field to the
    developer. The Ensure-SccCapacity.ps1 / Remove-SccCapacity.ps1 scripts also
    use its `recommendedDeleteAtFor1HrBudget` field to align their auto-delete
    timers to the :48 of the last paid clock hour.

.PARAMETER HoursOfBudget
    Number of CLOCK-HOUR blocks the developer wants to pay for in this session.
    Default 1 (~$4 for 1 SCU at standard rate). The helper computes
    `recommendedDeleteAtForNHrBudget = startOfHour(now) + N hours - 12 min`
    (the 12-min cushion absorbs the SCU delete (a long-running operation) trailing ~10-min backend
    deprovisioning settlement before the next hour rolls over and silently
    adds another $4 to the bill).

.PARAMETER DeleteBufferMinutes
    Minutes before the next clock-hour boundary at which the auto-delete is
    aligned (default 12 -> :48). SCU delete is an async long-running operation whose final billing
    settlement lands ~10 min after the delete request; the 12-min cushion keeps
    that settlement inside the paid block. Lower to e.g. 15 (:45) for extra
    safety at the cost of ~3 fewer testing minutes.

.PARAMETER Units
    Number of SCUs the developer plans to provision. Default 1. Used only to
    project the dollar cost in the recommendation text; does not affect timing.

.PARAMETER ScuPerHourUsd
    USD per SCU per clock hour. Default 4. Override for non-standard pricing.

.PARAMETER BlockTierMinutes
    minutesRemainingThisHour < this value -> tier = 'block-creation'.
    Default 15.

.PARAMETER SoftWarnTierMinutes
    minutesRemainingThisHour < this value -> tier = 'soft-warn'.
    Default 30. (15-30 min range is the soft-warn band.)

.PARAMETER NowOverride
    ISO-8601 timestamp to use INSTEAD of `Get-Date`. Used by tests / synthetic
    runs to verify the tier math at fixed clock positions (8:30, 8:46, 9:05,
    9:55, etc.). When omitted, current UTC time is used.

.PARAMETER PreviousDeleteAt
    ISO-8601 timestamp of the most recent SCU delete in this session, if any.
    Used to flag the SAME-HOUR RE-CREATE risk (law #2 above). The
    agent should pass this from progress.json.sccCapacityRecentlyDeleted when
    the developer types `create scu` shortly after a `delete scu`.

.PARAMETER Json
    Emit pure JSON to stdout (one object). When omitted, the script prints
    a human-readable summary AND emits the JSON.

.OUTPUTS
    JSON object (and PowerShell hashtable when called from another .ps1):
    {
      "nowUtc":                         "<ISO>",
      "currentHourStart":               "<ISO>",  # top of the current clock hour
      "currentHourEnd":                 "<ISO>",  # top of the next clock hour
      "minutesElapsedThisHour":         <int 0..59>,
      "minutesRemainingThisHour":       <int 1..60>,
      "hoursOfBudget":                  <int>,
      "recommendedCreateAt":            "<ISO>",  # next :01 if wait recommended; nowUtc otherwise
      "recommendedDeleteAtForNHrBudget":"<ISO>",  # startOfHour + N hours - 12 min, floor = now+5min
      "tier":                           "block-creation" | "soft-warn" | "proceed",
      "reasoning":                      "<one-line plain-English explanation>",
      "waitMinutesToNextHour":          <int 0..59>,
      "estimatedBillIfCreateNowUsd":    <int>,  # if create now + delete at recommendedDelete -> dollars
      "estimatedBillIfWaitAndCreateUsd":<int>,  # if wait to :01 + delete at :48 of last paid hour
      "estimatedWallClockMinutesIfCreateNow":   <int>,
      "estimatedWallClockMinutesIfWaitAndCreate":<int>,
      "sameHourRecreateRisk":           $true | $false,  # true iff PreviousDeleteAt is in the current clock-hour block
      "scuPerHourUsd":                  4,
      "billingDocUrl":                  "https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed",
      "recommendation":                 "<the verbatim chat block the agent should surface>"
    }

.EXITCODES
    0  Always (this is a pure-computation helper; never fails the chat flow).

.EXAMPLE
    ./scripts/Get-ScuCostWindow.ps1 -Json
    # -> live cost-window context for the current clock hour

.EXAMPLE
    ./scripts/Get-ScuCostWindow.ps1 -NowOverride '2026-06-10T14:30:00Z' -Json
    # -> synthetic context for 14:30 UTC (verifies the soft-warn tier)

.EXAMPLE
    ./scripts/Get-ScuCostWindow.ps1 -HoursOfBudget 2 -Units 2
    # -> 2 SCU * 2 hour blocks recommendation; recommendedDeleteAt is :48 of the (next-hour+1)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [int]$HoursOfBudget = 1,
    [Parameter(Mandatory=$false)] [int]$Units = 1,
    [Parameter(Mandatory=$false)] [int]$ScuPerHourUsd = 4,
    [Parameter(Mandatory=$false)] [int]$BlockTierMinutes = 15,
    [Parameter(Mandatory=$false)] [int]$SoftWarnTierMinutes = 30,
    [Parameter(Mandatory=$false)] [int]$DeleteBufferMinutes = 12,
    [Parameter(Mandatory=$false)] [string]$NowOverride,
    [Parameter(Mandatory=$false)] [string]$PreviousDeleteAt,
    [Parameter(Mandatory=$false)] [switch]$Json
)

$ErrorActionPreference = 'Stop'

# -------- 1. Resolve `now` (live or synthetic for tests) ---------------------
if ($NowOverride) {
    try {
        $now = [datetime]::Parse($NowOverride).ToUniversalTime()
    } catch {
        throw "Invalid -NowOverride '$NowOverride'. Must be ISO-8601 (e.g., 2026-06-10T14:30:00Z)."
    }
} else {
    $now = (Get-Date).ToUniversalTime()
}

if ($HoursOfBudget -lt 1) { $HoursOfBudget = 1 }
if ($Units -lt 1) { $Units = 1 }

# -------- 2. Clock-hour block boundaries -------------------------------------
# Strip minutes/seconds/ms to get the top of the current clock hour.
$currentHourStart = $now.Date.AddHours($now.Hour)
$currentHourEnd   = $currentHourStart.AddHours(1)

$minutesElapsed    = [int]($now - $currentHourStart).TotalMinutes
$minutesRemaining  = 60 - $minutesElapsed
if ($minutesRemaining -lt 1)  { $minutesRemaining = 1 }
if ($minutesRemaining -gt 60) { $minutesRemaining = 60 }

# -------- 3. Tier classification ---------------------------------------------
$tier = 'proceed'
if     ($minutesRemaining -lt $BlockTierMinutes)    { $tier = 'block-creation' }
elseif ($minutesRemaining -le $SoftWarnTierMinutes) { $tier = 'soft-warn' }

# -------- 4. Same-hour re-create risk ----------------------------------------
$sameHourRecreate = $false
if ($PreviousDeleteAt) {
    try {
        $prevDel = [datetime]::Parse($PreviousDeleteAt).ToUniversalTime()
        if ($prevDel -ge $currentHourStart -and $prevDel -lt $currentHourEnd) {
            $sameHourRecreate = $true
        }
    } catch { }
}

# -------- 5. Recommended timings ---------------------------------------------
# recommendedCreateAt:
#   - block-creation tier OR same-hour-re-create -> next :01 (avoid hour cross / double-bill)
#   - soft-warn / proceed                        -> now
$nextHourStart = $currentHourEnd
$nextHourOne   = $nextHourStart.AddMinutes(1)  # :01 of next hour (safety margin from :00)

$recommendedCreateAt = $now
if ($tier -eq 'block-creation' -or $sameHourRecreate) {
    $recommendedCreateAt = $nextHourOne
}

# recommendedDeleteAtForNHrBudget:
#   startOfHour + N hours - DeleteBufferMinutes (default 12 -> :48 of the last
#   paid clock hour). The 12-min cushion absorbs the SCU delete (a long-running operation) trailing ~10-min
#   backend deprovisioning settlement so the final "Capacities_Delete Succeeded"
#   event lands BEFORE the next clock hour rolls (a :55/-5min delete settles ~:05
#   of the next block and double-bills $4 -> $8).
#   FLOOR at now + 5 min (don't propose a delete in the past or too close to now).
#   If proposed time is too close, push by one hour at a time until safe.
$proposedDelete = $currentHourStart.AddHours($HoursOfBudget).AddMinutes(-$DeleteBufferMinutes)
$minSafeDelete  = $now.AddMinutes(5)
while ($proposedDelete -lt $minSafeDelete) {
    $proposedDelete = $proposedDelete.AddHours(1)
}
$recommendedDeleteAt = $proposedDelete

# -------- 6. Cost / wall-clock projection ------------------------------------
# CREATE NOW: spans from now to recommendedDeleteAt -> bills every clock hour touched.
# WAIT AND CREATE: spans from nextHourOne to (nextHourOne's-block + (N-1) hours).:48 -> bills N hours exactly.
function Get-BlocksTouched($from, $to) {
    $fromHour = $from.Date.AddHours($from.Hour)
    $toHour   = $to.Date.AddHours($to.Hour)
    # If the deletion lands at :48 (i.e., still in $toHour block), blocks = (toHour - fromHour)/1h + 1
    $blocks = [int](($toHour - $fromHour).TotalHours) + 1
    if ($blocks -lt 1) { $blocks = 1 }
    return $blocks
}

$blocksCreateNow      = Get-BlocksTouched $now $recommendedDeleteAt
$billCreateNowUsd     = $blocksCreateNow * $Units * $ScuPerHourUsd

# Wait-and-create: starts at nextHourOne, deletes at :48 of the (N-th) subsequent hour.
$waitDeleteAt          = $nextHourOne.Date.AddHours($nextHourOne.Hour).AddHours($HoursOfBudget).AddMinutes(-$DeleteBufferMinutes)
$blocksWaitAndCreate   = Get-BlocksTouched $nextHourOne $waitDeleteAt
$billWaitAndCreateUsd  = $blocksWaitAndCreate * $Units * $ScuPerHourUsd

$wallClockMinCreateNow      = [int](($recommendedDeleteAt - $now).TotalMinutes)
$wallClockMinWaitAndCreate  = [int](($waitDeleteAt - $nextHourOne).TotalMinutes)
if ($wallClockMinCreateNow -lt 0) { $wallClockMinCreateNow = 0 }

# -------- 7. Compose reasoning + recommendation text -------------------------
$reasoning = switch ($tier) {
    'block-creation' {
        "minutesRemainingThisHour=$minutesRemaining (< $BlockTierMinutes) -> creating now spans 2+ clock-hour blocks; bill ${blocksCreateNow}x = `$$billCreateNowUsd vs. `$$billWaitAndCreateUsd if you wait $($minutesRemaining + 1) min to $($nextHourOne.ToString('HH:mm')) UTC."
    }
    'soft-warn' {
        "minutesRemainingThisHour=$minutesRemaining ($BlockTierMinutes-$SoftWarnTierMinutes band) -> create-now gives $wallClockMinCreateNow min for `$$billCreateNowUsd; wait $($minutesRemaining + 1) min and you get $wallClockMinWaitAndCreate min for the same `$$billWaitAndCreateUsd."
    }
    'proceed' {
        "minutesRemainingThisHour=$minutesRemaining (> $SoftWarnTierMinutes) -> creating now gives $wallClockMinCreateNow min of paid testing for `$$billCreateNowUsd; no hour-cross risk."
    }
}
if ($sameHourRecreate) {
    $reasoning = "SAME-HOUR RE-CREATE DETECTED (previous delete at $PreviousDeleteAt is inside the current clock-hour block) -> re-creating now bills a SECOND SCU-hour for the $($currentHourStart.ToString('HH:mm'))-$($currentHourEnd.ToString('HH:mm')) UTC block. " + $reasoning
}

# Compose the verbatim chat block the agent should surface to the developer.
$createNowLabel = "$($now.ToString('HH:mm')) UTC -> delete $($recommendedDeleteAt.ToString('HH:mm')) UTC"
$waitLabel      = "wait $($minutesRemaining + 1) min -> create $($nextHourOne.ToString('HH:mm')) UTC -> delete $($waitDeleteAt.ToString('HH:mm')) UTC"

$recommendation = @()
$recommendation += "Cost-window check: it is $($now.ToString('HH:mm')) UTC with $minutesRemaining min remaining in the current $($currentHourStart.ToString('HH:mm'))-$($currentHourEnd.ToString('HH:mm')) clock-hour block."
$recommendation += ""
$recommendation += "| Option | Testing time | Bill |"
$recommendation += "|---|---|---|"
$recommendation += "| Create now ($createNowLabel) | $wallClockMinCreateNow min | `$$billCreateNowUsd |"
$recommendation += "| Wait and create ($waitLabel) | $wallClockMinWaitAndCreate min | `$$billWaitAndCreateUsd |"
$recommendation += ""
switch ($tier) {
    'block-creation' {
        $recommendation += "Recommendation: WAIT. Creating now $(if ($blocksCreateNow -gt 1) { "spans $blocksCreateNow clock-hour blocks and " })bills `$$billCreateNowUsd vs. `$$billWaitAndCreateUsd if you wait $($minutesRemaining + 1) min."
    }
    'soft-warn' {
        $recommendation += "Recommendation: WAIT is better value (same `$$billWaitAndCreateUsd, ~$([math]::Round($wallClockMinWaitAndCreate / [math]::Max(1, $wallClockMinCreateNow), 1))x the testing time)."
    }
    'proceed' {
        $recommendation += "Recommendation: CREATE NOW is fine ($wallClockMinCreateNow min of paid testing for `$$billCreateNowUsd; no hour-cross risk)."
    }
}
if ($sameHourRecreate) {
    $recommendation += ""
    $recommendation += "WARNING (same-hour re-create): you deleted a previous SCU at $PreviousDeleteAt -- the current clock-hour block is already paid for in your bill. Re-creating now bills a SECOND SCU-hour for the SAME block. The 'wait and create' option above avoids this; 'create now' will double-bill the current hour."
}
$recommendation += ""
$recommendation += "Billing model: SCU provisioned capacity is billed in WHOLE clock-hour blocks. See $($billingDocUrl = 'https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed')."

$recommendationText = ($recommendation -join "`n")

# -------- 8. Build output object --------------------------------------------
$result = [ordered]@{
    nowUtc                                  = $now.ToString('o')
    currentHourStart                        = $currentHourStart.ToString('o')
    currentHourEnd                          = $currentHourEnd.ToString('o')
    minutesElapsedThisHour                  = $minutesElapsed
    minutesRemainingThisHour                = $minutesRemaining
    hoursOfBudget                           = $HoursOfBudget
    units                                   = $Units
    recommendedCreateAt                     = $recommendedCreateAt.ToString('o')
    recommendedDeleteAtForNHrBudget         = $recommendedDeleteAt.ToString('o')
    tier                                    = $tier
    reasoning                               = $reasoning
    waitMinutesToNextHour                   = $minutesRemaining + 1
    estimatedBillIfCreateNowUsd             = $billCreateNowUsd
    estimatedBillIfWaitAndCreateUsd         = $billWaitAndCreateUsd
    estimatedWallClockMinutesIfCreateNow    = $wallClockMinCreateNow
    estimatedWallClockMinutesIfWaitAndCreate= $wallClockMinWaitAndCreate
    blocksTouchedIfCreateNow                = $blocksCreateNow
    blocksTouchedIfWaitAndCreate            = $blocksWaitAndCreate
    sameHourRecreateRisk                    = $sameHourRecreate
    previousDeleteAt                        = $PreviousDeleteAt
    scuPerHourUsd                           = $ScuPerHourUsd
    billingDocUrl                           = 'https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed'
    recommendation                          = $recommendationText
}

# -------- 9. Emit ------------------------------------------------------------
if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host ""
    Write-Host "=== SCU Cost-Window Check ===" -ForegroundColor Cyan
    Write-Host "Now (UTC):                $($result.nowUtc)"
    Write-Host "Current clock-hour block: $($currentHourStart.ToString('HH:mm'))-$($currentHourEnd.ToString('HH:mm')) UTC"
    Write-Host "Minutes remaining:        $minutesRemaining"
    Write-Host "Tier:                     $tier" -ForegroundColor $(if ($tier -eq 'block-creation') { 'Red' } elseif ($tier -eq 'soft-warn') { 'Yellow' } else { 'Green' })
    if ($sameHourRecreate) {
        Write-Host "Same-hour re-create risk: TRUE" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host $recommendationText
    Write-Host ""
    Write-Host "--- machine-readable JSON ---" -ForegroundColor DarkGray
    $result | ConvertTo-Json -Depth 8
}
