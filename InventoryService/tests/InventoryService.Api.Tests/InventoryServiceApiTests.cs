using System.Net;
using System.Net.Http.Json;
using InventoryService.Contracts;
using Microsoft.AspNetCore.Mvc.Testing;

namespace InventoryService.Api.Tests;

public sealed class InventoryServiceApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public InventoryServiceApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task Health_ReturnsHealthy()
    {
        using var response = await _client.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("Healthy", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Version_ReturnsApplicationIdentity()
    {
        using var response = await _client.GetAsync("/version");
        var result = await response.Content.ReadFromJsonAsync<VersionResponse>();

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.NotNull(result);
        Assert.NotEmpty(result.ApplicationVersion);
        Assert.Equal("local", result.GitCommit);
    }

    [Fact]
    public async Task Locales_ReturnsPackagedTranslationLocales()
    {
        using var response = await _client.GetAsync("/locales");
        var content = await response.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Contains("\"de\"", content, StringComparison.Ordinal);
        Assert.Contains("\"en\"", content, StringComparison.Ordinal);
        Assert.Contains("\"fr\"", content, StringComparison.Ordinal);
    }

    [Fact]
    public async Task GenerateInventorySummary_ReturnsPdf()
    {
        var request = CreateValidRequest();

        using var response = await _client.PostAsJsonAsync("/api/reports/inventory-summary", request);
        var content = await response.Content.ReadAsByteArrayAsync();

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("application/pdf", response.Content.Headers.ContentType?.MediaType);
        Assert.Equal("inventory-summary-INV-001.pdf", response.Content.Headers.ContentDisposition?.FileNameStar);
        Assert.Equal("%PDF-", System.Text.Encoding.ASCII.GetString(content, 0, 5));
    }

    [Fact]
    public async Task GenerateInventorySummary_WithNoItems_ReturnsValidationProblem()
    {
        var request = CreateValidRequest() with { Items = [] };

        using var response = await _client.PostAsJsonAsync("/api/reports/inventory-summary", request);

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Equal("application/problem+json", response.Content.Headers.ContentType?.MediaType);
    }

    private static GenerateInventorySummaryRequest CreateValidRequest() =>
        new(
            "INV-001",
            "Casablanca Warehouse",
            [
                new InventoryItemRequest("PAPER-A4", "A4 paper", 120, "boxes"),
                new InventoryItemRequest("TONER-BK", "Black toner", 8, "units")
            ],
            new DateTimeOffset(2026, 8, 9, 10, 0, 0, TimeSpan.Zero));
}
