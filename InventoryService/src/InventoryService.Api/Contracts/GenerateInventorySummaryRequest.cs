namespace InventoryService.Contracts;

public sealed record GenerateInventorySummaryRequest(
    string? ReportId,
    string? WarehouseName,
    string? Locale,
    IReadOnlyList<InventoryItemRequest>? Items,
    DateTimeOffset? GeneratedAt);

public sealed record InventoryItemRequest(
    string? Sku,
    string? Name,
    decimal Quantity,
    string? Unit);
