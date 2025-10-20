# SARB Economic Pipeline - Access Management Script (PowerShell)
# This script helps set up access for team members to the GCP project

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$UserEmail,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("analyst", "engineer", "devops", "manager", "viewer")]
    [string]$RoleType
)

# Color functions for output
function Write-StatusMessage {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Usage {
    Write-Host "Usage: .\grant_access.ps1 -ProjectId PROJECT_ID -UserEmail EMAIL -RoleType ROLE"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -ProjectId      GCP Project ID"
    Write-Host "  -UserEmail      User's email address"
    Write-Host "  -RoleType       Role type: analyst|engineer|devops|manager|viewer"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\grant_access.ps1 -ProjectId sarb-pipeline-prod -UserEmail analyst@company.com -RoleType analyst"
    Write-Host "  .\grant_access.ps1 -ProjectId sarb-pipeline-dev -UserEmail engineer@company.com -RoleType engineer"
    Write-Host ""
    Write-Host "Role Types:"
    Write-Host "  analyst  - BigQuery data viewer and job user"
    Write-Host "  engineer - BigQuery data editor, storage admin, Cloud Run developer"
    Write-Host "  devops   - Full editor access with service account admin"
    Write-Host "  manager  - Project viewer with BigQuery data viewer"
    Write-Host "  viewer   - Read-only access to all resources"
}

function Test-Authentication {
    Write-StatusMessage "Checking Google Cloud authentication..."
    
    try {
        $authOutput = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
        if ([string]::IsNullOrEmpty($authOutput)) {
            Write-ErrorMessage "No active Google Cloud authentication found"
            Write-Host "Please run: gcloud auth login"
            exit 1
        }
        
        # Set project
        gcloud config set project $ProjectId | Out-Null
        Write-SuccessMessage "Authenticated for project: $ProjectId"
    }
    catch {
        Write-ErrorMessage "Failed to authenticate with Google Cloud"
        Write-Host "Please ensure Google Cloud SDK is installed and run: gcloud auth login"
        exit 1
    }
}

function Grant-AnalystPermissions {
    Write-StatusMessage "Granting Data Analyst permissions to $UserEmail..."
    
    $roles = @(
        "roles/bigquery.dataViewer",
        "roles/bigquery.jobUser"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $ProjectId --member="user:$UserEmail" --role="$role" | Out-Null
        Write-SuccessMessage "Granted $role"
    }
}

function Grant-EngineerPermissions {
    Write-StatusMessage "Granting Data Engineer permissions to $UserEmail..."
    
    $roles = @(
        "roles/bigquery.dataEditor",
        "roles/bigquery.jobUser",
        "roles/storage.objectAdmin",
        "roles/run.developer",
        "roles/cloudbuild.builds.editor",
        "roles/logging.viewer"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $ProjectId --member="user:$UserEmail" --role="$role" | Out-Null
        Write-SuccessMessage "Granted $role"
    }
}

function Grant-DevOpsPermissions {
    Write-StatusMessage "Granting DevOps permissions to $UserEmail..."
    
    $roles = @(
        "roles/editor",
        "roles/iam.serviceAccountAdmin",
        "roles/resourcemanager.projectIamAdmin",
        "roles/run.admin",
        "roles/cloudbuild.builds.editor",
        "roles/cloudscheduler.admin"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $ProjectId --member="user:$UserEmail" --role="$role" | Out-Null
        Write-SuccessMessage "Granted $role"
    }
}

function Grant-ManagerPermissions {
    Write-StatusMessage "Granting Manager permissions to $UserEmail..."
    
    $roles = @(
        "roles/viewer",
        "roles/bigquery.dataViewer",
        "roles/monitoring.viewer",
        "roles/logging.viewer"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $ProjectId --member="user:$UserEmail" --role="$role" | Out-Null
        Write-SuccessMessage "Granted $role"
    }
}

function Grant-ViewerPermissions {
    Write-StatusMessage "Granting Viewer permissions to $UserEmail..."
    
    gcloud projects add-iam-policy-binding $ProjectId --member="user:$UserEmail" --role="roles/viewer" | Out-Null
    Write-SuccessMessage "Granted roles/viewer"
}

function Grant-Permissions {
    switch ($RoleType) {
        "analyst" { Grant-AnalystPermissions }
        "engineer" { Grant-EngineerPermissions }
        "devops" { Grant-DevOpsPermissions }
        "manager" { Grant-ManagerPermissions }
        "viewer" { Grant-ViewerPermissions }
    }
}

function Test-Permissions {
    Write-StatusMessage "Verifying permissions for $UserEmail..."
    
    Write-Host ""
    Write-Host "Current IAM bindings for $UserEmail:"
    gcloud projects get-iam-policy $ProjectId --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:user:$UserEmail"
    
    Write-SuccessMessage "Permissions verification complete"
}

function Show-AccessSummary {
    Write-StatusMessage "Access granted successfully!"
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "ACCESS GRANTED SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Project ID: $ProjectId"
    Write-Host "User Email: $UserEmail"
    Write-Host "Role Type: $RoleType"
    Write-Host "Date: $(Get-Date)"
    Write-Host ""
    Write-Host "Next Steps for $UserEmail:"
    Write-Host "1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    Write-Host "2. Authenticate: gcloud auth login"
    Write-Host "3. Set project: gcloud config set project $ProjectId"
    Write-Host "4. Clone repository: git clone <repository-url>"
    Write-Host "5. Follow README.md for setup instructions"
    Write-Host ""
    Write-Host "Resources accessible:"
    
    switch ($RoleType) {
        "analyst" {
            Write-Host "- BigQuery datasets (read-only)"
            Write-Host "- Run queries on economic indicators"
        }
        "engineer" {
            Write-Host "- BigQuery datasets (read/write)"
            Write-Host "- Cloud Storage buckets"
            Write-Host "- Cloud Run services"
            Write-Host "- Build and deployment"
        }
        "devops" {
            Write-Host "- Full project access"
            Write-Host "- Infrastructure management"
            Write-Host "- Service account administration"
        }
        "manager" {
            Write-Host "- Project monitoring and logs"
            Write-Host "- BigQuery data viewing"
            Write-Host "- Resource usage and costs"
        }
        "viewer" {
            Write-Host "- Read-only access to all resources"
        }
    }
    Write-Host "============================================" -ForegroundColor Cyan
}

# Main execution
try {
    Write-StatusMessage "Starting access management for SARB Economic Pipeline"
    
    Test-Authentication
    Grant-Permissions
    Test-Permissions
    Show-AccessSummary
    
    Write-SuccessMessage "Access management completed successfully!"
}
catch {
    Write-ErrorMessage "An error occurred: $($_.Exception.Message)"
    exit 1
}