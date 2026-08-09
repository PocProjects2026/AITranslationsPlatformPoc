using System.Globalization;
using InventoryService.Contracts;
using PdfSharp.Drawing;
using PdfSharp.Drawing.Layout;
using PdfSharp.Pdf;

namespace InventoryService.Reports;

public sealed class InventorySummaryPdfGenerator : IInventorySummaryPdfGenerator
{
    private const double PageMargin = 48;
    private const double RowHeight = 24;

    public byte[] Generate(GenerateInventorySummaryRequest request, DateTimeOffset generatedAt)
    {
        ArgumentNullException.ThrowIfNull(request.Items);

        using var document = new PdfDocument();
        document.Info.Title = $"Inventory summary {request.ReportId}";
        document.Info.Author = "InventoryService";

        var page = document.AddPage();
        using var graphics = XGraphics.FromPdfPage(page);
        var formatter = new XTextFormatter(graphics);

        var titleFont = new XFont("Inventory", 20, XFontStyleEx.Bold);
        var headingFont = new XFont("Inventory", 10, XFontStyleEx.Bold);
        var bodyFont = new XFont("Inventory", 9, XFontStyleEx.Regular);
        var mutedFont = new XFont("Inventory", 8, XFontStyleEx.Regular);

        graphics.DrawString(
            "Inventory summary",
            titleFont,
            XBrushes.Black,
            new XRect(PageMargin, 45, page.Width.Point - (2 * PageMargin), 30),
            XStringFormats.TopLeft);

        graphics.DrawString(
            $"Report: {request.ReportId}",
            bodyFont,
            XBrushes.Black,
            PageMargin,
            95);
        graphics.DrawString(
            $"Warehouse: {request.WarehouseName}",
            bodyFont,
            XBrushes.Black,
            PageMargin,
            112);
        graphics.DrawString(
            $"Generated: {generatedAt:yyyy-MM-dd HH:mm:ss zzz}",
            bodyFont,
            XBrushes.Black,
            PageMargin,
            129);

        const double tableTop = 165;
        const double skuWidth = 120;
        const double nameWidth = 259;
        const double quantityWidth = 120;
        var tableWidth = skuWidth + nameWidth + quantityWidth;

        DrawCell(graphics, formatter, "SKU", headingFont, PageMargin, tableTop, skuWidth, XBrushes.LightGray);
        DrawCell(graphics, formatter, "Item", headingFont, PageMargin + skuWidth, tableTop, nameWidth, XBrushes.LightGray);
        DrawCell(graphics, formatter, "Quantity", headingFont, PageMargin + skuWidth + nameWidth, tableTop, quantityWidth, XBrushes.LightGray);

        for (var index = 0; index < request.Items.Count; index++)
        {
            var item = request.Items[index];
            var top = tableTop + ((index + 1) * RowHeight);
            var background = index % 2 == 0 ? XBrushes.White : new XSolidBrush(XColor.FromArgb(245, 247, 249));

            DrawCell(graphics, formatter, item.Sku!, bodyFont, PageMargin, top, skuWidth, background);
            DrawCell(graphics, formatter, item.Name!, bodyFont, PageMargin + skuWidth, top, nameWidth, background);
            DrawCell(
                graphics,
                formatter,
                $"{item.Quantity.ToString("0.##", CultureInfo.InvariantCulture)} {item.Unit}",
                bodyFont,
                PageMargin + skuWidth + nameWidth,
                top,
                quantityWidth,
                background);
        }

        var tableBottom = tableTop + ((request.Items.Count + 1) * RowHeight);
        graphics.DrawLine(XPens.Black, PageMargin, tableBottom, PageMargin + tableWidth, tableBottom);
        graphics.DrawString(
            $"{request.Items.Count} item(s)",
            mutedFont,
            XBrushes.DimGray,
            new XRect(PageMargin, tableBottom + 14, tableWidth, 20),
            XStringFormats.TopRight);

        using var stream = new MemoryStream();
        document.Save(stream, closeStream: false);
        return stream.ToArray();
    }

    private static void DrawCell(
        XGraphics graphics,
        XTextFormatter formatter,
        string text,
        XFont font,
        double left,
        double top,
        double width,
        XBrush background)
    {
        graphics.DrawRectangle(background, left, top, width, RowHeight);
        graphics.DrawRectangle(XPens.Gray, left, top, width, RowHeight);
        formatter.DrawString(text, font, XBrushes.Black, new XRect(left + 5, top + 6, width - 10, RowHeight - 8));
    }
}

