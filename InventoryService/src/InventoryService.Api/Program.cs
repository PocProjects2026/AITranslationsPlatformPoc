using System.Reflection;
using System.Text.RegularExpressions;
using System.Threading.RateLimiting;
using InventoryService.Contracts;
using InventoryService.Reports;
using InventoryService.Translation;
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
builder.Services.AddSingleton<ITranslationCatalog>(_ =>
{
    var relativeDirectory = builder.Configuration["TranslationArtifacts:Directory"]
        ?? throw new InvalidOperationException("TranslationArtifacts:Directory is required.");
    var sourceLocale = builder.Configuration["TranslationArtifacts:SourceLocale"]
        ?? throw new InvalidOperationException("TranslationArtifacts:SourceLocale is required.");
    var supportedLocales = builder.Configuration
        .GetSection("TranslationArtifacts:SupportedLocales")
        .Get<string[]>() ?? throw new InvalidOperationException("TranslationArtifacts:SupportedLocales is required.");
    var artifactDirectory = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, relativeDirectory));

    return new JsonTranslationCatalog(artifactDirectory, sourceLocale, supportedLocales);
});
builder.Services.AddSingleton<IInventorySummaryPdfGenerator>(services =>
{
    PdfFontBootstrapper.Initialize(services.GetRequiredService<IConfiguration>());
    return new InventorySummaryPdfGenerator(services.GetRequiredService<ITranslationCatalog>());
});

var app = builder.Build();

_ = app.Services.GetRequiredService<ITranslationCatalog>();

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

app.MapGet("/locales", (ITranslationCatalog catalog) =>
    TypedResults.Ok(new { locales = catalog.SupportedLocales }));

app.MapPost(
        "/api/reports/inventory-summary",
        (GenerateInventorySummaryRequest request,
            IInventorySummaryPdfGenerator generator,
            ITranslationCatalog translations,
            TimeProvider timeProvider,
            IConfiguration configuration,
            HttpContext httpContext) =>
        {
            var errors = InventorySummaryRequestValidator.Validate(request);
            if (errors.Count > 0)
            {
                return Results.ValidationProblem(errors);
            }

            if (!translations.TryResolveLocale(request.Locale!, out var locale))
            {
                return Results.ValidationProblem(new Dictionary<string, string[]>
                {
                    [nameof(request.Locale)] =
                    [$"Supported locales are: {string.Join(", ", translations.SupportedLocales)}."]
                });
            }

            var generatedAt = request.GeneratedAt ?? timeProvider.GetUtcNow();
            var content = generator.Generate(request, generatedAt, locale);
            var applicationVersion = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "unknown";
            var gitCommit = configuration["Application:GitCommit"] ?? "unknown";
            var safeReportId = Regex.Replace(request.ReportId!, "[^a-zA-Z0-9._-]", "-");
            httpContext.Response.Headers.ContentLanguage = locale;

            app.Logger.LogInformation(
                "Generated inventory summary {ReportId} in {Locale} with {ItemCount} items",
                request.ReportId,
                locale,
                request.Items!.Count);

            return Results.File(
                content,
                "application/pdf",
                fileDownloadName: $"inventory-summary-{safeReportId}.{locale}.pdf",
                lastModified: generatedAt,
                entityTag: new Microsoft.Net.Http.Headers.EntityTagHeaderValue(
                    $"\"{applicationVersion}-{gitCommit}-{locale}\""));
        })
    .RequireRateLimiting("pdf-generation")
    .WithRequestTimeout("pdf-generation");

app.Run();

public partial class Program;
