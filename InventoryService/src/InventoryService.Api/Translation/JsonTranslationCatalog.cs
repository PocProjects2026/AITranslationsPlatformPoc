using System.Collections.ObjectModel;
using System.Text.Json;

namespace InventoryService.Translation;

public sealed class JsonTranslationCatalog : ITranslationCatalog
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);
    private readonly IReadOnlyDictionary<string, IReadOnlyDictionary<string, string>> _catalogs;

    public JsonTranslationCatalog(
        string artifactDirectory,
        string sourceLocale,
        IEnumerable<string> supportedLocales)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(artifactDirectory);
        ArgumentException.ThrowIfNullOrWhiteSpace(sourceLocale);
        ArgumentNullException.ThrowIfNull(supportedLocales);

        var normalizedSourceLocale = NormalizeLocale(sourceLocale);
        var locales = supportedLocales.Select(NormalizeLocale).Distinct(StringComparer.Ordinal).ToArray();
        if (locales.Length == 0 || !locales.Contains(normalizedSourceLocale, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("The source locale must be included in the supported locales.");
        }

        var catalogs = locales.ToDictionary(
            locale => locale,
            locale => LoadCatalog(artifactDirectory, locale),
            StringComparer.OrdinalIgnoreCase);

        var sourceKeys = catalogs[normalizedSourceLocale].Keys.ToHashSet(StringComparer.Ordinal);
        foreach (var (locale, catalog) in catalogs)
        {
            if (!sourceKeys.SetEquals(catalog.Keys))
            {
                throw new InvalidOperationException(
                    $"Translation artifact 'backend.{locale}.json' does not contain the same keys as the source artifact.");
            }
        }

        _catalogs = new ReadOnlyDictionary<string, IReadOnlyDictionary<string, string>>(catalogs);
        SupportedLocales = Array.AsReadOnly(locales.Order(StringComparer.Ordinal).ToArray());
    }

    public IReadOnlyCollection<string> SupportedLocales { get; }

    public bool TryResolveLocale(string requestedLocale, out string locale)
    {
        if (string.IsNullOrWhiteSpace(requestedLocale))
        {
            locale = string.Empty;
            return false;
        }

        var normalized = NormalizeLocale(requestedLocale);
        if (_catalogs.ContainsKey(normalized))
        {
            locale = normalized;
            return true;
        }

        var separatorIndex = normalized.IndexOf('-', StringComparison.Ordinal);
        if (separatorIndex > 0 && _catalogs.ContainsKey(normalized[..separatorIndex]))
        {
            locale = normalized[..separatorIndex];
            return true;
        }

        locale = string.Empty;
        return false;
    }

    public string Get(string locale, string key)
    {
        if (!TryResolveLocale(locale, out var resolvedLocale))
        {
            throw new InvalidOperationException($"Locale '{locale}' is not available.");
        }

        return _catalogs[resolvedLocale].TryGetValue(key, out var value)
            ? value
            : throw new KeyNotFoundException($"Translation key '{key}' does not exist.");
    }

    private static IReadOnlyDictionary<string, string> LoadCatalog(string artifactDirectory, string locale)
    {
        var fileName = $"backend.{locale}.json";
        var filePath = Path.Combine(artifactDirectory, fileName);
        if (!File.Exists(filePath))
        {
            throw new InvalidOperationException($"Translation artifact '{fileName}' was not packaged.");
        }

        var values = JsonSerializer.Deserialize<Dictionary<string, string>>(
            File.ReadAllText(filePath),
            JsonOptions) ?? throw new InvalidOperationException($"Translation artifact '{fileName}' is empty.");

        if (values.Count == 0 || values.Any(entry => string.IsNullOrWhiteSpace(entry.Value)))
        {
            throw new InvalidOperationException($"Translation artifact '{fileName}' contains empty values.");
        }

        return new ReadOnlyDictionary<string, string>(
            new Dictionary<string, string>(values, StringComparer.Ordinal));
    }

    private static string NormalizeLocale(string locale) =>
        locale.Trim().Replace('_', '-').ToLowerInvariant();
}
