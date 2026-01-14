# Script to move the project to a path without special characters

Write-Host "Moving project to a path without special characters..." -ForegroundColor Cyan

$sourcePath = "C:\Users\m\Desktop\Project #5"
$destPath = "C:\Users\m\Desktop\websocket-chat"

# Check if source exists
if (-not (Test-Path $sourcePath)) {
    Write-Host "Error: Source directory not found at $sourcePath" -ForegroundColor Red
    exit 1
}

# Check if destination already exists
if (Test-Path $destPath) {
    Write-Host "Warning: Destination directory already exists at $destPath" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and continue? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Path $destPath -Recurse -Force
}

# Move the directory
Write-Host "Moving from: $sourcePath" -ForegroundColor Gray
Write-Host "Moving to:   $destPath" -ForegroundColor Gray

try {
    Move-Item -Path $sourcePath -Destination $destPath -Force
    Write-Host "`nSuccess! Project moved to: $destPath" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. cd $destPath" -ForegroundColor White
    Write-Host "2. Start backend:  cd backend && uvicorn main:app --reload --port 8000" -ForegroundColor White
    Write-Host "3. Start frontend: cd frontend && npm run dev" -ForegroundColor White
} catch {
    Write-Host "Error moving directory: $_" -ForegroundColor Red
    exit 1
}
