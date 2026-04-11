$token = $env:HF_TOKEN # Use environment variable
$repo = "happyjourney1/skyroute-dashboard"
$apiBase = "https://huggingface.co/api/spaces/$repo"
$uploadBase = "https://huggingface.co/spaces/$repo/upload"

# Step 1: Create/ensure the repo exists
Write-Host "[INFO] Ensuring HuggingFace Space repo exists..."
$createJson = '{"type":"space","sdk":"docker","private":false}'
$createResult = curl.exe -s -o /dev/null -w "%{http_code}" `
    -X POST "https://huggingface.co/api/repos/create" `
    -H "Authorization: Bearer $token" `
    -H "Content-Type: application/json" `
    -d $createJson

if ($createResult -eq "200" -or $createResult -eq "409") {
    Write-Host "[OK] Repo is ready (status: $createResult)"
} else {
    Write-Host "[WARN] Create repo returned status: $createResult (may already exist, continuing...)"
}

# Step 2: Upload files using the HuggingFace Hub API (LFS-based upload)
# We'll use the direct file upload endpoint

$filesToUpload = @(
    "Dockerfile",
    "requirements.txt",
    "inference.py",
    "drone_env.py",
    "openenv.yaml",
    "README.md",
    "ppo_drone_aid.zip"
)

$serverFiles = @(
    "server\__init__.py",
    "server\app.py",
    "server\drone_dashboard.py",
    "server\drone_env.py",
    "server\graders.py"
)

$frontendFiles = @()
if (Test-Path "frontend") {
    $frontendFiles = Get-ChildItem -Path "frontend" -File -Recurse | ForEach-Object {
        $_.FullName.Replace("$PWD\", "").Replace("\", "/")
    }
}

$allFiles = $filesToUpload + $serverFiles

function Upload-File {
    param(
        [string]$localPath,
        [string]$remotePath
    )
    
    if (-not (Test-Path $localPath)) {
        Write-Host "[SKIP] $localPath not found"
        return
    }
    
    $remotePath = $remotePath.Replace("\", "/")
    $url = "https://huggingface.co/spaces/$repo/resolve/main/$remotePath"
    $uploadUrl = "https://huggingface.co/api/spaces/$repo/upload"
    
    Write-Host "[UPLOAD] $localPath -> $remotePath"
    
    $result = curl.exe -s -o /dev/null -w "%{http_code}" `
        -X PUT "https://huggingface.co/api/spaces/$repo/raw/main/$remotePath" `
        -H "Authorization: Bearer $token" `
        -H "Content-Type: application/octet-stream" `
        --data-binary "@$localPath"
    
    Write-Host "  Status: $result"
}

Write-Host "`n[INFO] Uploading files..."

foreach ($f in $allFiles) {
    Upload-File -localPath $f -remotePath $f
}

# Upload frontend files
if ($frontendFiles.Count -gt 0) {
    foreach ($f in $frontendFiles) {
        Upload-File -localPath $f -remotePath $f
    }
}

Write-Host "`n[DONE] Upload complete! Check: https://huggingface.co/spaces/$repo"
