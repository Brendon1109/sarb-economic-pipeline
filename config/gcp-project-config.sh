# SARB Economic Pipeline - GCP Project Configuration
# This file contains the actual GCP project details provided by the assessor

# Main GCP Project Configuration
PROJECT_ID="brendon-presentation"
PROJECT_NUMBER=""  # Will be populated after project inspection
REGION="us-central1"  # Default region, can be changed based on requirements
ZONE="us-central1-a"

# BigQuery Configuration
BIGQUERY_DATASET="sarb_economic_data"
BIGQUERY_LOCATION="US"  # Multi-region for better performance

# Cloud Storage Configuration
RAW_DATA_BUCKET="${PROJECT_ID}-economic-raw-data"
PROCESSED_DATA_BUCKET="${PROJECT_ID}-economic-processed"
BACKUP_DATA_BUCKET="${PROJECT_ID}-economic-backups"
ARCHIVE_DATA_BUCKET="${PROJECT_ID}-economic-archive"

# Security Configuration
KMS_KEYRING_NAME="economic-data-keyring"
KMS_KEY_NAME="economic-data-encryption-key"
KMS_LOCATION="global"

# Service Account Configuration
SERVICE_ACCOUNT_NAME="sarb-pipeline-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Cloud Run Configuration
CLOUD_RUN_SERVICE_NAME="economic-data-processor"
CLOUD_RUN_REGION="${REGION}"

# Demo and Testing Configuration
DEMO_USER_EMAIL="demo.analyst@example.com"  # Replace with actual demo email
TEST_USER_EMAIL="test.user@example.com"     # Replace with actual test email

# URLs and Endpoints
BIGQUERY_CONSOLE_URL="https://console.cloud.google.com/bigquery?project=${PROJECT_ID}"
CLOUD_STORAGE_CONSOLE_URL="https://console.cloud.google.com/storage/browser?project=${PROJECT_ID}"
CLOUD_RUN_CONSOLE_URL="https://console.cloud.google.com/run?project=${PROJECT_ID}"

# Assessment Specific Configuration
ASSESSOR_PROJECT_URL="https://console.cloud.google.com/bigquery?referrer=search&inv=1&invt=Ab5Qcg&project=brendon-presentation&ws=!1m0"
ASSESSMENT_MODE=true

echo "GCP Project Configuration Loaded:"
echo "Project ID: $PROJECT_ID"
echo "BigQuery Console: $BIGQUERY_CONSOLE_URL"
echo "Assessment URL: $ASSESSOR_PROJECT_URL"