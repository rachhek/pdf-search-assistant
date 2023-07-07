$output = azd env get-values

foreach ($line in $output) {
    $name, $value = $line.Split("=")
    $value = $value -replace '^\"|\"$'
    [Environment]::SetEnvironmentVariable($name, $value)
}

Write-Host "Environment variables set."

$roles = @(
    "a97b65f3-24c7-4388-baec-2e87135dc908"
)

if ([string]::IsNullOrEmpty($env:AZURE_RESOURCE_GROUP)) {
    $env:AZURE_RESOURCE_GROUP = "rg-$env:AZURE_ENV_NAME"
    azd env set AZURE_RESOURCE_GROUP $env:AZURE_RESOURCE_GROUP
}

foreach ($role in $roles) {
    az role assignment create `
        --role $role `
        --assignee-object-id $env:AZURE_PRINCIPAL_ID `
        --scope /subscriptions/$env:AZURE_SUBSCRIPTION_ID/resourceGroups/$env:AZURE_RESOURCE_GROUP `
        --assignee-principal-type User
}
