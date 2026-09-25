$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host " Small Business Data Platform"
Write-Host "========================================"
Write-Host ""

# Project root = directory containing this script
$ProjectRoot = $PSScriptRoot

# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

Write-Host "[1/6] Loading environment configuration..."

$EnvFile = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvFile)) {
    throw "Missing .env file. Copy .env.example to .env and configure it."
}

Get-Content $EnvFile | ForEach-Object {

    $line = $_.Trim()

    # Ignore blank lines and comments
    if ($line -and -not $line.StartsWith("#")) {

        $parts = $line -split "=", 2

        if ($parts.Count -eq 2) {

            $name = $parts[0].Trim()
            $value = $parts[1].Trim()

            [Environment]::SetEnvironmentVariable(
                $name,
                $value,
                "Process"
            )
        }
    }
}

Write-Host "Environment configuration loaded successfully."

# --------------------------------------------------
# 2. Validate Docker configuration
# --------------------------------------------------

Write-Host ""
Write-Host "[2/6] Validating Docker configuration..."

Push-Location $ProjectRoot

try {
    docker compose config --quiet

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose configuration validation failed."
    }
}
finally {
    Pop-Location
}

Write-Host "Docker configuration is valid."

# --------------------------------------------------
# 3. Start infrastructure
# --------------------------------------------------

Write-Host ""
Write-Host "[3/6] Starting infrastructure..."

docker compose -f (Join-Path $ProjectRoot "docker-compose.yml") up -d

if ($LASTEXITCODE -ne 0) {
    throw "Failed to start Docker infrastructure."
}

Write-Host "Infrastructure started successfully."

# --------------------------------------------------
# 4. Load raw data
# --------------------------------------------------

Write-Host ""
Write-Host "[4/6] Loading raw data into PostgreSQL..."

$LoaderScript = Join-Path $ProjectRoot "scripts\load_raw_data.py"

if (-not (Test-Path $LoaderScript)) {
    throw "Python ingestion script not found: $LoaderScript"
}

python $LoaderScript

if ($LASTEXITCODE -ne 0) {
    throw "Raw data ingestion failed."
}

Write-Host "Raw data loaded successfully."

# --------------------------------------------------
# 5. Build and test dbt models
# --------------------------------------------------

Write-Host ""
Write-Host "[5/6] Building and testing dbt models..."

$DbtProject = Join-Path $ProjectRoot "small_business"

if (-not (Test-Path $DbtProject)) {
    throw "dbt project not found: $DbtProject"
}

Push-Location $DbtProject

try {
    dbt seed

    if ($LASTEXITCODE -ne 0) {
        throw "dbt seed failed."
    }

    dbt build

    if ($LASTEXITCODE -ne 0) {
        throw "dbt build failed."
    }
}
finally {
    Pop-Location
}

Write-Host "dbt build and data quality tests passed."

# --------------------------------------------------
# 6. Pipeline complete
# --------------------------------------------------

Write-Host ""
Write-Host "[6/6] Pipeline completed successfully."
Write-Host ""
Write-Host "========================================"
Write-Host " SUCCESS"
Write-Host "========================================"
Write-Host " Raw data loaded"
Write-Host " dbt models built"
Write-Host " Data quality tests passed"
Write-Host " Analytics are ready in Metabase"
Write-Host ""