namespace InventoryService.Contracts;

public sealed record VersionResponse(string ApplicationVersion, string GitCommit);

