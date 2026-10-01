#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Pushes one tagged container image and returns its immutable registry reference.

.DESCRIPTION
Authenticates to a container registry, pushes an already-tagged local image, extracts
the registry digest, and logs out during cleanup. The registry token must be provided
through the CONTAINER_REGISTRY_TOKEN process environment variable.

.PARAMETER Image
Full registry image name including its tag.

.PARAMETER Registry
Container registry host. The default is ghcr.io.

.PARAMETER RegistryUsername
Username used for registry authentication.

.OUTPUTS
The immutable image reference in the form <registry-image>@sha256:<digest>.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Image,

    [ValidateNotNullOrEmpty()]
    [string] $Registry = 'ghcr.io',

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RegistryUsername
)

$ErrorActionPreference = 'Stop'
$tokenVariableName = 'CONTAINER_REGISTRY_TOKEN'
$loggedIn = $false

if ($Registry -cne $Registry.ToLowerInvariant()) {
    throw 'Registry must use lowercase characters.'
}

if ($Registry.Contains('/')) {
    throw 'Registry must contain only the registry host.'
}

$registryPrefix = "$Registry/"
if (-not $Image.StartsWith($registryPrefix, [StringComparison]::Ordinal)) {
    throw "Image must belong to the $Registry registry."
}

if ($Image.Contains('@')) {
    throw 'Image must use a tag, not a digest.'
}

$lastSlash = $Image.LastIndexOf('/')
$tagSeparator = $Image.LastIndexOf(':')
if ($tagSeparator -le $lastSlash) {
    throw 'Image must include a tag.'
}

$imageRepository = $Image.Substring(0, $tagSeparator)
$imageTag = $Image.Substring($tagSeparator + 1)
if ($imageRepository -cne $imageRepository.ToLowerInvariant()) {
    throw 'The image repository must use lowercase characters.'
}

if ($imageTag -notmatch '^git-[0-9a-f]{40}-run-[1-9][0-9]*-attempt-[1-9][0-9]*$') {
    throw 'Image must use a git-<full-commit-sha>-run-<run-id>-attempt-<run-attempt> tag.'
}

$token = [Environment]::GetEnvironmentVariable($tokenVariableName, 'Process')
if ([string]::IsNullOrWhiteSpace($token)) {
    throw "$tokenVariableName is required."
}

try {
    & docker image inspect $Image *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Local image not found: $Image"
    }

    $loginOutput = $token | & docker login $Registry --username $RegistryUsername --password-stdin 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker login to $Registry failed."
    }
    $loggedIn = $true
    $loginOutput | ForEach-Object { Write-Verbose $_.ToString() }

    $token = $null
    [Environment]::SetEnvironmentVariable($tokenVariableName, $null, 'Process')

    $pushOutput = @(& docker image push $Image 2>&1)
    $pushExitCode = $LASTEXITCODE
    if ($pushExitCode -ne 0) {
        $pushOutput | ForEach-Object { Write-Warning $_.ToString() }
        throw "Docker push failed for $Image."
    }
    $pushOutput | ForEach-Object { Write-Verbose $_.ToString() }

    $pushText = ($pushOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    $digestMatch = [regex]::Match(
        $pushText,
        'digest:\s*(sha256:[0-9a-f]{64})',
        [Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if (-not $digestMatch.Success) {
        throw 'Docker push succeeded but did not return an image digest.'
    }

    $digest = $digestMatch.Groups[1].Value.ToLowerInvariant()
    Write-Output ('{0}@{1}' -f $imageRepository, $digest)
}
finally {
    $token = $null
    [Environment]::SetEnvironmentVariable($tokenVariableName, $null, 'Process')

    if ($loggedIn) {
        $logoutOutput = @(& docker logout $Registry 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Docker logout from $Registry failed."
        }
        else {
            $logoutOutput | ForEach-Object { Write-Verbose $_.ToString() }
        }
    }
}
