#requires -Version 7.0
#requires -PSEdition Core

<#
.SYNOPSIS
Checks the runtime contract of an InventoryService container image.

.DESCRIPTION
Starts an already-built image and verifies its configured and runtime user, health,
Git metadata, supported locales, and localized PDF endpoint. The container and
temporary PDF are removed even when a check fails.

.PARAMETER ImageName
Local image name and tag to test.

.PARAMETER GitCommit
Git commit expected from the /version endpoint.

.PARAMETER ContainerName
Temporary container name. A process-specific name is used by default.

.PARAMETER HostPort
Local TCP port mapped to container port 8080.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ImageName,

    [Parameter(Mandatory = $true)]
    [string] $GitCommit,

    [string] $ContainerName = "inventory-service-validation-$PID",

    [ValidateRange(1, 65535)]
    [int] $HostPort = 18080
)

$ErrorActionPreference = 'Stop'
$expectedUser = '1654'
$baseUri = "http://127.0.0.1:$HostPort"
$pdfPath = Join-Path ([IO.Path]::GetTempPath()) "$ContainerName-inventory-summary.pdf"

function Invoke-DockerText {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    $output = & docker @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }

    return ($output | Out-String).Trim()
}

try {
    $configuredUser = Invoke-DockerText @(
        'image', 'inspect', $ImageName,
        '--format', '{{.Config.User}}'
    )
    if ($configuredUser -ne $expectedUser) {
        throw "Expected image user $expectedUser, found '$configuredUser'."
    }

    $portMapping = '127.0.0.1:{0}:8080' -f $HostPort
    Invoke-DockerText @(
        'run', '--detach',
        '--name', $ContainerName,
        '--publish', $portMapping,
        $ImageName
    ) | Out-Null

    $health = $null
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "$baseUri/health" -TimeoutSec 2
            if ($health -eq 'Healthy') {
                break
            }
        }
        catch {
            # The service may reject requests while the container is starting.
        }

        Start-Sleep -Seconds 2
    }

    if ($health -ne 'Healthy') {
        throw 'InventoryService did not become healthy within 60 seconds.'
    }

    $runtimeUser = Invoke-DockerText @('exec', $ContainerName, 'id', '-u')
    if ($runtimeUser -ne $expectedUser) {
        throw "Expected runtime user $expectedUser, found '$runtimeUser'."
    }

    $version = Invoke-RestMethod -Uri "$baseUri/version"
    if ($version.gitCommit -ne $GitCommit) {
        throw "Expected Git commit '$GitCommit', found '$($version.gitCommit)'."
    }

    $localeResponse = Invoke-RestMethod -Uri "$baseUri/locales"
    $locales = @($localeResponse.locales)
    if (($locales -join ',') -ne 'de,en,fr') {
        throw "Expected locales 'de,en,fr', found '$($locales -join ',')'."
    }

    $requestBody = @{
        reportId = 'INV-FEATURE-CI'
        warehouseName = 'Feature CI'
        locale = 'fr'
        items = @(
            @{
                sku = 'PAPER-A4'
                name = 'A4 paper'
                quantity = 10
                unit = 'boxes'
            }
        )
    } | ConvertTo-Json -Depth 4

    $requestParameters = @{
        Uri = "$baseUri/api/reports/inventory-summary"
        Method = 'Post'
        ContentType = 'application/json'
        Body = $requestBody
        OutFile = $pdfPath
    }
    Invoke-WebRequest @requestParameters

    $pdfBytes = [IO.File]::ReadAllBytes($pdfPath)
    if ($pdfBytes.Length -lt 5) {
        throw 'Generated PDF is empty.'
    }

    $signature = [Text.Encoding]::ASCII.GetString($pdfBytes, 0, 5)
    if ($signature -ne '%PDF-') {
        throw "Expected PDF signature '%PDF-', found '$signature'."
    }

    Write-Host 'InventoryService container validation passed.'
    Write-Host "  Image user: $configuredUser"
    Write-Host "  Runtime user: $runtimeUser"
    Write-Host "  Git commit: $($version.gitCommit)"
    Write-Host "  Locales: $($locales -join ', ')"
    Write-Host "  PDF signature: $signature"
}
catch {
    Write-Warning 'InventoryService validation failed. Container logs follow.'
    & docker logs $ContainerName 2>$null
    throw
}
finally {
    & docker rm --force $ContainerName 2>$null | Out-Null
    if (Test-Path -LiteralPath $pdfPath) {
        [IO.File]::Delete($pdfPath)
    }
}
