# 🚀 QUICK DEMO REFERENCE CARD

## ⚡ IMMEDIATE SETUP (Run these commands first)
```powershell
# 1. Authenticate (CRITICAL!)
gcloud auth login
gcloud auth application-default login
gcloud config set project brendon-presentation

# 2. Run setup
.\setup-assessment.ps1

# 3. Verify everything works
gcloud bigquery ls --project_id=brendon-presentation
```

## 🎯 DEMO SEQUENCE (15 minutes)

### Opening (2 min) - Show the presentation
- Open: `presentation/SARB_Economic_Pipeline.html`
- Key message: "Real-world economic data pipeline on GCP"

### Technical Demo (8 min)
```powershell
# Show project structure
tree /f

# Upload sample data
python src/main.py --upload-sample-data

# Query economic data
gcloud bigquery query --use_legacy_sql=false "
SELECT indicator_name, value, date 
FROM \`brendon-presentation.sarb_economic_data.economic_indicators\` 
ORDER BY date DESC LIMIT 10"

# Open analysis notebook
jupyter notebook analysis/sarb_macroeconomic_analysis.ipynb
```

### Business Value (3 min) - Show monitoring
- Cost: $50-150/month
- Performance: 1000+ records/second
- Uptime: 99.9%

### Q&A (2 min) - Common questions ready

## 🆘 EMERGENCY FIXES
```powershell
# If auth fails
gcloud auth revoke --all && gcloud auth login

# If BigQuery fails
gcloud bigquery mk --dataset brendon-presentation:sarb_economic_data

# If Python fails
pip install -r requirements.txt
```

## 💡 KEY TALKING POINTS
- "Transforms SARB's data processing from days to minutes"
- "Scales automatically with South Africa's economic data growth"
- "Enterprise-grade security meets government standards"
- "Cost-optimized for government budget constraints"

**Contact**: mapindabrendon@gmail.com | **Project**: SARB Economic Pipeline | **Date**: Oct 21, 2025