# SARB Economic Pipeline - Assessment Setup Script
# This script helps connect your project to the assessor's GCP project: brendon-presentation

param(
    [string]$ProjectId = "brendon-presentation",
    [string]$UserEmail = "",
    [switch]$SetupDemo,
    [switch]$ValidateConnection
)

# Load configuration
. ".\config\gcp-project-config.ps1"

Write-Host "=== SARB Economic Pipeline - Assessment Setup ===" -ForegroundColor Cyan
Write-Host "Connecting to GCP Project: $ProjectId" -ForegroundColor Green
Write-Host ""

function Test-GCloudAuth {
    Write-Host "Checking Google Cloud authentication..." -ForegroundColor Yellow
    
    try {
        $authInfo = gcloud auth list --format="value(account)" --filter="status:ACTIVE" 2>$null
        if ($authInfo) {
            Write-Host "✅ Authenticated as: $authInfo" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Not authenticated with Google Cloud" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Google Cloud CLI not installed or configured" -ForegroundColor Red
        return $false
    }
}

function Set-GCPProject {
    param([string]$ProjectId)
    
    Write-Host "Setting GCP project to: $ProjectId" -ForegroundColor Yellow
    
    try {
        gcloud config set project $ProjectId
        $currentProject = gcloud config get-value project 2>$null
        
        if ($currentProject -eq $ProjectId) {
            Write-Host "✅ Successfully set project to: $currentProject" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to set project" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Error setting GCP project: $_" -ForegroundColor Red
        return $false
    }
}

function Test-ProjectAccess {
    param([string]$ProjectId)
    
    Write-Host "Testing access to project: $ProjectId" -ForegroundColor Yellow
    
    try {
        # Test BigQuery access
        $datasets = bq ls --project_id=$ProjectId --format=json 2>$null
        if ($datasets) {
            Write-Host "✅ BigQuery access confirmed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  BigQuery access may be limited" -ForegroundColor Yellow
        }
        
        # Test Cloud Storage access
        $buckets = gsutil ls -p $ProjectId 2>$null
        if ($buckets) {
            Write-Host "✅ Cloud Storage access confirmed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Cloud Storage access may be limited" -ForegroundColor Yellow
        }
        
        return $true
    } catch {
        Write-Host "❌ Error testing project access: $_" -ForegroundColor Red
        return $false
    }
}

function Initialize-SARBDataset {
    param([string]$ProjectId)
    
    Write-Host "Creating SARB economic dataset..." -ForegroundColor Yellow
    
    try {
        # Create BigQuery dataset
        bq mk --project_id=$ProjectId --dataset --location=US sarb_economic_data
        
        # Create sample table
        $tableSchema = @"
[
  {"name": "indicator_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "indicator_name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "value", "type": "NUMERIC", "mode": "REQUIRED"},
  {"name": "date_recorded", "type": "DATE", "mode": "REQUIRED"},
  {"name": "source", "type": "STRING", "mode": "REQUIRED"},
  {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
]
"@
        
        $tableSchema | Out-File -FilePath "temp_schema.json" -Encoding utf8
        bq mk --project_id=$ProjectId --table sarb_economic_data.economic_indicators temp_schema.json
        Remove-Item "temp_schema.json" -ErrorAction SilentlyContinue
        
        Write-Host "✅ SARB dataset and tables created successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "⚠️  Dataset may already exist or insufficient permissions: $_" -ForegroundColor Yellow
        return $false
    }
}

function Show-DemoCommands {
    param([string]$ProjectId)
    
    Write-Host ""
    Write-Host "=== Demo Commands for Assessment ===" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "1. Grant Access Command:" -ForegroundColor Yellow
    Write-Host "   .\scripts\grant_access.ps1 -ProjectId $ProjectId -UserEmail your.email@example.com -RoleType analyst" -ForegroundColor White
    Write-Host ""
    
    Write-Host "2. BigQuery Console:" -ForegroundColor Yellow
    Write-Host "   https://console.cloud.google.com/bigquery?project=$ProjectId" -ForegroundColor White
    Write-Host ""
    
    Write-Host "3. View Economic Data:" -ForegroundColor Yellow
    Write-Host "   SELECT * FROM ``$ProjectId.sarb_economic_data.economic_indicators`` LIMIT 10;" -ForegroundColor White
    Write-Host ""
    
    Write-Host "4. Upload Sample Data:" -ForegroundColor Yellow
    Write-Host "   python src\main.py --project-id $ProjectId --upload-sample-data" -ForegroundColor White
    Write-Host ""
    
    Write-Host "5. Run Economic Analysis:" -ForegroundColor Yellow
    Write-Host "   jupyter notebook analysis\sarb_macroeconomic_analysis.ipynb" -ForegroundColor White
    Write-Host ""
}

function Create-SampleData {
    param([string]$ProjectId)
    
    Write-Host "Creating sample economic data..." -ForegroundColor Yellow
    
    $sampleData = @"
indicator_id,indicator_name,value,date_recorded,source
REPO_RATE,Repository Rate,7.75,2025-10-21,SARB
CPI_INFLATION,Consumer Price Index,4.2,2025-10-21,Statistics SA
GDP_GROWTH,GDP Growth Rate,2.1,2025-09-30,Statistics SA
UNEMPLOYMENT,Unemployment Rate,32.4,2025-09-30,Statistics SA
PRIME_RATE,Prime Lending Rate,11.25,2025-10-21,SARB
"@
    
    $sampleData | Out-File -FilePath "sample_economic_data.csv" -Encoding utf8
    
    try {
        # Upload to BigQuery
        bq load --project_id=$ProjectId --source_format=CSV --skip_leading_rows=1 `
            sarb_economic_data.economic_indicators sample_economic_data.csv
        
        Write-Host "✅ Sample economic data uploaded successfully" -ForegroundColor Green
        Remove-Item "sample_economic_data.csv" -ErrorAction SilentlyContinue
        return $true
    } catch {
        Write-Host "⚠️  Could not upload sample data: $_" -ForegroundColor Yellow
        return $false
    }
}

# Main execution
Write-Host "Starting assessment setup..." -ForegroundColor Green

# Check authentication
if (-not (Test-GCloudAuth)) {
    Write-Host ""
    Write-Host "Please authenticate with Google Cloud first:" -ForegroundColor Red
    Write-Host "gcloud auth login" -ForegroundColor White
    Write-Host "gcloud auth application-default login" -ForegroundColor White
    exit 1
}

# Set project
if (-not (Set-GCPProject -ProjectId $ProjectId)) {
    Write-Host "Failed to set GCP project. Please check permissions." -ForegroundColor Red
    exit 1
}

if ($ValidateConnection) {
    Test-ProjectAccess -ProjectId $ProjectId
}

if ($SetupDemo) {
    Initialize-SARBDataset -ProjectId $ProjectId
    Create-SampleData -ProjectId $ProjectId
}

Show-DemoCommands -ProjectId $ProjectId

Write-Host ""
Write-Host "=== Assessment Project Connected Successfully! ===" -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "BigQuery Console: https://console.cloud.google.com/bigquery?project=$ProjectId" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\setup-assessment.ps1 -SetupDemo" -ForegroundColor White
Write-Host "2. Open BigQuery console to verify setup" -ForegroundColor White
Write-Host "3. Use the demo commands above for your presentation" -ForegroundColor White