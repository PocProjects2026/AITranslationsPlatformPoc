#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Runs the standard CI validation for a .NET service.

.DESCRIPTION
Restores locked dependencies, verifies formatting, builds in the selected
configuration, and runs the service tests. The script is intentionally independent
of GitHub Actions so the same commands can be reproduced locally.

.PARAMETER ServicePath
Path to the service directory, relative to the current directory or absolute.

.PARAMETER SolutionFile
Solution filename relative to ServicePath.

.PARAMETER NuGetConfig
NuGet configuration filename relative to ServicePath.

.PARAMETER Configuration
.NET build configuration. The default is Release.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ServicePath,

    [Parameter(Mandatory = $true)]
    [string] $SolutionFile,

    [string] $NuGetConfig = 'NuGet.Config',

    [string] $Configuration = 'Release'
)

$ErrorActionPreference = 'Stop'

function Invoke-DotNetCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    Write-Host "dotnet $($Arguments -join ' ')"
    & dotnet @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "dotnet command failed with exit code $LASTEXITCODE."
    }
}

$serviceRoot = (Resolve-Path -LiteralPath $ServicePath).Path
$solutionPath = Join-Path $serviceRoot $SolutionFile
$nuGetConfigPath = Join-Path $serviceRoot $NuGetConfig

if (-not (Test-Path -LiteralPath $solutionPath -PathType Leaf)) {
    throw "Solution file not found: $solutionPath"
}

if (-not (Test-Path -LiteralPath $nuGetConfigPath -PathType Leaf)) {
    throw "NuGet configuration not found: $nuGetConfigPath"
}

Push-Location $serviceRoot
try {
    Invoke-DotNetCommand @(
        'restore', $SolutionFile,
        '--configfile', $NuGetConfig,
        '--locked-mode'
    )

    Invoke-DotNetCommand @(
        'format', $SolutionFile,
        '--no-restore',
        '--verify-no-changes'
    )

    Invoke-DotNetCommand @(
        'build', $SolutionFile,
        '--configuration', $Configuration,
        '--no-restore'
    )

    Invoke-DotNetCommand @(
        'test', $SolutionFile,
        '--configuration', $Configuration,
        '--no-build',
        '--no-restore'
    )
}
finally {
    Pop-Location
}
