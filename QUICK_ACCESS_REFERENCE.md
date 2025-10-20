# Quick Access Reference Card

## Repository Access (GitHub)

### 1. Repository URL
```
https://github.com/YOUR_USERNAME/sarb-economic-pipeline
```

### 2. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/sarb-economic-pipeline.git
cd sarb-economic-pipeline
```

### 3. Add Collaborators
- Go to: Repository → Settings → Manage access
- Click: "Invite a collaborator"
- Enter: GitHub username or email
- Select permission level

---

## GCP Project Access

### Quick Commands

#### Set Environment Variables
```bash
export PROJECT_ID="your-actual-project-id"
export USER_EMAIL="user@company.com"
export ROLE_TYPE="analyst"  # analyst|engineer|devops|manager|viewer
```

#### Grant Access (Bash)
```bash
chmod +x scripts/grant_access.sh
./scripts/grant_access.sh --project-id $PROJECT_ID --user-email $USER_EMAIL --role $ROLE_TYPE
```

#### Grant Access (PowerShell)
```powershell
.\scripts\grant_access.ps1 -ProjectId $PROJECT_ID -UserEmail $USER_EMAIL -RoleType $ROLE_TYPE
```

### Role Permissions Matrix

| Role | BigQuery | Storage | Cloud Run | IAM Admin | Monitoring |
|------|----------|---------|-----------|-----------|------------|
| **Analyst** | Read Only | - | - | - | - |
| **Engineer** | Read/Write | Admin | Developer | - | Viewer |
| **DevOps** | Full | Full | Admin | Admin | Full |
| **Manager** | Read Only | - | - | - | Viewer |
| **Viewer** | - | - | - | - | - |

### Manual IAM Commands

#### Data Analyst
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/bigquery.dataViewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/bigquery.jobUser"
```

#### Data Engineer
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/storage.objectAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/run.developer"
```

#### DevOps Engineer
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/editor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$USER_EMAIL" --role="roles/iam.serviceAccountAdmin"
```

### Verification Commands

#### Check User Permissions
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:user:$USER_EMAIL"
```

#### Test BigQuery Access
```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`$PROJECT_ID.sarb_economic_data.silver_economic_indicators\` LIMIT 1"
```

#### List All Project Resources
```bash
gcloud projects describe $PROJECT_ID
gcloud services list --enabled --project=$PROJECT_ID
```

---

## Common Access Scenarios

### New Team Member Onboarding
1. **GitHub**: Add as collaborator with Write access
2. **GCP**: Grant appropriate role (analyst/engineer/devops)
3. **Send**: Repository URL and GCP project ID
4. **Guide**: Point to README.md and ACCESS_MANAGEMENT.md

### External Consultant Access
1. **GitHub**: Add as collaborator with Read access
2. **GCP**: Grant Viewer role initially
3. **Time-limited**: Set calendar reminder to remove access
4. **Audit**: Document access in project records

### Temporary Access for Analysis
1. **GitHub**: No access needed for data-only work
2. **GCP**: Grant BigQuery dataViewer + jobUser roles
3. **Resources**: Share direct BigQuery dataset links
4. **Duration**: Set automatic expiration if possible

---

## Security Checklist

- [ ] Use principle of least privilege
- [ ] Document all access grants
- [ ] Set up access review schedule
- [ ] Enable audit logging
- [ ] Use groups instead of individual users where possible
- [ ] Rotate service account keys regularly
- [ ] Monitor unusual access patterns
- [ ] Remove access when team members leave

---

## Support Contacts

**Repository Issues**: Create GitHub issue or contact repository maintainer
**GCP Access Issues**: Contact project administrator or cloud team
**Emergency Access**: [Emergency contact information]