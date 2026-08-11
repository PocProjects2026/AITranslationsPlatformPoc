using InventoryService.Contracts;
using InventoryService.Validation;

namespace InventoryService.Api.Tests;

public sealed class InventorySummaryRequestValidatorTests
{
    [Fact]
    public void Validate_WithValidRequest_ReturnsNoErrors()
    {
        var request = new GenerateInventorySummaryRequest(
            "INV-001",
            "Casablanca Warehouse",
            "en",
            [new InventoryItemRequest("PAPER-A4", "A4 paper", 120, "boxes")],
            null);

        var errors = InventorySummaryRequestValidator.Validate(request);

        Assert.Empty(errors);
    }

    [Fact]
    public void Validate_WithNegativeQuantity_ReturnsQuantityError()
    {
        var request = new GenerateInventorySummaryRequest(
            "INV-001",
            "Casablanca Warehouse",
            "en",
            [new InventoryItemRequest("PAPER-A4", "A4 paper", -1, "boxes")],
            null);

        var errors = InventorySummaryRequestValidator.Validate(request);

        Assert.Contains("Items[0].Quantity", errors.Keys);
    }
}
