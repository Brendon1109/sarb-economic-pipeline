#!/bin/bash

# SARB Economic Pipeline - Access Management Script
# This script helps set up access for team members to the GCP project

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
USER_EMAIL=${USER_EMAIL:-""}
ROLE_TYPE=${ROLE_TYPE:-""}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --project-id PROJECT_ID    GCP Project ID"
    echo "  --user-email EMAIL         User's email address"
    echo "  --role ROLE_TYPE          Role type: analyst|engineer|devops|manager|viewer"
    echo "  --help                    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --project-id sarb-pipeline-prod --user-email analyst@company.com --role analyst"
    echo "  $0 --project-id sarb-pipeline-dev --user-email engineer@company.com --role engineer"
    echo ""
    echo "Role Types:"
    echo "  analyst  - BigQuery data viewer and job user"
    echo "  engineer - BigQuery data editor, storage admin, Cloud Run developer"
    echo "  devops   - Full editor access with service account admin"
    echo "  manager  - Project viewer with BigQuery data viewer"
    echo "  viewer   - Read-only access to all resources"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --user-email)
            USER_EMAIL="$2"
            shift 2
            ;;
        --role)
            ROLE_TYPE="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate inputs
validate_inputs() {
    if [ -z "$PROJECT_ID" ]; then
        print_error "Project ID is required"
        show_usage
        exit 1
    fi

    if [ -z "$USER_EMAIL" ]; then
        print_error "User email is required"
        show_usage
        exit 1
    fi

    if [ -z "$ROLE_TYPE" ]; then
        print_error "Role type is required"
        show_usage
        exit 1
    fi

    # Validate role type
    case $ROLE_TYPE in
        analyst|engineer|devops|manager|viewer)
            ;;
        *)
            print_error "Invalid role type: $ROLE_TYPE"
            print_error "Valid roles: analyst, engineer, devops, manager, viewer"
            exit 1
            ;;
    esac

    print_success "Inputs validated successfully"
}

# Check authentication
check_auth() {
    print_status "Checking Google Cloud authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active Google Cloud authentication found"
        echo "Please run: gcloud auth login"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    print_success "Authenticated for project: $PROJECT_ID"
}

# Grant permissions based on role
grant_analyst_permissions() {
    print_status "Granting Data Analyst permissions to $USER_EMAIL..."
    
    local roles=(
        "roles/bigquery.dataViewer"
        "roles/bigquery.jobUser"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="user:$USER_EMAIL" \
            --role="$role"
        print_success "Granted $role"
    done
}

grant_engineer_permissions() {
    print_status "Granting Data Engineer permissions to $USER_EMAIL..."
    
    local roles=(
        "roles/bigquery.dataEditor"
        "roles/bigquery.jobUser"
        "roles/storage.objectAdmin"
        "roles/run.developer"
        "roles/cloudbuild.builds.editor"
        "roles/logging.viewer"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="user:$USER_EMAIL" \
            --role="$role"
        print_success "Granted $role"
    done
}

grant_devops_permissions() {
    print_status "Granting DevOps permissions to $USER_EMAIL..."
    
    local roles=(
        "roles/editor"
        "roles/iam.serviceAccountAdmin"
        "roles/resourcemanager.projectIamAdmin"
        "roles/run.admin"
        "roles/cloudbuild.builds.editor"
        "roles/cloudscheduler.admin"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="user:$USER_EMAIL" \
            --role="$role"
        print_success "Granted $role"
    done
}

grant_manager_permissions() {
    print_status "Granting Manager permissions to $USER_EMAIL..."
    
    local roles=(
        "roles/viewer"
        "roles/bigquery.dataViewer"
        "roles/monitoring.viewer"
        "roles/logging.viewer"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="user:$USER_EMAIL" \
            --role="$role"
        print_success "Granted $role"
    done
}

grant_viewer_permissions() {
    print_status "Granting Viewer permissions to $USER_EMAIL..."
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="user:$USER_EMAIL" \
        --role="roles/viewer"
    print_success "Granted roles/viewer"
}

# Main function to grant permissions
grant_permissions() {
    case $ROLE_TYPE in
        analyst)
            grant_analyst_permissions
            ;;
        engineer)
            grant_engineer_permissions
            ;;
        devops)
            grant_devops_permissions
            ;;
        manager)
            grant_manager_permissions
            ;;
        viewer)
            grant_viewer_permissions
            ;;
    esac
}

# Verify permissions
verify_permissions() {
    print_status "Verifying permissions for $USER_EMAIL..."
    
    echo ""
    echo "Current IAM bindings for $USER_EMAIL:"
    gcloud projects get-iam-policy $PROJECT_ID \
        --flatten="bindings[].members" \
        --format="table(bindings.role)" \
        --filter="bindings.members:user:$USER_EMAIL"
    
    print_success "Permissions verification complete"
}

# Send notification email (placeholder)
send_notification() {
    print_status "Access granted successfully!"
    echo ""
    echo "============================================"
    echo "ACCESS GRANTED SUMMARY"
    echo "============================================"
    echo "Project ID: $PROJECT_ID"
    echo "User Email: $USER_EMAIL"
    echo "Role Type: $ROLE_TYPE"
    echo "Date: $(date)"
    echo ""
    echo "Next Steps for $USER_EMAIL:"
    echo "1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    echo "2. Authenticate: gcloud auth login"
    echo "3. Set project: gcloud config set project $PROJECT_ID"
    echo "4. Clone repository: git clone <repository-url>"
    echo "5. Follow README.md for setup instructions"
    echo ""
    echo "Resources accessible:"
    case $ROLE_TYPE in
        analyst)
            echo "- BigQuery datasets (read-only)"
            echo "- Run queries on economic indicators"
            ;;
        engineer)
            echo "- BigQuery datasets (read/write)"
            echo "- Cloud Storage buckets"
            echo "- Cloud Run services"
            echo "- Build and deployment"
            ;;
        devops)
            echo "- Full project access"
            echo "- Infrastructure management"
            echo "- Service account administration"
            ;;
        manager)
            echo "- Project monitoring and logs"
            echo "- BigQuery data viewing"
            echo "- Resource usage and costs"
            ;;
        viewer)
            echo "- Read-only access to all resources"
            ;;
    esac
    echo "============================================"
}

# Main execution
main() {
    print_status "Starting access management for SARB Economic Pipeline"
    
    validate_inputs
    check_auth
    grant_permissions
    verify_permissions
    send_notification
    
    print_success "Access management completed successfully!"
}

# Run main function
main "$@"