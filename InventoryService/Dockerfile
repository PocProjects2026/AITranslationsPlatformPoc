# syntax=docker/dockerfile:1@sha256:87999aa3d42bdc6bea60565083ee17e86d1f3339802f543c0d03998580f9cb89

FROM mcr.microsoft.com/dotnet/sdk:10.0.102-noble@sha256:6ba533cc61a5d8c5e7d4b3a3e33e2ddc2efef200b112e4d658303516bfd24255 AS build

ARG APP_VERSION=0.1.0
WORKDIR /src

COPY global.json Directory.Build.props NuGet.Config ./
COPY src/InventoryService.Api/InventoryService.Api.csproj src/InventoryService.Api/packages.lock.json src/InventoryService.Api/
RUN dotnet restore src/InventoryService.Api/InventoryService.Api.csproj \
    --configfile NuGet.Config \
    --locked-mode

COPY translation-artifacts/local/ translation-artifacts/local/
COPY src/InventoryService.Api/ src/InventoryService.Api/
RUN dotnet publish src/InventoryService.Api/InventoryService.Api.csproj \
    --configuration Release \
    --no-restore \
    --output /app/publish \
    -p:ContinuousIntegrationBuild=true \
    -p:Version="${APP_VERSION}"

FROM mcr.microsoft.com/dotnet/aspnet:10.0.10-noble@sha256:f1126d438ccc359f51cc6d4701a8deae513856cf10f5fe645d29ea6403dcac6b AS runtime

ARG APP_VERSION=0.1.0
ARG GIT_COMMIT=local

RUN apt-get update \
    && apt-get install --yes --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /app/publish/ ./

ENV Application__GitCommit=${GIT_COMMIT} \
    ASPNETCORE_HTTP_PORTS=8080 \
    DOTNET_EnableDiagnostics=0

LABEL org.opencontainers.image.source="https://github.com/PocProjects2026/AITranslationsPlatformPoc" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

EXPOSE 8080
USER $APP_UID

ENTRYPOINT ["dotnet", "InventoryService.Api.dll"]
