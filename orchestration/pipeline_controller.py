#!/usr/bin/env python3
"""
SARB Pipeline Control Interface
Provides easy controls for pausing/resuming pipeline components
"""

import os
import json
from datetime import datetime
from google.cloud import bigquery
from airflow import settings
from airflow.models import Variable, DagRun
from airflow.api.client.local_client import Client

class SARBPipelineController:
    """Control interface for SARB economic pipeline orchestration"""
    
    def __init__(self):
        self.airflow_client = Client(None, None)
        self.bigquery_client = bigquery.Client(project='brendon-presentation')
    
    def pause_pipeline(self, reason="Manual pause"):
        """Pause the entire pipeline"""
        try:
            # Set pipeline control variable
            Variable.set("sarb_pipeline_enabled", False, serialize_json=True)
            
            # Pause the DAG
            self.airflow_client.pause('sarb_economic_pipeline')
            
            # Log the pause
            pause_info = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "paused_by": "pipeline_controller",
                "status": "paused"
            }
            
            print(f"🛑 Pipeline paused: {pause_info}")
            return pause_info
            
        except Exception as e:
            print(f"❌ Error pausing pipeline: {e}")
            return {"error": str(e)}
    
    def resume_pipeline(self, reason="Manual resume"):
        """Resume the entire pipeline"""
        try:
            # Enable pipeline control variable
            Variable.set("sarb_pipeline_enabled", True, serialize_json=True)
            
            # Unpause the DAG
            self.airflow_client.unpause('sarb_economic_pipeline')
            
            # Log the resume
            resume_info = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "resumed_by": "pipeline_controller",
                "status": "active"
            }
            
            print(f"▶️ Pipeline resumed: {resume_info}")
            return resume_info
            
        except Exception as e:
            print(f"❌ Error resuming pipeline: {e}")
            return {"error": str(e)}
    
    def pause_ai_analysis(self):
        """Pause only AI analysis component"""
        Variable.set("sarb_ai_enabled", False, serialize_json=True)
        print("🤖 AI analysis paused")
        return {"component": "ai_analysis", "status": "paused"}
    
    def resume_ai_analysis(self):
        """Resume AI analysis component"""
        Variable.set("sarb_ai_enabled", True, serialize_json=True)
        print("🤖 AI analysis resumed")
        return {"component": "ai_analysis", "status": "active"}
    
    def pause_dashboard_updates(self):
        """Pause dashboard update component"""
        Variable.set("sarb_dashboard_enabled", False, serialize_json=True)
        print("📊 Dashboard updates paused")
        return {"component": "dashboard_updates", "status": "paused"}
    
    def resume_dashboard_updates(self):
        """Resume dashboard update component"""
        Variable.set("sarb_dashboard_enabled", True, serialize_json=True)
        print("📊 Dashboard updates resumed")
        return {"component": "dashboard_updates", "status": "active"}
    
    def get_pipeline_status(self):
        """Get current status of all pipeline components"""
        try:
            status = {
                "pipeline_enabled": Variable.get("sarb_pipeline_enabled", default_var=True, deserialize_json=True),
                "ai_enabled": Variable.get("sarb_ai_enabled", default_var=True, deserialize_json=True),
                "dashboard_enabled": Variable.get("sarb_dashboard_enabled", default_var=True, deserialize_json=True),
                "last_run": self.get_last_run_info(),
                "data_freshness": self.check_data_freshness(),
                "health_status": self.get_health_status()
            }
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_last_run_info(self):
        """Get information about the last pipeline run"""
        try:
            dag_runs = DagRun.find(dag_id='sarb_economic_pipeline', limit=1)
            if dag_runs:
                last_run = dag_runs[0]
                return {
                    "execution_date": last_run.execution_date.isoformat(),
                    "state": last_run.state,
                    "start_date": last_run.start_date.isoformat() if last_run.start_date else None,
                    "end_date": last_run.end_date.isoformat() if last_run.end_date else None
                }
            return {"status": "no_runs_found"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_data_freshness(self):
        """Check how fresh the data is"""
        try:
            query = """
            SELECT 
                MAX(date) as latest_date,
                COUNT(*) as total_records
            FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
            """
            
            result = list(self.bigquery_client.query(query).result())[0]
            days_old = (datetime.now().date() - result.latest_date).days
            
            return {
                "latest_data_date": str(result.latest_date),
                "days_old": days_old,
                "total_records": result.total_records,
                "freshness_status": "fresh" if days_old < 7 else "stale"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_health_status(self):
        """Get overall pipeline health"""
        try:
            # Check BigQuery datasets
            datasets = ['sarb_bronze_raw', 'sarb_silver_staging', 'sarb_gold_reporting', 'sarb_ai_insights']
            dataset_health = {}
            
            for dataset_id in datasets:
                try:
                    dataset = self.bigquery_client.get_dataset(dataset_id)
                    tables = list(self.bigquery_client.list_tables(dataset))
                    dataset_health[dataset_id] = {
                        "exists": True,
                        "table_count": len(tables)
                    }
                except Exception:
                    dataset_health[dataset_id] = {"exists": False}
            
            overall_health = all(ds["exists"] for ds in dataset_health.values())
            
            return {
                "overall_healthy": overall_health,
                "dataset_health": dataset_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def emergency_stop(self):
        """Emergency stop all pipeline operations"""
        print("🚨 EMERGENCY STOP INITIATED")
        
        results = {
            "pipeline_pause": self.pause_pipeline("Emergency stop"),
            "ai_pause": self.pause_ai_analysis(),
            "dashboard_pause": self.pause_dashboard_updates(),
            "timestamp": datetime.now().isoformat()
        }
        
        print("🛑 All pipeline components stopped")
        return results
    
    def full_restart(self):
        """Restart all pipeline components"""
        print("🔄 FULL PIPELINE RESTART INITIATED")
        
        results = {
            "pipeline_resume": self.resume_pipeline("Full restart"),
            "ai_resume": self.resume_ai_analysis(),
            "dashboard_resume": self.resume_dashboard_updates(),
            "timestamp": datetime.now().isoformat()
        }
        
        print("▶️ All pipeline components restarted")
        return results

def main():
    """Command-line interface for pipeline control"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SARB Pipeline Control Interface')
    parser.add_argument('action', choices=[
        'status', 'pause', 'resume', 'pause-ai', 'resume-ai', 
        'pause-dashboard', 'resume-dashboard', 'emergency-stop', 'restart'
    ], help='Action to perform')
    parser.add_argument('--reason', default='Manual control', help='Reason for action')
    
    args = parser.parse_args()
    
    controller = SARBPipelineController()
    
    if args.action == 'status':
        status = controller.get_pipeline_status()
        print(json.dumps(status, indent=2))
        
    elif args.action == 'pause':
        result = controller.pause_pipeline(args.reason)
        print(json.dumps(result, indent=2))
        
    elif args.action == 'resume':
        result = controller.resume_pipeline(args.reason)
        print(json.dumps(result, indent=2))
        
    elif args.action == 'pause-ai':
        result = controller.pause_ai_analysis()
        print(json.dumps(result, indent=2))
        
    elif args.action == 'resume-ai':
        result = controller.resume_ai_analysis()
        print(json.dumps(result, indent=2))
        
    elif args.action == 'pause-dashboard':
        result = controller.pause_dashboard_updates()
        print(json.dumps(result, indent=2))
        
    elif args.action == 'resume-dashboard':
        result = controller.resume_dashboard_updates()
        print(json.dumps(result, indent=2))
        
    elif args.action == 'emergency-stop':
        result = controller.emergency_stop()
        print(json.dumps(result, indent=2))
        
    elif args.action == 'restart':
        result = controller.full_restart()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()