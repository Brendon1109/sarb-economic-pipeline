# GCP Project Setup Instructions

## Prerequisites Installation

### 1. Install Google Cloud SDK
**Download and install from**: https://cloud.google.com/sdk/docs/install-sdk

**For Windows**:
- Download the installer: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
- Run the installer
- Follow the setup wizard
- Restart PowerShell after installation

### 2. Verify Installation
```powershell
# After installation, restart PowerShell and run:
gcloud --version
```

## Project Creation and Setup

### 3. Authenticate with Google Cloud
```powershell
# Login to your Google account
gcloud auth login

# This will open a browser window for authentication
```

### 4. Create New GCP Project
```powershell
# Option A: Use the project ID you mentioned
gcloud projects create molten-avatar-437519-m8 --name="SARB Economic Pipeline"

# Option B: Let Google generate a unique project ID
gcloud projects create --name="SARB Economic Pipeline"
```

### 5. Set Up Billing (Required)
- Go to: https://console.cloud.google.com/billing
- Create a billing account if you don't have one
- Link your project to the billing account
- **Note**: This project will incur GCP costs for BigQuery, Cloud Run, Storage, etc.

### 6. Set Default Project
```powershell
# Set your project as default
gcloud config set project molten-avatar-437519-m8
```

## Infrastructure Setup

### 7. Run Infrastructure Creation Script
```powershell
# Set environment variables
$env:PROJECT_ID = "molten-avatar-437519-m8"
$env:BUCKET_NAME = "sarb-economic-data-molten-avatar-437519-m8"  # Must be globally unique
$env:REGION = "europe-west1"
$env:DATASET_ID = "sarb_economic_data"

# Make script executable and run it
# Note: You may need to run this in Git Bash or WSL for the bash script
bash scripts/create_infrastructure.sh
```

### 8. Deploy Application
```powershell
# After infrastructure is created, deploy the application
bash scripts/deploy.sh
```

## Alternative: Manual Setup

If you prefer manual setup or the scripts don't work:

### Enable Required APIs
```powershell
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### Create Storage Bucket
```powershell
# Create bucket (name must be globally unique)
gsutil mb -p molten-avatar-437519-m8 -c STANDARD -l europe-west1 gs://sarb-economic-data-molten-avatar-437519-m8
```

### Create BigQuery Dataset
```powershell
bq mk --dataset --description="South African Reserve Bank Economic Indicators Dataset" --location=europe-west1 molten-avatar-437519-m8:sarb_economic_data
```

### Create BigQuery Tables
```powershell
# Run the BigQuery setup script
bq query --use_legacy_sql=false --project_id=molten-avatar-437519-m8 < infrastructure/bigquery_setup.sql
```

## Cost Estimate

**Expected Monthly Costs** (approximate):
- BigQuery: $10-50 (depends on data volume and queries)
- Cloud Storage: $1-5 (for raw data storage)
- Cloud Run: $5-20 (depends on usage)
- Vertex AI: $10-100 (depends on AI analysis frequency)
- **Total**: ~$25-175/month (varies with usage)

## Verification Commands

### Check Project Status
```powershell
gcloud projects describe molten-avatar-437519-m8
```

### Check Enabled Services
```powershell
gcloud services list --enabled --project=molten-avatar-437519-m8
```

### Test BigQuery Access
```powershell
bq ls molten-avatar-437519-m8:sarb_economic_data
```

## Next Steps After Setup

1. **Test the pipeline**: Run the application to ensure it works
2. **Grant Lyle access**: Use the access management scripts
3. **Set up monitoring**: Configure alerts and monitoring
4. **Schedule regular runs**: Set up Cloud Scheduler for automated execution

## Troubleshooting

### Common Issues:
- **Billing not enabled**: Enable billing in GCP console
- **API not enabled**: Run the enable services commands
- **Permission denied**: Ensure you're project owner
- **Bucket name conflicts**: Use a more unique bucket name

### Support Resources:
- Google Cloud Console: https://console.cloud.google.com
- Documentation: https://cloud.google.com/docs
- Pricing Calculator: https://cloud.google.com/products/calculator