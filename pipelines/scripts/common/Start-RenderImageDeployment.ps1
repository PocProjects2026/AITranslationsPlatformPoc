#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Starts a Render deployment for an immutable container image.

.DESCRIPTION
Calls a Render deploy hook with an exact container image digest. The secret deploy
hook must be provided through the RENDER_DEPLOY_HOOK_URL process environment variable.

The image repository must match the image repository configured on the Render service.
Render enforces this when it receives the request.

.PARAMETER ImageReference
Immutable container image reference in the form <registry>/<image>@sha256:<digest>.

.OUTPUTS
The Render deployment ID, or the value "queued" when Render accepts the deployment
behind another deployment already in progress.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ImageReference
)

$ErrorActionPreference = 'Stop'
$hookVariableName = 'RENDER_DEPLOY_HOOK_URL'
$imagePattern = '^[a-z0-9.-]+(?::[0-9]+)?/[a-z0-9._/-]+@sha256:[0-9a-f]{64}$'

if ($ImageReference -cne $ImageReference.ToLowerInvariant()) {
    throw 'ImageReference must use lowercase characters.'
}

if ($ImageReference -notmatch $imagePattern) {
    throw 'ImageReference must contain a registry, repository, and sha256 digest.'
}

$hookValue = [Environment]::GetEnvironmentVariable($hookVariableName, 'Process')
if ([string]::IsNullOrWhiteSpace($hookValue)) {
    throw "$hookVariableName is required."
}

$hookUri = $null
if (-not [Uri]::TryCreate($hookValue, [UriKind]::Absolute, [ref] $hookUri)) {
    throw "$hookVariableName must be an absolute URL."
}

if ($hookUri.Scheme -ne [Uri]::UriSchemeHttps) {
    throw "$hookVariableName must use HTTPS."
}

if ($hookUri.Host -ne 'api.render.com') {
    throw "$hookVariableName must use the api.render.com host."
}

$requestUri = [UriBuilder]::new($hookUri)
$encodedImageReference = [Uri]::EscapeDataString($ImageReference)
$existingQuery = $requestUri.Query.TrimStart('?')

if ($existingQuery -match '(^|&)imgURL=') {
    throw "$hookVariableName must not already contain an imgURL parameter."
}

$requestUri.Query = if ([string]::IsNullOrWhiteSpace($existingQuery)) {
    "imgURL=$encodedImageReference"
}
else {
    "$existingQuery&imgURL=$encodedImageReference"
}

Write-Host "Requesting Render deployment for $ImageReference"
$response = Invoke-WebRequest -Method Post -Uri $requestUri.Uri -TimeoutSec 30

if ($response.StatusCode -eq 202) {
    Write-Warning 'Render queued the deployment behind another deployment.'
    Write-Output 'queued'
    return
}

if ($response.StatusCode -ne 200) {
    throw "Render returned unexpected HTTP status $($response.StatusCode)."
}

$responseBody = $response.Content | ConvertFrom-Json
$deployId = $responseBody.deploy.id
if ([string]::IsNullOrWhiteSpace($deployId)) {
    $deployId = $responseBody.id
}

if ([string]::IsNullOrWhiteSpace($deployId)) {
    throw 'Render accepted the deployment but did not return a deployment ID.'
}

Write-Output $deployId
