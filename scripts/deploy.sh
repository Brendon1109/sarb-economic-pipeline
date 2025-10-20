#!/bin/bash

# SARB Economic Pipeline - Deployment Script
# This script deploys the complete infrastructure and application to Google Cloud Platform

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_environment() {
    print_status "Checking environment variables..."
    
    if [ -z "$PROJECT_ID" ]; then
        print_error "PROJECT_ID environment variable is not set"
        echo "Usage: export PROJECT_ID=your-project-id"
        exit 1
    fi
    
    if [ -z "$BUCKET_NAME" ]; then
        print_error "BUCKET_NAME environment variable is not set"
        echo "Usage: export BUCKET_NAME=your-bucket-name"
        exit 1
    fi
    
    # Set default region if not provided
    if [ -z "$REGION" ]; then
        export REGION="europe-west1"
        print_warning "REGION not set, defaulting to europe-west1"
    fi
    
    # Set default dataset if not provided
    if [ -z "$DATASET_ID" ]; then
        export DATASET_ID="sarb_economic_data"
        print_warning "DATASET_ID not set, defaulting to sarb_economic_data"
    fi
    
    print_success "Environment variables validated"
    echo "  PROJECT_ID: $PROJECT_ID"
    echo "  BUCKET_NAME: $BUCKET_NAME"
    echo "  REGION: $REGION"
    echo "  DATASET_ID: $DATASET_ID"
}

# Verify Google Cloud authentication and project
verify_gcloud_auth() {
    print_status "Verifying Google Cloud authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active Google Cloud authentication found"
        echo "Please run: gcloud auth login"
        exit 1
    fi
    
    # Set the project
    gcloud config set project $PROJECT_ID
    print_success "Google Cloud authentication verified for project: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "storage.googleapis.com"
        "bigquery.googleapis.com"
        "cloudscheduler.googleapis.com"
        "aiplatform.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done
    
    print_success "All required APIs enabled"
}

# Create service account with required permissions
create_service_account() {
    print_status "Creating service account for the pipeline..."
    
    SERVICE_ACCOUNT_NAME="sarb-pipeline-sa"
    SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL >/dev/null 2>&1; then
        gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
            --display-name="SARB Economic Pipeline Service Account" \
            --description="Service account for SARB economic data pipeline"
        print_success "Service account created: $SERVICE_ACCOUNT_EMAIL"
    else
        print_warning "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
    fi
    
    # Grant required permissions
    print_status "Granting IAM permissions to service account..."
    
    roles=(
        "roles/bigquery.dataEditor"
        "roles/bigquery.jobUser"
        "roles/storage.objectAdmin"
        "roles/aiplatform.user"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
            --role="$role" >/dev/null
    done
    
    print_success "IAM permissions granted to service account"
}

# Create Cloud Storage bucket
create_storage_bucket() {
    print_status "Creating Cloud Storage bucket..."
    
    if ! gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
        gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
        
        # Set lifecycle policy for bronze layer data (optional cleanup after 1 year)
        cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 365,
          "matchesPrefix": ["bronze/"]
        }
      }
    ]
  }
}
EOF
        gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
        rm lifecycle.json
        
        print_success "Storage bucket created: gs://$BUCKET_NAME"
    else
        print_warning "Storage bucket already exists: gs://$BUCKET_NAME"
    fi
}

# Create BigQuery dataset and tables
create_bigquery_infrastructure() {
    print_status "Creating BigQuery infrastructure..."
    
    # Create dataset if it doesn't exist
    if ! bq ls -d $PROJECT_ID:$DATASET_ID >/dev/null 2>&1; then
        bq mk --dataset \
            --description="South African Reserve Bank Economic Indicators Dataset" \
            --location=$REGION \
            $PROJECT_ID:$DATASET_ID
        print_success "BigQuery dataset created: $PROJECT_ID:$DATASET_ID"
    else
        print_warning "BigQuery dataset already exists: $PROJECT_ID:$DATASET_ID"
    fi
    
    # Run BigQuery setup script
    print_status "Creating BigQuery tables and views..."
    if [ -f "infrastructure/bigquery_setup.sql" ]; then
        # Replace placeholders in SQL file
        sed "s/sarb_economic_data/$DATASET_ID/g" infrastructure/bigquery_setup.sql > temp_setup.sql
        
        bq query --use_legacy_sql=false --project_id=$PROJECT_ID < temp_setup.sql
        rm temp_setup.sql
        
        print_success "BigQuery tables and views created"
    else
        print_error "BigQuery setup script not found: infrastructure/bigquery_setup.sql"
        exit 1
    fi
}

# Build and deploy Cloud Run service
deploy_cloud_run() {
    print_status "Building and deploying Cloud Run service..."
    
    SERVICE_NAME="sarb-economic-pipeline"
    SERVICE_ACCOUNT_EMAIL="sarb-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Build and deploy using Cloud Build
    gcloud run deploy $SERVICE_NAME \
        --source . \
        --platform managed \
        --region $REGION \
        --service-account $SERVICE_ACCOUNT_EMAIL \
        --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET_NAME=$BUCKET_NAME,BIGQUERY_DATASET_ID=$DATASET_ID,GCP_REGION=$REGION,ENABLE_AI_ANALYSIS=true" \
        --memory 2Gi \
        --cpu 2 \
        --timeout 900 \
        --max-instances 10 \
        --min-instances 0 \
        --allow-unauthenticated \
        --port 8080
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_success "Cloud Run service deployed successfully"
    echo "  Service URL: $SERVICE_URL"
    
    # Test the health endpoint
    print_status "Testing service health endpoint..."
    if curl -s "$SERVICE_URL/" | grep -q "healthy"; then
        print_success "Service health check passed"
    else
        print_warning "Service health check failed - service may still be starting"
    fi
    
    # Export service URL for scheduler setup
    export SERVICE_URL
}

# Setup Cloud Scheduler job
setup_cloud_scheduler() {
    print_status "Setting up Cloud Scheduler job..."
    
    JOB_NAME="sarb-daily-pipeline"
    
    # Delete existing job if it exists
    if gcloud scheduler jobs describe $JOB_NAME --location=$REGION >/dev/null 2>&1; then
        print_warning "Existing scheduler job found, deleting..."
        gcloud scheduler jobs delete $JOB_NAME --location=$REGION --quiet
    fi
    
    # Create new scheduler job
    gcloud scheduler jobs create http $JOB_NAME \
        --schedule="0 2 * * *" \
        --uri="$SERVICE_URL/run-pipeline" \
        --http-method=POST \
        --location=$REGION \
        --time-zone="Africa/Johannesburg" \
        --description="Daily execution of SARB economic indicators pipeline"
    
    print_success "Cloud Scheduler job created: $JOB_NAME"
    echo "  Schedule: Daily at 2:00 AM (Africa/Johannesburg)"
    echo "  Target: $SERVICE_URL/run-pipeline"
}

# Run a test execution
test_pipeline() {
    print_status "Running test pipeline execution..."
    
    response=$(curl -s -X POST "$SERVICE_URL/manual-trigger" \
        -H "Content-Type: application/json" \
        -w "%{http_code}")
    
    http_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        print_success "Test pipeline execution completed successfully"
        echo "Response: $response_body"
    else
        print_warning "Test pipeline execution returned status $http_code"
        echo "Response: $response_body"
    fi
}

# Create monitoring dashboard (optional)
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Create log-based metrics for monitoring
    gcloud logging metrics create pipeline_executions \
        --description="Count of pipeline executions" \
        --log-filter='resource.type="cloud_run_revision" AND jsonPayload.message="Pipeline execution completed"' || true
    
    gcloud logging metrics create pipeline_errors \
        --description="Count of pipeline errors" \
        --log-filter='resource.type="cloud_run_revision" AND severity="ERROR"' || true
    
    print_success "Basic monitoring metrics created"
    echo "  - pipeline_executions: Tracks successful pipeline runs"
    echo "  - pipeline_errors: Tracks error occurrences"
    echo "  View logs: gcloud logging read 'resource.type=\"cloud_run_revision\"'"
}

# Main deployment function
main() {
    echo "======================================"
    echo "SARB Economic Pipeline Deployment"
    echo "======================================"
    echo
    
    # Pre-deployment checks
    check_environment
    verify_gcloud_auth
    
    # Infrastructure setup
    print_status "Starting infrastructure deployment..."
    enable_apis
    create_service_account
    create_storage_bucket
    create_bigquery_infrastructure
    
    # Application deployment
    print_status "Starting application deployment..."
    deploy_cloud_run
    setup_cloud_scheduler
    
    # Post-deployment
    setup_monitoring
    test_pipeline
    
    echo
    echo "======================================"
    print_success "Deployment completed successfully!"
    echo "======================================"
    echo
    echo "🚀 Deployment Summary:"
    echo "  • Project: $PROJECT_ID"
    echo "  • Region: $REGION"
    echo "  • Service URL: $SERVICE_URL"
    echo "  • Storage Bucket: gs://$BUCKET_NAME"
    echo "  • BigQuery Dataset: $PROJECT_ID:$DATASET_ID"
    echo "  • Scheduler Job: $JOB_NAME (runs daily at 2 AM)"
    echo
    echo "📊 Next Steps:"
    echo "  1. Test manual execution: curl -X POST $SERVICE_URL/manual-trigger"
    echo "  2. View logs: gcloud logs tail --follow --format='value(timestamp,severity,textPayload)'"
    echo "  3. Query gold data: bq query 'SELECT * FROM \`$PROJECT_ID.$DATASET_ID.gold_macroeconomic_report\` LIMIT 10'"
    echo "  4. Open analysis notebook: analysis/sarb_macroeconomic_analysis.ipynb"
    echo
    print_success "Happy data engineering! 🎉"
}

# Execute main function
main "$@"