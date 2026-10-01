using InventoryService.Contracts;

namespace InventoryService.Validation;

public static class InventorySummaryRequestValidator
{
    private const int MaximumItemCount = 20;

    public static Dictionary<string, string[]> Validate(GenerateInventorySummaryRequest request)
    {
        var errors = new Dictionary<string, string[]>(StringComparer.Ordinal);

        ValidateRequiredLength(request.ReportId, nameof(request.ReportId), 80, errors);
        ValidateRequiredLength(request.WarehouseName, nameof(request.WarehouseName), 120, errors);
        ValidateRequiredLength(request.Locale, nameof(request.Locale), 20, errors);

        if (request.Items is null || request.Items.Count == 0)
        {
            errors[nameof(request.Items)] = ["At least one inventory item is required."];
            return errors;
        }

        if (request.Items.Count > MaximumItemCount)
        {
            errors[nameof(request.Items)] = [$"No more than {MaximumItemCount} inventory items are allowed."];
        }

        for (var index = 0; index < request.Items.Count; index++)
        {
            var item = request.Items[index];
            ValidateRequiredLength(item.Sku, $"Items[{index}].Sku", 60, errors);
            ValidateRequiredLength(item.Name, $"Items[{index}].Name", 120, errors);
            ValidateRequiredLength(item.Unit, $"Items[{index}].Unit", 30, errors);

            if (item.Quantity < 0)
            {
                errors[$"Items[{index}].Quantity"] = ["Quantity cannot be negative."];
            }
        }

        return errors;
    }

    private static void ValidateRequiredLength(
        string? value,
        string field,
        int maximumLength,
        IDictionary<string, string[]> errors)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            errors[field] = ["A value is required."];
        }
        else if (value.Length > maximumLength)
        {
            errors[field] = [$"The value cannot exceed {maximumLength} characters."];
        }
    }
}
