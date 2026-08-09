using System.Reflection;
using System.Text.RegularExpressions;
using System.Threading.RateLimiting;
using InventoryService.Contracts;
using InventoryService.Reports;
using InventoryService.Validation;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.RateLimiting;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 64 * 1024);
builder.Services.AddProblemDetails();
builder.Services.AddHealthChecks();
builder.Services.AddRequestTimeouts(options => options.AddPolicy("pdf-generation", TimeSpan.FromSeconds(15)));
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("pdf-generation", limiter =>
    {
        limiter.PermitLimit = 10;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
        limiter.AutoReplenishment = true;
    });
});
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<IInventorySummaryPdfGenerator>(services =>
{
    PdfFontBootstrapper.Initialize(services.GetRequiredService<IConfiguration>());
    return new InventorySummaryPdfGenerator();
});

var app = builder.Build();

app.UseExceptionHandler();
app.UseRequestTimeouts();
app.UseRateLimiter();

app.MapHealthChecks("/health", new HealthCheckOptions { AllowCachingResponses = false });

app.MapGet("/version", (IConfiguration configuration) =>
{
    var applicationVersion = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "unknown";
    var gitCommit = configuration["Application:GitCommit"] ?? "unknown";
    return TypedResults.Ok(new VersionResponse(applicationVersion, gitCommit));
});

app.MapPost(
        "/api/reports/inventory-summary",
        (GenerateInventorySummaryRequest request,
            IInventorySummaryPdfGenerator generator,
            TimeProvider timeProvider,
            IConfiguration configuration) =>
        {
            var errors = InventorySummaryRequestValidator.Validate(request);
            if (errors.Count > 0)
            {
                return Results.ValidationProblem(errors);
            }

            var generatedAt = request.GeneratedAt ?? timeProvider.GetUtcNow();
            var content = generator.Generate(request, generatedAt);
            var applicationVersion = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "unknown";
            var gitCommit = configuration["Application:GitCommit"] ?? "unknown";
            var safeReportId = Regex.Replace(request.ReportId!, "[^a-zA-Z0-9._-]", "-");

            app.Logger.LogInformation(
                "Generated inventory summary {ReportId} with {ItemCount} items",
                request.ReportId,
                request.Items!.Count);

            return Results.File(
                content,
                "application/pdf",
                fileDownloadName: $"inventory-summary-{safeReportId}.pdf",
                lastModified: generatedAt,
                entityTag: new Microsoft.Net.Http.Headers.EntityTagHeaderValue($"\"{applicationVersion}-{gitCommit}\""));
        })
    .RequireRateLimiting("pdf-generation")
    .WithRequestTimeout("pdf-generation");

app.Run();

public partial class Program;
