using InventoryService.Contracts;

namespace InventoryService.Reports;

public interface IInventorySummaryPdfGenerator
{
    byte[] Generate(GenerateInventorySummaryRequest request, DateTimeOffset generatedAt);
}

