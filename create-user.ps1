param(
    [string]$Email = "admin@company.com",
    [string]$Password = "password123",  # Must be >= 8 chars
    [string]$FullName = "Admin User"
)

$Url = "http://localhost:8000/users"
$Body = @{
    email     = $Email
    password  = $Password
    full_name = $FullName
} | ConvertTo-Json

try {
    Write-Host "Creating user $Email..."
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType "application/json"
    Write-Host "✅ User created successfully!" -ForegroundColor Green
    Write-Host "ID: $($Response.id)"
    Write-Host "Email: $($Response.email)"
}
catch {
    Write-Host "❌ Failed to create user" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $Stream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($Stream)
        $ErrorBody = $Reader.ReadToEnd()
        Write-Host "Details: $ErrorBody" -ForegroundColor Yellow
    }
}
