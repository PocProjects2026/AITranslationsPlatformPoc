using InventoryService.Translation;

namespace InventoryService.Api.Tests;

public sealed class TranslationCatalogTests
{
    private readonly JsonTranslationCatalog _catalog = new(
        Path.Combine(AppContext.BaseDirectory, "translation-artifacts"),
        "en",
        ["en", "fr", "de"]);

    [Fact]
    public void Get_ReturnsValueFromRequestedLocale()
    {
        var result = _catalog.Get("fr", "inventory.title");

        Assert.Equal("Résumé de l'inventaire", result);
    }

    [Fact]
    public void TryResolveLocale_ResolvesRegionalLocale()
    {
        var found = _catalog.TryResolveLocale("de-CH", out var locale);

        Assert.True(found);
        Assert.Equal("de", locale);
    }
}
