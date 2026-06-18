# PowerShell script to push Docker images with retry logic
param(
    [int]$MaxRetries = 3,
    [int]$RetryDelay = 10
)

$images = @(
    "hammadasher/mlops-saylani-api:latest",
    "hammadasher/mlops-saylani-frontend:latest"
)

function Push-DockerImageWithRetry {
    param(
        [string]$ImageName,
        [int]$MaxRetries,
        [int]$RetryDelay
    )
    
    $attempt = 1
    $success = $false
    
    while ($attempt -le $MaxRetries -and -not $success) {
        Write-Host "==> Attempt $attempt of ${MaxRetries}: Pushing ${ImageName}..." -ForegroundColor Cyan
        
        try {
            $process = Start-Process -FilePath "docker" -ArgumentList "push", $ImageName -NoNewWindow -Wait -PassThru
            
            if ($process.ExitCode -eq 0) {
                Write-Host "✓ Successfully pushed $ImageName" -ForegroundColor Green
                $success = $true
            } else {
                throw "Docker push failed with exit code $($process.ExitCode)"
            }
        }
        catch {
            Write-Host "✗ Failed to push $ImageName : $_" -ForegroundColor Red
            
            if ($attempt -lt $MaxRetries) {
                Write-Host "Waiting $RetryDelay seconds before retry..." -ForegroundColor Yellow
                Start-Sleep -Seconds $RetryDelay
                $attempt++
            } else {
                Write-Host "✗ Max retries reached for $ImageName" -ForegroundColor Red
                return $false
            }
        }
    }
    
    return $success
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Image Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if logged in to DockerHub
$loginCheck = docker info 2>&1 | Select-String "Username"
if (-not $loginCheck) {
    Write-Host "⚠ Not logged in to DockerHub. Attempting login..." -ForegroundColor Yellow
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Docker login failed" -ForegroundColor Red
        exit 1
    }
}

$allSuccess = $true

foreach ($image in $images) {
    Write-Host ""
    $result = Push-DockerImageWithRetry -ImageName $image -MaxRetries $MaxRetries -RetryDelay $RetryDelay
    
    if (-not $result) {
        $allSuccess = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allSuccess) {
    Write-Host "✓ All images pushed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Images on DockerHub:" -ForegroundColor Cyan
    Write-Host "  - https://hub.docker.com/r/hammadasher/mlops-saylani-api" -ForegroundColor White
    Write-Host "  - https://hub.docker.com/r/hammadasher/mlops-saylani-frontend" -ForegroundColor White
} else {
    Write-Host "✗ Some images failed to push" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Build on EC2 directly" -ForegroundColor Yellow
    Write-Host "See AWS_DEPLOYMENT.md for instructions" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
