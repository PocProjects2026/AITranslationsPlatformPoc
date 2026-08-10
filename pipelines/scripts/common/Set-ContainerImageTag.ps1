#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Adds the approved Git commit tag to a local container image.

.DESCRIPTION
Creates a second local name for an already-built image. The target name uses the
registry repository and the full source commit in the form:

    <registry-image>:git-<full-commit-sha>

This script does not authenticate to a registry or push the image.

.PARAMETER LocalImage
Name and tag of the already-built local image.

.PARAMETER RegistryImage
Registry and image repository without a tag or digest.

.PARAMETER GitCommit
Full 40-character Git commit SHA used to build the image.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $LocalImage,

    [Parameter(Mandatory = $true)]
    [string] $RegistryImage,

    [Parameter(Mandatory = $true)]
    [string] $GitCommit
)

$ErrorActionPreference = 'Stop'

if ($GitCommit -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'GitCommit must be a full 40-character hexadecimal Git SHA.'
}

if ($RegistryImage -cne $RegistryImage.ToLowerInvariant()) {
    throw 'RegistryImage must use lowercase characters.'
}

if ($RegistryImage.Contains('@')) {
    throw 'RegistryImage must not include a digest.'
}

$lastSlash = $RegistryImage.LastIndexOf('/')
$lastColon = $RegistryImage.LastIndexOf(':')
if ($lastColon -gt $lastSlash) {
    throw 'RegistryImage must not include a tag.'
}

$normalizedCommit = $GitCommit.ToLowerInvariant()
$targetImage = '{0}:git-{1}' -f $RegistryImage, $normalizedCommit

$sourceImageId = & docker image inspect $LocalImage --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) {
    throw "Local image not found: $LocalImage"
}

Write-Verbose "Adding local image tag $targetImage"
& docker image tag $LocalImage $targetImage
if ($LASTEXITCODE -ne 0) {
    throw "Unable to tag local image $LocalImage."
}

$targetImageId = & docker image inspect $targetImage --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect tagged image $targetImage."
}

if ($targetImageId.Trim() -ne $sourceImageId.Trim()) {
    throw 'The source and tagged image IDs do not match.'
}

Write-Output $targetImage
