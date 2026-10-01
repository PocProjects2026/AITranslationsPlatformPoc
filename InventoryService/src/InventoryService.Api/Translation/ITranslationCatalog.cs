namespace InventoryService.Translation;

public interface ITranslationCatalog
{
    IReadOnlyCollection<string> SupportedLocales { get; }

    bool TryResolveLocale(string requestedLocale, out string locale);

    string Get(string locale, string key);
}
