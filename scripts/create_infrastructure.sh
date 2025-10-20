#!/bin/bash

# SARB Economic Pipeline - Infrastructure Creation Script
# This script creates the foundational infrastructure for the pipeline

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration with defaults
PROJECT_ID=${PROJECT_ID:-""}
BUCKET_NAME=${BUCKET_NAME:-""}
REGION=${REGION:-"europe-west1"}
DATASET_ID=${DATASET_ID:-"sarb_economic_data"}

# Validate required environment variables
validate_environment() {
    print_status "Validating environment variables..."
    
    local errors=0
    
    if [ -z "$PROJECT_ID" ]; then
        print_error "PROJECT_ID environment variable is required"
        errors=$((errors + 1))
    fi
    
    if [ -z "$BUCKET_NAME" ]; then
        print_error "BUCKET_NAME environment variable is required"
        errors=$((errors + 1))
    fi
    
    if [ $errors -gt 0 ]; then
        echo
        echo "Usage:"
        echo "  export PROJECT_ID=your-project-id"
        echo "  export BUCKET_NAME=your-bucket-name"
        echo "  export REGION=europe-west1  # Optional, defaults to europe-west1"
        echo "  export DATASET_ID=sarb_economic_data  # Optional"
        echo "  ./create_infrastructure.sh"
        exit 1
    fi
    
    print_success "Environment variables validated"
    echo "  PROJECT_ID: $PROJECT_ID"
    echo "  BUCKET_NAME: $BUCKET_NAME"
    echo "  REGION: $REGION"
    echo "  DATASET_ID: $DATASET_ID"
}

# Verify gcloud authentication
verify_auth() {
    print_status "Verifying Google Cloud authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active Google Cloud authentication found"
        echo "Please run: gcloud auth login"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    print_success "Authenticated for project: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    local apis=(
        "storage.googleapis.com"
        "bigquery.googleapis.com"
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "cloudscheduler.googleapis.com"
        "aiplatform.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "  Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID --quiet
    done
    
    print_success "All required APIs enabled"
}

# Create IAM service account
create_service_account() {
    print_status "Creating service account..."
    
    local sa_name="sarb-pipeline-sa"
    local sa_email="$sa_name@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $sa_email --project=$PROJECT_ID >/dev/null 2>&1; then
        gcloud iam service-accounts create $sa_name \
            --display-name="SARB Economic Pipeline Service Account" \
            --description="Service account for automated SARB economic data pipeline" \
            --project=$PROJECT_ID
        
        print_success "Service account created: $sa_email"
    else
        print_warning "Service account already exists: $sa_email"
    fi
    
    # Grant required IAM roles
    print_status "Granting IAM permissions..."
    
    local roles=(
        "roles/bigquery.dataEditor"
        "roles/bigquery.jobUser"
        "roles/storage.objectAdmin"
        "roles/aiplatform.user"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
        "roles/cloudscheduler.serviceAgent"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$sa_email" \
            --role="$role" \
            --project=$PROJECT_ID \
            --quiet >/dev/null
    done
    
    print_success "IAM permissions granted"
}

# Create Cloud Storage bucket
create_storage_bucket() {
    print_status "Creating Cloud Storage bucket..."
    
    # Check if bucket exists
    if gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
        print_warning "Bucket already exists: gs://$BUCKET_NAME"
        return
    fi
    
    # Create bucket
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    
    # Set up lifecycle policy for data management
    cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 365,
          "matchesPrefix": ["bronze/"]
        }
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["bronze/"]
        }
      }
    ]
  }
}
EOF
    
    gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
    rm lifecycle.json
    
    # Set uniform bucket-level access
    gsutil uniformbucketlevelaccess set on gs://$BUCKET_NAME
    
    print_success "Storage bucket created: gs://$BUCKET_NAME"
    echo "  Location: $REGION"
    echo "  Storage class: STANDARD"
    echo "  Lifecycle: Bronze data archived after 90 days, deleted after 365 days"
}

# Create BigQuery dataset and tables
create_bigquery_infrastructure() {
    print_status "Creating BigQuery infrastructure..."
    
    # Create dataset if it doesn't exist
    if ! bq ls -d $PROJECT_ID:$DATASET_ID >/dev/null 2>&1; then
        bq mk --dataset \
            --description="South African Reserve Bank Economic Indicators Dataset - Production" \
            --location=$REGION \
            --default_table_expiration=0 \
            $PROJECT_ID:$DATASET_ID
        
        print_success "BigQuery dataset created: $PROJECT_ID:$DATASET_ID"
    else
        print_warning "BigQuery dataset already exists: $PROJECT_ID:$DATASET_ID"
    fi
    
    # Apply DDL scripts
    print_status "Creating BigQuery tables and views..."
    
    if [ ! -f "infrastructure/bigquery_setup.sql" ]; then
        print_error "BigQuery setup script not found: infrastructure/bigquery_setup.sql"
        print_warning "Skipping BigQuery table creation"
        return
    fi
    
    # Replace dataset placeholder in SQL and execute
    sed "s/sarb_economic_data/$DATASET_ID/g" infrastructure/bigquery_setup.sql > temp_setup.sql
    
    if bq query --use_legacy_sql=false --project_id=$PROJECT_ID < temp_setup.sql; then
        print_success "BigQuery tables and views created"
        rm temp_setup.sql
    else
        print_error "Failed to create BigQuery infrastructure"
        rm temp_setup.sql
        exit 1
    fi
    
    # Set up dataset labels
    bq update --set_label environment:production --set_label project:sarb-pipeline $PROJECT_ID:$DATASET_ID
    
    print_success "BigQuery infrastructure setup complete"
}

# Create monitoring and alerting resources
setup_monitoring() {
    print_status "Setting up monitoring and logging..."
    
    # Create log-based metrics
    local metrics=(
        "pipeline_executions:Count of successful pipeline executions:jsonPayload.status=\"success\""
        "pipeline_failures:Count of pipeline failures:jsonPayload.status=\"failed\""
        "data_quality_issues:Count of data quality issues:jsonPayload.data_quality_check=\"failed\""
    )
    
    for metric_def in "${metrics[@]}"; do
        local metric_name=$(echo $metric_def | cut -d: -f1)
        local description=$(echo $metric_def | cut -d: -f2)
        local filter=$(echo $metric_def | cut -d: -f3)
        
        gcloud logging metrics create $metric_name \
            --description="$description" \
            --log-filter="resource.type=\"cloud_run_revision\" AND $filter" \
            --project=$PROJECT_ID 2>/dev/null || true
    done
    
    print_success "Monitoring metrics created"
}

# Verify infrastructure
verify_infrastructure() {
    print_status "Verifying infrastructure creation..."
    
    local errors=0
    
    # Check BigQuery dataset
    if bq ls -d $PROJECT_ID:$DATASET_ID >/dev/null 2>&1; then
        print_success "✓ BigQuery dataset verified"
    else
        print_error "✗ BigQuery dataset not found"
        errors=$((errors + 1))
    fi
    
    # Check storage bucket
    if gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
        print_success "✓ Storage bucket verified"
    else
        print_error "✗ Storage bucket not found"
        errors=$((errors + 1))
    fi
    
    # Check service account
    if gcloud iam service-accounts describe sarb-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID >/dev/null 2>&1; then
        print_success "✓ Service account verified"
    else
        print_error "✗ Service account not found"
        errors=$((errors + 1))
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "All infrastructure components verified successfully"
        return 0
    else
        print_error "$errors infrastructure components failed verification"
        return 1
    fi
}

# Main function
main() {
    echo "==========================================="
    echo "SARB Economic Pipeline Infrastructure Setup"
    echo "==========================================="
    echo
    
    validate_environment
    verify_auth
    
    print_status "Starting infrastructure creation..."
    
    enable_apis
    create_service_account
    create_storage_bucket
    create_bigquery_infrastructure
    setup_monitoring
    
    echo
    print_status "Verifying infrastructure..."
    if verify_infrastructure; then
        echo
        echo "==========================================="
        print_success "Infrastructure setup completed successfully!"
        echo "==========================================="
        echo
        echo "📋 Infrastructure Summary:"
        echo "  • Project: $PROJECT_ID"
        echo "  • Region: $REGION"
        echo "  • Storage Bucket: gs://$BUCKET_NAME"
        echo "  • BigQuery Dataset: $PROJECT_ID:$DATASET_ID"
        echo "  • Service Account: sarb-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com"
        echo
        echo "🚀 Next Steps:"
        echo "  1. Deploy the application: ./scripts/deploy.sh"
        echo "  2. Setup scheduler: ./scripts/setup_scheduler.sh"
        echo "  3. Run analysis notebook: analysis/sarb_macroeconomic_analysis.ipynb"
        echo
        print_success "Ready for application deployment! 🎉"
    else
        print_error "Infrastructure verification failed. Please check the errors above."
        exit 1
    fi
}

# Execute main function
main "$@"