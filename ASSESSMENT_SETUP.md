# Connecting to Assessment GCP Project

## Overview
The assessor has provided a GCP project for the SARB Economic Pipeline assessment:

- **Project ID**: `brendon-presentation`
- **BigQuery Console**: https://console.cloud.google.com/bigquery?referrer=search&inv=1&invt=Ab5Qcg&project=brendon-presentation&ws=!1m0

## Quick Setup Steps

### 1. Authenticate with Google Cloud
```powershell
# Login to Google Cloud
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Set the project
gcloud config set project brendon-presentation
```

### 2. Run Assessment Setup
```powershell
# Navigate to project directory
cd c:\sarb-economic-pipeline

# Run the assessment setup script
.\setup-assessment.ps1 -SetupDemo

# Validate connection
.\setup-assessment.ps1 -ValidateConnection
```

### 3. Create BigQuery Dataset
```powershell
# Create the dataset using the SQL script
bq query --project_id=brendon-presentation --use_legacy_sql=false < infrastructure/bigquery_setup.sql

# Or create manually
bq mk --project_id=brendon-presentation --dataset --location=US sarb_economic_data
```

### 4. Demo Commands for Assessment

#### Grant Access Command:
```powershell
.\scripts\grant_access.ps1 -ProjectId brendon-presentation -UserEmail your.email@example.com -RoleType analyst
```

#### Upload Sample Data:
```powershell
# This will be created by the setup script or main.py
python src/main.py --project-id brendon-presentation --upload-sample-data
```

#### View Data in BigQuery:
```sql
SELECT 
    indicator_name,
    value,
    date_recorded,
    source
FROM `brendon-presentation.sarb_economic_data.economic_indicators`
ORDER BY date_recorded DESC
LIMIT 10;
```

#### Economic Analysis Query:
```sql
-- Repo Rate Trend Analysis
SELECT 
    date_recorded,
    value as repo_rate,
    LAG(value) OVER (ORDER BY date_recorded) as prev_rate,
    value - LAG(value) OVER (ORDER BY date_recorded) as rate_change
FROM `brendon-presentation.sarb_economic_data.economic_indicators`
WHERE indicator_name = 'Repository Rate'
ORDER BY date_recorded DESC;
```

## Assessment Demo Flow

### 1. Data Upload Demo
- Show CSV file upload to BigQuery
- Demonstrate data validation and processing
- Expected: Data appears in BigQuery within 30 seconds

### 2. Access Management Demo
```powershell
.\scripts\grant_access.ps1 -ProjectId brendon-presentation -UserEmail demo.analyst@example.com -RoleType analyst
```
- Show role-based permissions being granted
- Demonstrate security controls

### 3. Economic Analysis Demo
- Open Jupyter notebook: `analysis/sarb_macroeconomic_analysis.ipynb`
- Execute economic indicator queries
- Show real-time analysis capabilities

### 4. Security Audit Demo
```powershell
# View audit logs
gcloud logging read "protoPayload.serviceName=bigquery.googleapis.com" --project=brendon-presentation --limit=5
```

## Troubleshooting

### If Authentication Fails:
```powershell
# Re-authenticate
gcloud auth revoke --all
gcloud auth login
gcloud auth application-default login
```

### If Project Access Denied:
- Ensure the assessor has granted you appropriate permissions
- Verify project ID is correct: `brendon-presentation`
- Check if you're using the correct Google account

### If BigQuery Commands Fail:
```powershell
# Test BigQuery access
bq ls --project_id=brendon-presentation

# If no datasets shown, you may need additional permissions
```

## Files Updated for Assessment

The following files have been updated to work with the assessment project:

- `config/gcp-project-config.ps1` - Project configuration
- `infrastructure/bigquery_setup.sql` - Updated with correct project ID
- `setup-assessment.ps1` - Assessment setup automation
- This file: `ASSESSMENT_SETUP.md` - Instructions

## Next Steps

1. ✅ Run the setup script: `.\setup-assessment.ps1 -SetupDemo`
2. ✅ Verify BigQuery access in the console
3. ✅ Test the demo commands
4. ✅ Practice the presentation flow
5. ✅ Prepare for live demonstration

The system is now configured to work with the assessor's GCP project `brendon-presentation` and ready for your assessment presentation.