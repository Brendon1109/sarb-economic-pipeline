# Access Management Guide

This document provides instructions for providing access to the SARB Economic Pipeline repository and GCP project.

## Repository Access

### 1. Create GitHub Repository

```bash
# Create a new repository on GitHub (via web interface or GitHub CLI)
gh repo create sarb-economic-pipeline --public --description "South African Macroeconomic Indicators Pipeline & AI Analyst"

# Add GitHub as remote origin
git remote add origin https://github.com/Brendon1109/sarb-economic-pipeline.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Grant Repository Access

#### For Collaborators:
1. Go to GitHub repository → Settings → Manage access
2. Click "Invite a collaborator"
3. Enter GitHub username or email
4. Select permission level:
   - **Read**: View and clone repository
   - **Write**: Read + create branches, push changes
   - **Admin**: Full access including repository settings

#### Access Levels:
- **Viewers**: Can view and clone the repository
- **Contributors**: Can create branches, submit PRs, and push to designated branches
- **Maintainers**: Can manage releases, merge PRs, and modify repository settings
- **Owners**: Full administrative access

### 3. Repository Structure
```
sarb-economic-pipeline/
├── src/main.py                    # Main application code
├── analysis/                      # Jupyter notebooks and insights
├── infrastructure/               # BigQuery setup scripts
├── scripts/                      # Deployment and setup scripts
├── Dockerfile                    # Container configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

---

## GCP Project Access

### Current Project Configuration
- **Project ID**: Set via `GCP_PROJECT_ID` environment variable
- **Region**: `europe-west1` (default)
- **Dataset**: `sarb_economic_data`
- **Services Used**:
  - Cloud Run
  - Cloud Storage
  - BigQuery
  - Vertex AI
  - Cloud Scheduler

### 1. IAM Roles for Team Members

#### Data Analysts
```bash
# View BigQuery data and run queries
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:analyst@company.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:analyst@company.com" \
  --role="roles/bigquery.jobUser"
```

#### Data Engineers
```bash
# Full BigQuery and Storage access for pipeline management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:engineer@company.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:engineer@company.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:engineer@company.com" \
  --role="roles/run.developer"
```

#### DevOps/Platform Engineers
```bash
# Full deployment and infrastructure management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:devops@company.com" \
  --role="roles/editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:devops@company.com" \
  --role="roles/iam.serviceAccountAdmin"
```

#### Project Managers/Stakeholders
```bash
# Read-only access to monitor resources and costs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:manager@company.com" \
  --role="roles/viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:manager@company.com" \
  --role="roles/bigquery.dataViewer"
```

### 2. Service Account Access

#### Pipeline Service Account
Current service account: `sarb-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com`

**Permissions:**
- `roles/bigquery.dataEditor`
- `roles/bigquery.jobUser`
- `roles/storage.objectAdmin`
- `roles/aiplatform.user`
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`

#### Create Additional Service Accounts (if needed)
```bash
# For external integrations
gcloud iam service-accounts create external-api-sa \
  --display-name="External API Service Account"

# Generate and download key
gcloud iam service-accounts keys create external-api-key.json \
  --iam-account=external-api-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 3. Resource-Level Access

#### BigQuery Dataset Access
```bash
# Grant access to specific dataset
bq add-iam-policy-binding \
  --member="user:analyst@company.com" \
  --role="roles/bigquery.dataViewer" \
  $PROJECT_ID:sarb_economic_data
```

#### Cloud Storage Bucket Access
```bash
# Grant access to specific bucket
gsutil iam ch user:analyst@company.com:legacyBucketReader gs://$BUCKET_NAME
```

### 4. Access Verification Commands

#### Check Current Permissions
```bash
# List all IAM bindings for the project
gcloud projects get-iam-policy $PROJECT_ID

# Check specific user's roles
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:user@company.com"
```

#### Test BigQuery Access
```bash
# Test query access
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`$PROJECT_ID.sarb_economic_data.silver_economic_indicators\`"
```

---

## Security Best Practices

### 1. Principle of Least Privilege
- Grant minimum permissions necessary for each role
- Use predefined roles when possible
- Regularly review and audit permissions

### 2. Environment Separation
```bash
# Create separate projects for different environments
export DEV_PROJECT_ID="sarb-pipeline-dev"
export STAGING_PROJECT_ID="sarb-pipeline-staging"
export PROD_PROJECT_ID="sarb-pipeline-prod"
```

### 3. Access Monitoring
```bash
# Enable audit logging
gcloud logging sinks create sarb-audit-sink \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/audit_logs \
  --log-filter="protoPayload.authenticationInfo.principalEmail:*"
```

### 4. Key Management
- Rotate service account keys regularly
- Use workload identity for GKE/Cloud Run when possible
- Store secrets in Secret Manager, not environment variables

---

## Quick Access Commands

### Repository Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/sarb-economic-pipeline.git
cd sarb-economic-pipeline

# Set up environment
export PROJECT_ID="your-project-id"
export BUCKET_NAME="your-bucket-name"
export REGION="europe-west1"
```

### GCP Authentication
```bash
# Authenticate with Google Cloud
gcloud auth login

# Set default project
gcloud config set project $PROJECT_ID

# Verify access
gcloud projects describe $PROJECT_ID
```

### Quick Deployment
```bash
# Run infrastructure setup
chmod +x scripts/create_infrastructure.sh
./scripts/create_infrastructure.sh

# Deploy application
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

---

## Contact Information

For access requests or issues:
1. Create an issue in the GitHub repository
2. Contact the project administrator
3. Email: [your-email@company.com]

## Additional Resources

- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)
- [GitHub Permissions Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-teams-and-people-with-access-to-your-repository)
- [BigQuery Access Control](https://cloud.google.com/bigquery/docs/access-control)