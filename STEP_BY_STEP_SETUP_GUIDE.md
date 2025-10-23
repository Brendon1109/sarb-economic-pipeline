# 🎯 SARB Pipeline Setup Guide - Complete Walkthrough

## 📋 **Overview**
This guide walks you through setting up the complete SARB Economic Pipeline from scratch to production deployment.

---

## **🔧 Step 1: Initial Setup (5 minutes)**

### **1.1 Verify Google Cloud Configuration**
```powershell
# Check current configuration
gcloud config list

# Expected output should show:
# - account: mapindabrendon@gmail.com
# - project: brendon-presentation  
# - region: us-central1
```

### **1.2 Enable Required APIs**
```powershell
# Enable all necessary GCP APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### **1.3 Verify BigQuery Data**
```powershell
# Check if data exists
python quick_assessment_demo.py

# Expected: 25+ records across 5 indicators
```

---

## **🏗️ Step 2: Infrastructure Setup (10 minutes)**

### **2.1 Create BigQuery Datasets (if not exists)**
```powershell
# Create all required datasets
bq mk --dataset --location=US brendon-presentation:sarb_bronze_raw
bq mk --dataset --location=US brendon-presentation:sarb_silver_staging  
bq mk --dataset --location=US brendon-presentation:sarb_gold_reporting
bq mk --dataset --location=US brendon-presentation:sarb_ai_insights
bq mk --dataset --location=US brendon-presentation:sarb_economic_data
```

### **2.2 Create BigQuery Tables**
```powershell
# Run the infrastructure setup
python src/main.py --setup-infrastructure
```

### **2.3 Upload Sample Data (if needed)**
```powershell
# Upload historical economic data
python src/main.py --upload-sample-data
```

---

## **🐳 Step 3: Containerization Setup (5 minutes)**

### **3.1 Verify Docker Configuration**
```powershell
# Check Dockerfile exists and is configured
type Dockerfile

# Expected: Production-ready configuration with gunicorn
```

### **3.2 Test Local Container Build (Optional)**
```powershell
# If Docker is installed locally
docker build -t sarb-pipeline .
docker run -p 8080:8080 sarb-pipeline
```

### **3.3 Prepare for Cloud Build**
```powershell
# Verify all source files are ready
dir src
dir scripts
dir requirements.txt
```

---

## **☁️ Step 4: Cloud Run Deployment (15 minutes)**

### **4.1 Deploy Using Cloud Build**
```powershell
# Deploy directly from source (preferred method)
gcloud run deploy sarb-economic-pipeline `
    --source . `
    --region us-central1 `
    --project brendon-presentation `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 1 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080
```

**Note**: If you get permission errors, the service account needs additional IAM roles.

### **4.2 Alternative: Manual Build and Deploy**
```powershell
# If direct deployment fails, build separately
gcloud builds submit --tag gcr.io/brendon-presentation/sarb-pipeline

# Then deploy the built image
gcloud run deploy sarb-economic-pipeline `
    --image gcr.io/brendon-presentation/sarb-pipeline `
    --region us-central1 `
    --project brendon-presentation `
    --allow-unauthenticated
```

### **4.3 Verify Deployment**
```powershell
# Get service URL
gcloud run services list --region us-central1

# Test health endpoint
curl "https://YOUR-SERVICE-URL/"
# Expected: {"status": "healthy", "service": "sarb-economic-pipeline"}
```

---

## **⏰ Step 5: Cloud Scheduler Setup (5 minutes)**

### **5.1 Configure Environment Variables**
```powershell
# Set required variables
$env:PROJECT_ID = "brendon-presentation"
$env:REGION = "us-central1"
$env:SERVICE_NAME = "sarb-economic-pipeline"
```

### **5.2 Run Scheduler Setup Script**
```powershell
# Execute the automated setup
./scripts/setup_scheduler.sh
```

### **5.3 Manual Scheduler Creation (if script fails)**
```powershell
# Get your Cloud Run service URL first
$SERVICE_URL = gcloud run services describe sarb-economic-pipeline --region us-central1 --format="value(status.url)"

# Create the scheduler job
gcloud scheduler jobs create http sarb-daily-pipeline `
    --schedule="0 2 * * *" `
    --uri="$SERVICE_URL/run-pipeline" `
    --http-method=POST `
    --location=us-central1 `
    --time-zone="Africa/Johannesburg" `
    --description="Daily SARB economic indicators data pipeline"
```

### **5.4 Test Scheduler Job**
```powershell
# Run a test execution
gcloud scheduler jobs run sarb-daily-pipeline --location=us-central1

# Check execution logs
gcloud logging read "resource.type=cloud_run_revision" --limit=10
```

---

## **🤖 Step 6: AI Integration Setup (3 minutes)**

### **6.1 Configure Gemini API Key**
```powershell
# Set environment variable for AI features
$env:GEMINI_API_KEY = "AIzaSyBn7rHoJ2O4qWBYtKVRdmKSt1DbstVb2_Q"
```

### **6.2 Test AI Integration**
```powershell
# Test AI analysis locally
python src/ai_demo_gemini.py

# Expected: Real-time economic analysis output
```

### **6.3 Update Cloud Run with AI Key (Optional)**
```powershell
# Add environment variable to Cloud Run service
gcloud run services update sarb-economic-pipeline `
    --region us-central1 `
    --set-env-vars GEMINI_API_KEY="AIzaSyBn7rHoJ2O4qWBYtKVRdmKSt1DbstVb2_Q"
```

---

## **📊 Step 7: Dashboard Setup (10 minutes)**

### **7.1 Verify Looker Studio Presentation**
```powershell
# Open the main presentation
start SARB_Comprehensive_Dashboard_Presentation.html
```

### **7.2 Check GitHub Pages Deployment**
```powershell
# Verify embedded reports exist
dir github_pages_deployment
dir *_embeddable.html
```

### **7.3 Generate Latest Reports**
```powershell
# Create fresh analytical reports
python src/comprehensive_report_generator.py
```

---

## **🎛️ Step 8: Orchestration Setup (Optional - 15 minutes)**

### **8.1 Basic Orchestration Demo**
```powershell
# Test orchestration capabilities
python orchestration/demo_orchestration.py
```

### **8.2 Advanced: Cloud Composer Setup**
```powershell
# For full production orchestration (advanced)
# Note: This requires additional setup and costs

# Create Composer environment
gcloud composer environments create sarb-pipeline `
    --location us-central1 `
    --node-count 3 `
    --machine-type n1-standard-1

# Upload DAG
gcloud composer environments storage dags import `
    --environment sarb-pipeline `
    --location us-central1 `
    --source orchestration/sarb_pipeline_dag.py
```

---

## **✅ Step 9: Verification & Testing (10 minutes)**

### **9.1 End-to-End Test**
```powershell
# Run complete verification
python quick_assessment_demo.py

# Expected: All components showing ✅
```

### **9.2 Test Pipeline Execution**
```powershell
# Trigger manual pipeline execution
curl -X POST "https://YOUR-SERVICE-URL/run-pipeline"

# Check BigQuery for new data
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM brendon-presentation.sarb_economic_data.economic_indicators"
```

### **9.3 Monitor Logs**
```powershell
# Check Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=20

# Check Scheduler logs  
gcloud logging read "resource.type=cloud_scheduler_job" --limit=10
```

---

## **🎯 Step 10: Assessment Preparation (5 minutes)**

### **10.1 Prepare Demo Environment**
```powershell
# Ensure all files are ready
dir ASSESSMENT_*.md
dir quick_assessment_demo.py
dir SARB_Comprehensive_Dashboard_Presentation.html
```

### **10.2 Practice Demo Flow**
```powershell
# Run through the assessment demo
python quick_assessment_demo.py

# Open dashboard presentation
start SARB_Comprehensive_Dashboard_Presentation.html

# Test AI capabilities
python src/ai_demo_gemini.py
```

### **10.3 Final Status Check**
```powershell
# Verify all services are running
gcloud run services list
gcloud scheduler jobs list --location=us-central1
bq ls brendon-presentation:
```

---

## **🚨 Troubleshooting Common Issues**

### **Issue 1: Permission Denied During Deployment**
```powershell
# Grant necessary permissions
gcloud projects add-iam-policy-binding brendon-presentation `
    --member="user:mapindabrendon@gmail.com" `
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding brendon-presentation `
    --member="serviceAccount:957852305111-compute@developer.gserviceaccount.com" `
    --role="roles/storage.admin"
```

### **Issue 2: BigQuery Access Denied**
```powershell
# Verify BigQuery permissions
gcloud projects add-iam-policy-binding brendon-presentation `
    --member="user:mapindabrendon@gmail.com" `
    --role="roles/bigquery.admin"
```

### **Issue 3: Cloud Run Service Won't Start**
```powershell
# Check service logs
gcloud run services logs read sarb-economic-pipeline --region us-central1

# Verify environment variables
gcloud run services describe sarb-economic-pipeline --region us-central1
```

### **Issue 4: Scheduler Job Fails**
```powershell
# Check if service URL is correct
gcloud run services describe sarb-economic-pipeline --region us-central1 --format="value(status.url)"

# Update scheduler job with correct URL
gcloud scheduler jobs update http sarb-daily-pipeline `
    --location=us-central1 `
    --uri="https://NEW-SERVICE-URL/run-pipeline"
```

---

## **🎉 Success Criteria**

Your pipeline is successfully set up when:

✅ **BigQuery**: Contains economic indicators data  
✅ **Cloud Run**: Service responds to health checks  
✅ **Scheduler**: Job executes without errors  
✅ **AI Integration**: Provides economic analysis  
✅ **Dashboards**: Display live data  
✅ **Demo Script**: Runs successfully  

---

## **📊 Total Setup Time: ~75 minutes**

- **Basic Setup**: 30 minutes
- **Advanced Features**: 45 minutes  
- **Testing & Verification**: 15 minutes (included above)

---

## **🎯 Next Steps After Setup**

1. **Practice your assessment presentation**
2. **Familiarize yourself with the demo flow**
3. **Review technical architecture talking points**
4. **Prepare for Q&A about design decisions**

**You're ready for assessment success!** 🚀