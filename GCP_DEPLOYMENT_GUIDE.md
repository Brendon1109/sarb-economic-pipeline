# SARB Economic Pipeline - GCP Deployment Guide

## Overview
This guide will help you deploy and run the SARB Economic Pipeline on Google Cloud Platform using the assessor's project: `brendon-presentation`.

## Prerequisites Setup

### 1. Install Google Cloud CLI

**Option A: Direct Download (Recommended)**
1. Go to: https://cloud.google.com/sdk/docs/install-sdk
2. Download "Google Cloud CLI Installer for Windows"
3. Run the installer and follow the setup wizard
4. Restart your terminal/PowerShell

**Option B: PowerShell Installation**
```powershell
# Download the installer
Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile "GoogleCloudSDKInstaller.exe"

# Run the installer
Start-Process -FilePath "GoogleCloudSDKInstaller.exe" -Wait
```

**Option C: Using Chocolatey (if installed)**
```powershell
choco install gcloudsdk
```

### 2. Install Python Dependencies
```powershell
# Make sure you're in the project directory
cd C:\sarb-economic-pipeline

# Install required Python packages
pip install -r requirements.txt

# Install additional packages for GCP
pip install google-cloud-bigquery google-cloud-storage google-cloud-run pandas jupyter
```

## Authentication & Project Setup

### 1. Authenticate with Google Cloud
```powershell
# Login to Google Cloud (opens browser)
gcloud auth login

# Set application default credentials for API access
gcloud auth application-default login

# Set the project to the assessor's project
gcloud config set project brendon-presentation

# Verify your configuration
gcloud config list
```

### 2. Verify Project Access
```powershell
# Test BigQuery access
bq ls --project_id=brendon-presentation

# Test Cloud Storage access
gsutil ls -p brendon-presentation

# Check your permissions
gcloud projects get-iam-policy brendon-presentation
```

## Running the SARB Pipeline

### 1. Automated Setup
```powershell
# Navigate to project directory
cd C:\sarb-economic-pipeline

# Run the assessment setup script
.\setup-assessment.ps1 -SetupDemo

# This will:
# - Verify GCP authentication
# - Set the correct project
# - Create BigQuery dataset
# - Upload sample data
# - Display demo commands
```

### 2. Manual BigQuery Setup (if needed)
```powershell
# Create the dataset
bq mk --project_id=brendon-presentation --dataset --location=US sarb_economic_data

# Create the main table using SQL script
bq query --project_id=brendon-presentation --use_legacy_sql=false < infrastructure/bigquery_setup.sql

# Or create table manually
bq mk --project_id=brendon-presentation --table sarb_economic_data.economic_indicators indicator_id:STRING,indicator_name:STRING,value:NUMERIC,date_recorded:DATE,source:STRING,created_at:TIMESTAMP
```

### 3. Upload Sample Data
```powershell
# Upload sample economic data using Python script
python src/main.py --project-id brendon-presentation --upload-sample-data

# Or upload manually with bq command
echo "indicator_id,indicator_name,value,date_recorded,source
REPO_RATE,Repository Rate,7.75,2025-10-21,SARB
CPI_INFLATION,Consumer Price Index,4.2,2025-10-21,Statistics SA
GDP_GROWTH,GDP Growth Rate,2.1,2025-09-30,Statistics SA" > sample_data.csv

bq load --project_id=brendon-presentation --source_format=CSV --skip_leading_rows=1 sarb_economic_data.economic_indicators sample_data.csv
```

## Demo Scenarios

### 1. Data Processing Demo
```powershell
# Process and upload data
python src/main.py --project-id brendon-presentation --upload-sample-data

# View the data in BigQuery console
# https://console.cloud.google.com/bigquery?project=brendon-presentation
```

### 2. Access Management Demo
```powershell
# Grant analyst access to a user
.\scripts\grant_access.ps1 -ProjectId brendon-presentation -UserEmail demo.analyst@example.com -RoleType analyst

# Test permissions
.\scripts\grant_access.ps1 -ProjectId brendon-presentation -UserEmail demo.analyst@example.com -RoleType analyst -ValidateAccess
```

### 3. Economic Analysis Demo
```powershell
# Open Jupyter notebook for analysis
jupyter notebook analysis/sarb_macroeconomic_analysis.ipynb

# Or run analysis queries directly
bq query --project_id=brendon-presentation --use_legacy_sql=false "
SELECT 
    indicator_name,
    value,
    date_recorded,
    source
FROM \`brendon-presentation.sarb_economic_data.economic_indicators\`
ORDER BY date_recorded DESC
LIMIT 10"
```

### 4. Security Audit Demo
```powershell
# View audit logs
gcloud logging read "protoPayload.serviceName=bigquery.googleapis.com" --project=brendon-presentation --limit=5

# Check encryption status
bq show --encryption_configuration brendon-presentation:sarb_economic_data.economic_indicators
```

## Key BigQuery Queries for Demo

### Repository Rate Analysis
```sql
SELECT 
    date_recorded,
    value as repo_rate,
    LAG(value) OVER (ORDER BY date_recorded) as prev_rate,
    value - LAG(value) OVER (ORDER BY date_recorded) as rate_change,
    CASE 
        WHEN value > LAG(value) OVER (ORDER BY date_recorded) THEN 'INCREASE'
        WHEN value < LAG(value) OVER (ORDER BY date_recorded) THEN 'DECREASE'
        ELSE 'UNCHANGED'
    END as trend_direction
FROM `brendon-presentation.sarb_economic_data.economic_indicators`
WHERE indicator_name = 'Repository Rate'
ORDER BY date_recorded DESC;
```

### Economic Overview Dashboard
```sql
SELECT 
    indicator_name,
    value,
    date_recorded,
    source,
    RANK() OVER (PARTITION BY indicator_name ORDER BY date_recorded DESC) as latest_rank
FROM `brendon-presentation.sarb_economic_data.economic_indicators`
WHERE date_recorded >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY indicator_name, date_recorded DESC;
```

## Accessing Your Pipeline

### BigQuery Console
- URL: https://console.cloud.google.com/bigquery?project=brendon-presentation
- Dataset: `sarb_economic_data`
- Main Table: `economic_indicators`

### Cloud Storage Console
- URL: https://console.cloud.google.com/storage/browser?project=brendon-presentation

### Monitoring & Logs
- URL: https://console.cloud.google.com/monitoring?project=brendon-presentation

## Troubleshooting

### Authentication Issues
```powershell
# Clear and re-authenticate
gcloud auth revoke --all
gcloud auth login
gcloud auth application-default login
gcloud config set project brendon-presentation
```

### Permission Issues
```powershell
# Check your permissions
gcloud projects get-iam-policy brendon-presentation --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:YOUR_EMAIL@gmail.com"

# If you need additional permissions, contact the assessor
```

### BigQuery Access Issues
```powershell
# Test BigQuery access
bq ls --project_id=brendon-presentation

# If no datasets shown, you may need BigQuery User role
```

## Assessment Presentation Flow

1. **Setup Verification** (2 minutes)
   - Show GCP project access
   - Verify BigQuery dataset exists
   - Display sample data

2. **Data Pipeline Demo** (5 minutes)
   - Upload new economic data
   - Show real-time processing
   - Verify data in BigQuery

3. **Access Management Demo** (3 minutes)
   - Grant user permissions
   - Show role-based access
   - Demonstrate security controls

4. **Economic Analysis Demo** (5 minutes)
   - Execute economic queries
   - Show trend analysis
   - Display insights

5. **Q&A and Technical Discussion** (5 minutes)
   - Answer questions about architecture
   - Discuss scaling and costs
   - Show monitoring capabilities

## Contact Information

For technical support during setup:
- **Project Lead**: Brendon Mapinda
- **Email**: mapindabrendon@gmail.com
- **Repository**: github.com/Brendon1109/sarb-economic-pipeline

## Next Steps After Setup

1. ✅ Verify all authentication works
2. ✅ Upload sample data successfully
3. ✅ Test access management script
4. ✅ Practice demo queries
5. ✅ Prepare presentation flow
6. ✅ Test backup scenarios

Your SARB Economic Pipeline is ready for deployment and demonstration on Google Cloud Platform!