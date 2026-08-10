# Pipeline automation

The `pipelines` folder contains automation used by GitHub Actions and by developers
locally. Workflows should describe **when** a check runs and the order of the jobs.
PowerShell scripts should describe **how** the check is performed.

## Structure

- `scripts/common/` contains technology-level operations that have no service-specific
  assumptions.
- A folder under `scripts/`, such as `scripts/inventory-service/`, contains checks
  that depend on that service's HTTP endpoints or runtime contract.

Keep service-specific assumptions out of `scripts/common/`.

## Prerequisites

- PowerShell 7 (`pwsh`) is required on Windows and Linux.
- Windows PowerShell 5.1 (`powershell.exe`) is not supported.
- Each script expects its native tools, such as .NET or Docker, to be installed.

## Current feature CI mapping

| Workflow step | Script | Responsibility |
| --- | --- | --- |
| Validate .NET service | `scripts/common/Test-DotNetService.ps1` | Locked restore, formatting, build, and tests |
| Build container image | `scripts/common/Build-ContainerImage.ps1` | Reproducible Docker build with version metadata |
| Test InventoryService container | `scripts/inventory-service/Test-InventoryServiceContainer.ps1` | Non-root, health, version, locale, and PDF checks |

The scripts fail immediately when a command or assertion fails. They do not publish an
image, access secrets, or deploy infrastructure.

## InventoryService container identity

Development images will be stored in GitHub Container Registry:

```text
ghcr.io/pocprojects2026/ai-translations-inventory-service
```

Each published image will have:

- a `git-<full-commit-sha>` tag that identifies its source code;
- a Docker-generated `sha256:<digest>` that identifies the exact packaged image.

Deployment and rollback will select the immutable digest. The Git tag is for source
traceability. Moving tags such as `latest` and `develop` are not used.

## Run locally

From the repository root:

~~~powershell
pwsh -NoProfile -File ./pipelines/scripts/common/Test-DotNetService.ps1 `
  -ServicePath ./InventoryService `
  -SolutionFile InventoryService.sln
~~~

To reproduce the container checks:

~~~powershell
$commit = git rev-parse HEAD
pwsh -NoProfile -File ./pipelines/scripts/common/Build-ContainerImage.ps1 `
  -ContextPath ./InventoryService `
  -ImageName inventory-service:local-validation `
  -AppVersion 0.1.0-local `
  -GitCommit $commit

pwsh -NoProfile -File ./pipelines/scripts/inventory-service/Test-InventoryServiceContainer.ps1 `
  -ImageName inventory-service:local-validation `
  -GitCommit $commit
~~~
