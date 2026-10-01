#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Builds a versioned Docker image for a service.

.DESCRIPTION
Builds an image from a service context and passes the application version and exact
Git commit to the Dockerfile. Publishing is deliberately outside this script.

.PARAMETER ContextPath
Docker build context, relative to the current directory or absolute.

.PARAMETER ImageName
Local image name and tag to create.

.PARAMETER AppVersion
Application version recorded in the image and application metadata.

.PARAMETER GitCommit
Exact Git commit recorded in the image and application metadata.

.PARAMETER Dockerfile
Dockerfile path relative to ContextPath.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ContextPath,

    [Parameter(Mandatory = $true)]
    [string] $ImageName,

    [Parameter(Mandatory = $true)]
    [string] $AppVersion,

    [Parameter(Mandatory = $true)]
    [string] $GitCommit,

    [string] $Dockerfile = 'Dockerfile'
)

$ErrorActionPreference = 'Stop'

$contextRoot = (Resolve-Path -LiteralPath $ContextPath).Path
$dockerfilePath = Join-Path $contextRoot $Dockerfile

if (-not (Test-Path -LiteralPath $dockerfilePath -PathType Leaf)) {
    throw "Dockerfile not found: $dockerfilePath"
}

$dockerArguments = @(
    'build',
    '--file', $dockerfilePath,
    '--build-arg', "APP_VERSION=$AppVersion",
    '--build-arg', "GIT_COMMIT=$GitCommit",
    '--tag', $ImageName,
    $contextRoot
)

Write-Host "Building image $ImageName from $contextRoot"
& docker @dockerArguments
if ($LASTEXITCODE -ne 0) {
    throw "docker build failed with exit code $LASTEXITCODE."
}
