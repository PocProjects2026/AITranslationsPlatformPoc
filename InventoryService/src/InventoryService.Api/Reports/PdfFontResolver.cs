using PdfSharp.Fonts;

namespace InventoryService.Reports;

internal sealed class PdfFontResolver : IFontResolver
{
    private const string RegularFace = "Inventory-Regular";
    private const string BoldFace = "Inventory-Bold";

    private readonly byte[] _regularFont;
    private readonly byte[] _boldFont;

    public PdfFontResolver(string regularFontPath, string boldFontPath)
    {
        _regularFont = File.ReadAllBytes(regularFontPath);
        _boldFont = File.ReadAllBytes(boldFontPath);
    }

    public byte[]? GetFont(string faceName) => faceName switch
    {
        RegularFace => _regularFont,
        BoldFace => _boldFont,
        _ => null
    };

    public FontResolverInfo? ResolveTypeface(string familyName, bool isBold, bool isItalic) =>
        new(isBold ? BoldFace : RegularFace);
}

