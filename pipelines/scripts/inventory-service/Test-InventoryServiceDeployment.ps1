#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Verifies a deployed InventoryService version.

.DESCRIPTION
Waits for the public service to become healthy and verifies that its /version endpoint
reports the expected Git commit. This accommodates Render Free cold starts and deploy
time without accepting an older deployment as successful.

.PARAMETER ServiceUrl
HTTPS base URL of the deployed InventoryService.

.PARAMETER GitCommit
Full 40-character Git commit expected from the /version endpoint.

.PARAMETER TimeoutSeconds
Maximum time to wait for the expected deployment. The default is ten minutes.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ServiceUrl,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $GitCommit,

    [ValidateRange(30, 1800)]
    [int] $TimeoutSeconds = 600
)

$ErrorActionPreference = 'Stop'

if ($GitCommit -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'GitCommit must be a full 40-character hexadecimal Git SHA.'
}

$serviceUri = $null
if (-not [Uri]::TryCreate($ServiceUrl, [UriKind]::Absolute, [ref] $serviceUri)) {
    throw 'ServiceUrl must be an absolute URL.'
}

if ($serviceUri.Scheme -ne [Uri]::UriSchemeHttps) {
    throw 'ServiceUrl must use HTTPS.'
}

if (-not [string]::IsNullOrEmpty($serviceUri.UserInfo) -or
    -not [string]::IsNullOrEmpty($serviceUri.Query) -or
    -not [string]::IsNullOrEmpty($serviceUri.Fragment)) {
    throw 'ServiceUrl must not contain credentials, a query, or a fragment.'
}

$baseUrl = $ServiceUrl.TrimEnd('/')
$expectedCommit = $GitCommit.ToLowerInvariant()
$deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
$lastStatus = 'No response received.'

while ([DateTimeOffset]::UtcNow -lt $deadline) {
    try {
        $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 15
        $version = Invoke-RestMethod -Uri "$baseUrl/version" -TimeoutSec 15
        $deployedCommit = $version.gitCommit

        if ($health -eq 'Healthy' -and $deployedCommit -eq $expectedCommit) {
            Write-Host 'InventoryService development deployment is ready.'
            Write-Host "  Service: $baseUrl"
            Write-Host "  Application version: $($version.applicationVersion)"
            Write-Host "  Git commit: $deployedCommit"
            return
        }

        $lastStatus = "Health='$health', Git commit='$deployedCommit'."
    }
    catch {
        $lastStatus = $_.Exception.Message
    }

    Write-Host "Waiting for expected deployment. $lastStatus"
    Start-Sleep -Seconds 10
}

throw "InventoryService did not deploy Git commit '$expectedCommit' within $TimeoutSeconds seconds. Last status: $lastStatus"
