#!/bin/bash

# SARB Economic Pipeline - Cloud Scheduler Setup Script
# This script sets up Cloud Scheduler for automated pipeline execution

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

# Configuration
PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"europe-west1"}
SERVICE_NAME=${SERVICE_NAME:-"sarb-economic-pipeline"}
JOB_NAME=${JOB_NAME:-"sarb-daily-pipeline"}
SCHEDULE=${SCHEDULE:-"0 2 * * *"}  # Daily at 2 AM
TIMEZONE=${TIMEZONE:-"Africa/Johannesburg"}

# Validate environment
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID environment variable is required"
    echo "Usage: export PROJECT_ID=your-project-id && ./setup_scheduler.sh"
    exit 1
fi

print_status "Setting up Cloud Scheduler for SARB Economic Pipeline"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Schedule: $SCHEDULE ($TIMEZONE)"
echo

# Get Cloud Run service URL
print_status "Retrieving Cloud Run service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)" 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    print_error "Cloud Run service '$SERVICE_NAME' not found in region '$REGION'"
    echo "Please deploy the service first using deploy.sh"
    exit 1
fi

print_success "Found Cloud Run service: $SERVICE_URL"

# Enable Cloud Scheduler API
print_status "Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Delete existing job if it exists
if gcloud scheduler jobs describe $JOB_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    print_warning "Existing scheduler job found, deleting..."
    gcloud scheduler jobs delete $JOB_NAME \
        --location=$REGION \
        --project=$PROJECT_ID \
        --quiet
    print_success "Existing job deleted"
fi

# Create the scheduler job
print_status "Creating Cloud Scheduler job..."
gcloud scheduler jobs create http $JOB_NAME \
    --schedule="$SCHEDULE" \
    --uri="$SERVICE_URL/run-pipeline" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --time-zone="$TIMEZONE" \
    --description="Automated daily execution of SARB economic indicators data pipeline" \
    --headers="Content-Type=application/json" \
    --message-body='{"source": "cloud-scheduler", "trigger_time": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}'

print_success "Cloud Scheduler job created successfully!"

# Display job details
print_status "Scheduler job details:"
gcloud scheduler jobs describe $JOB_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="table(name,schedule,timeZone,httpTarget.uri,state)"

# Test the scheduler job (optional)
echo
read -p "Would you like to test the scheduler job now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running test execution..."
    gcloud scheduler jobs run $JOB_NAME \
        --location=$REGION \
        --project=$PROJECT_ID
    
    print_success "Test execution triggered!"
    echo "Monitor execution: gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
    echo "View logs: gcloud logs tail --follow --filter='resource.type=\"cloud_run_revision\"'"
fi

echo
print_success "Cloud Scheduler setup complete!"
echo
echo "📅 Schedule Summary:"
echo "  Job Name: $JOB_NAME"
echo "  Schedule: $SCHEDULE"
echo "  Timezone: $TIMEZONE"
echo "  Target: $SERVICE_URL/run-pipeline"
echo "  Next Run: $(gcloud scheduler jobs describe $JOB_NAME --location=$REGION --format='value(scheduleTime)' 2>/dev/null || echo 'Check in GCP Console')"
echo
echo "🔧 Management Commands:"
echo "  View job: gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
echo "  Run manually: gcloud scheduler jobs run $JOB_NAME --location=$REGION"
echo "  Pause job: gcloud scheduler jobs pause $JOB_NAME --location=$REGION"
echo "  Resume job: gcloud scheduler jobs resume $JOB_NAME --location=$REGION"
echo "  Delete job: gcloud scheduler jobs delete $JOB_NAME --location=$REGION"