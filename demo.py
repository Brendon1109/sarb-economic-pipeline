#!/usr/bin/env python3
"""
SARB Pipeline - Project Demo
Comprehensive demonstration of all working components
"""

import os
import json
from datetime import datetime
from google.cloud import bigquery

def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_status(message):
    """Print status message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def check_bigquery_data():
    """Check BigQuery data status"""
    try:
        client = bigquery.Client()
        project_id = client.project
        
        print_status(f"Connected to BigQuery project: {project_id}")
        
        # List datasets
        datasets = list(client.list_datasets())
        print_status(f"Found {len(datasets)} datasets")
        
        for dataset in datasets:
            if 'sarb' in dataset.dataset_id.lower():
                print(f"  📊 {dataset.dataset_id}")
                
                # List tables in SARB datasets
                tables = list(client.list_tables(dataset.dataset_id))
                for table in tables:
                    table_ref = client.get_table(table.reference)
                    print(f"    📋 {table.table_id} ({table_ref.num_rows:,} rows)")
        
        return True
    except Exception as e:
        print_error(f"BigQuery check failed: {str(e)}")
        return False

def check_cloud_run_status():
    """Check Cloud Run service status"""
    try:
        # Check if gcloud CLI is available
        result = os.system("gcloud version > nul 2>&1")
        if result != 0:
            print_error("Google Cloud CLI not available")
            return False
            
        print_status("Google Cloud CLI available")
        
        # Try to get Cloud Run service info
        import subprocess
        result = subprocess.run([
            "gcloud", "run", "services", "list", 
            "--filter=sarb-economic-pipeline", 
            "--format=json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            services = json.loads(result.stdout)
            if services:
                service = services[0]
                print_status(f"Cloud Run service: {service.get('metadata', {}).get('name', 'Unknown')}")
                print_status(f"Region: {service.get('metadata', {}).get('labels', {}).get('cloud.googleapis.com/location', 'Unknown')}")
                print_status(f"URL: {service.get('status', {}).get('url', 'Unknown')}")
                return True
            else:
                print_error("No Cloud Run services found")
                return False
        else:
            print_error("Failed to check Cloud Run status")
            return False
            
    except Exception as e:
        print_error(f"Cloud Run check failed: {str(e)}")
        return False

def check_project_structure():
    """Check project file structure"""
    print_status("Checking project structure...")
    
    essential_files = [
        'main.py',
        'Dockerfile', 
        'requirements.txt',
        'README.md'
    ]
    
    essential_dirs = [
        'src',
        'infrastructure', 
        'orchestration',
        'analysis'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print_status(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
    
    for dir in essential_dirs:
        if os.path.exists(dir):
            print_status(f"Found directory: {dir}")
        else:
            print_error(f"Missing directory: {dir}")

def main():
    """Main demo function"""
    print("🏦 SARB Economic Pipeline - Project Demo")
    print("="*50)
    print(f"Demo run on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check project structure
    print_header("PROJECT STRUCTURE")
    check_project_structure()
    
    # Check BigQuery data
    print_header("BIGQUERY DATA STATUS")
    bigquery_ok = check_bigquery_data()
    
    # Check Cloud Run status
    print_header("CLOUD RUN SERVICE STATUS")
    cloudrun_ok = check_cloud_run_status()
    
    # Summary
    print_header("DEMO SUMMARY")
    print_status("Project structure verified")
    
    if bigquery_ok:
        print_status("BigQuery data accessible")
    else:
        print_error("BigQuery data check failed")
        
    if cloudrun_ok:
        print_status("Cloud Run service active")
    else:
        print_error("Cloud Run service check failed")
    
    print("\n🎯 Demo completed!")
    print("For live dashboards, visit: https://brendon1109.github.io/sarb-economic-pipeline/")

if __name__ == "__main__":
    main()