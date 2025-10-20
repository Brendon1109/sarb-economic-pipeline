# Access Setup for Lyle (lyle@automationarchitects.ai)

## Repository Access

### GitHub Repository
- **URL**: https://github.com/Brendon1109/sarb-economic-pipeline
- **Access Level**: Collaborator (Write access recommended for contribution)

### Steps for Repository Owner (Brendon1109):
1. **Create the repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `sarb-economic-pipeline`
   - Description: "South African Macroeconomic Indicators Pipeline & AI Analyst"
   - Make it Public (or Private based on preference)
   - Click "Create repository"

2. **Push local code to GitHub**:
   ```bash
   git remote add origin https://github.com/Brendon1109/sarb-economic-pipeline.git
   git branch -M main
   git push -u origin main
   ```

3. **Add Lyle as a collaborator**:
   - Go to repository → Settings → Manage access
   - Click "Invite a collaborator"
   - Enter: `lyle@automationarchitects.ai` or GitHub username
   - Select: "Write" permission level
   - Send invitation

## GCP Project Access

### Recommended Role for Lyle
Based on the email domain `automationarchitects.ai`, Lyle appears to be a technical consultant. Recommended role: **Engineer** (full development access).

### Grant GCP Access (PowerShell)
```powershell
# Set variables
$ProjectId = "your-actual-project-id"  # Replace with your GCP project ID
$UserEmail = "lyle@automationarchitects.ai"
$RoleType = "engineer"

# Run access script
.\scripts\grant_access.ps1 -ProjectId $ProjectId -UserEmail $UserEmail -RoleType $RoleType
```

### Manual GCP Access Grant (if script not available)
```bash
# Set your project ID
export PROJECT_ID="your-actual-project-id"

# Grant Data Engineer permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:lyle@automationarchitects.ai" \
  --role="roles/logging.viewer"
```

## Access Verification

### Verify GCP Permissions
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:user:lyle@automationarchitects.ai"
```

## Information to Send to Lyle

### Email Template
```
Subject: Access Granted - SARB Economic Pipeline Project

Hi Lyle,

You now have access to the SARB Economic Pipeline project:

📂 **Repository Access**:
- URL: https://github.com/Brendon1109/sarb-economic-pipeline
- Access Level: Collaborator (Write access)
- Clone: git clone https://github.com/Brendon1109/sarb-economic-pipeline.git

☁️ **GCP Project Access**:
- Project ID: [YOUR_PROJECT_ID]
- Role: Data Engineer (BigQuery, Storage, Cloud Run access)
- Authenticate: gcloud auth login
- Set project: gcloud config set project [YOUR_PROJECT_ID]

📋 **Next Steps**:
1. Clone the repository
2. Follow README.md for setup instructions  
3. Check ACCESS_MANAGEMENT.md for detailed documentation
4. Review QUICK_ACCESS_REFERENCE.md for common commands

🔧 **What you can do**:
- Read/write BigQuery datasets
- Manage Cloud Storage buckets
- Deploy Cloud Run services
- Build and modify the pipeline
- View logs and monitoring

Let me know if you need any help getting started!

Best regards,
[Your Name]
```

## Security Notes

- **Access Review**: Lyle's access should be reviewed periodically
- **Time-bound**: Consider setting an access expiration date if this is project-based work
- **Monitoring**: Monitor Lyle's resource usage in GCP console
- **Documentation**: All access has been documented in project files

## Troubleshooting for Lyle

### Common Setup Issues
1. **GitHub Access**: Check email for GitHub invitation
2. **GCP Authentication**: Run `gcloud auth login` and follow browser prompts
3. **Project Access**: Verify project ID is set correctly
4. **Permission Errors**: Contact project administrator if access is denied

### Useful Commands for Lyle
```bash
# Check current GCP authentication
gcloud auth list

# Verify project access
gcloud projects describe $PROJECT_ID

# Test BigQuery access
bq ls $PROJECT_ID:sarb_economic_data

# Test storage access
gsutil ls gs://your-bucket-name
```

---
**Date Created**: $(Get-Date)
**Created By**: Project Administrator
**Access Level**: Data Engineer
**Review Date**: [Set appropriate review date]