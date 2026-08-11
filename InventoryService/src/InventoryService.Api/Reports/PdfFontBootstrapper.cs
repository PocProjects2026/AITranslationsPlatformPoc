using PdfSharp.Fonts;

namespace InventoryService.Reports;

internal static class PdfFontBootstrapper
{
    private static readonly object SyncRoot = new();
    private static bool _initialized;

    public static void Initialize(IConfiguration configuration)
    {
        if (_initialized)
        {
            return;
        }

        lock (SyncRoot)
        {
            if (_initialized)
            {
                return;
            }

            var regularPath = FindFont(
                configuration["Pdf:RegularFontPath"],
                @"C:\Windows\Fonts\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf");
            var boldPath = FindFont(
                configuration["Pdf:BoldFontPath"],
                @"C:\Windows\Fonts\arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf");

            GlobalFontSettings.FontResolver = new PdfFontResolver(regularPath, boldPath);
            _initialized = true;
        }
    }

    private static string FindFont(string? configuredPath, params string[] fallbackPaths)
    {
        var candidates = string.IsNullOrWhiteSpace(configuredPath)
            ? fallbackPaths
            : fallbackPaths.Prepend(configuredPath);

        return candidates.FirstOrDefault(File.Exists)
            ?? throw new InvalidOperationException(
                "No supported PDF font was found. Configure Pdf:RegularFontPath and Pdf:BoldFontPath.");
    }
}

