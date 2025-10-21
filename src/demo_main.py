"""
SARB Economic Pipeline - Demo Version
Simplified for assessment demonstration
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SARBDataPipelineDemo:
    """Demo version of SARB Economic Data Pipeline for assessment"""
    
    def __init__(self, project_id='brendon-presentation'):
        self.project_id = project_id
        self.dataset_id = 'sarb_economic_data'
        self.table_id = 'economic_indicators'
        
        # Initialize GCP clients
        try:
            self.storage_client = storage.Client(project=self.project_id)
            self.bigquery_client = bigquery.Client(project=self.project_id)
            logger.info(f"✅ Connected to GCP project: {self.project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to GCP: {e}")
            raise

    def create_dataset_and_table(self):
        """Create BigQuery dataset and table for demo"""
        try:
            # Create dataset
            dataset_ref = self.bigquery_client.dataset(self.dataset_id)
            try:
                dataset = self.bigquery_client.get_dataset(dataset_ref)
                logger.info(f"✅ Dataset {self.dataset_id} already exists")
            except:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = self.bigquery_client.create_dataset(dataset)
                logger.info(f"✅ Created dataset {self.dataset_id}")
            
            # Create table schema
            schema = [
                bigquery.SchemaField("indicator_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("value", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            table_ref = dataset_ref.table(self.table_id)
            try:
                table = self.bigquery_client.get_table(table_ref)
                logger.info(f"✅ Table {self.table_id} already exists")
            except:
                table = bigquery.Table(table_ref, schema=schema)
                table = self.bigquery_client.create_table(table)
                logger.info(f"✅ Created table {self.table_id}")
                
        except Exception as e:
            logger.error(f"❌ Error creating dataset/table: {e}")
            raise

    def upload_sample_data(self):
        """Upload sample SARB economic indicators for demo"""
        try:
            # Create sample economic data
            sample_data = [
                {
                    "indicator_name": "GDP_Growth_Rate",
                    "value": 2.3,
                    "date": "2024-09-30",
                    "category": "Economic Growth",
                    "unit": "Percentage",
                    "source": "SARB",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "indicator_name": "Inflation_Rate",
                    "value": 5.4,
                    "date": "2024-09-30",
                    "category": "Price Stability",
                    "unit": "Percentage",
                    "source": "SARB",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "indicator_name": "Prime_Interest_Rate",
                    "value": 11.75,
                    "date": "2024-09-30",
                    "category": "Monetary Policy",
                    "unit": "Percentage",
                    "source": "SARB",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "indicator_name": "USD_ZAR_Exchange_Rate",
                    "value": 18.45,
                    "date": "2024-10-21",
                    "category": "Exchange Rates",
                    "unit": "ZAR per USD",
                    "source": "SARB",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "indicator_name": "Unemployment_Rate",
                    "value": 32.1,
                    "date": "2024-06-30",
                    "category": "Employment",
                    "unit": "Percentage",
                    "source": "SARB/StatsSA",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            # Convert to DataFrame
            df = pd.DataFrame(sample_data)
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Upload to BigQuery
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )
            
            job = self.bigquery_client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()  # Wait for job to complete
            
            logger.info(f"✅ Uploaded {len(sample_data)} sample records to BigQuery")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading sample data: {e}")
            return False

    def query_latest_indicators(self, limit=10):
        """Query latest economic indicators for demo"""
        try:
            query = f"""
                SELECT 
                    indicator_name,
                    value,
                    date,
                    category,
                    unit,
                    source
                FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                ORDER BY date DESC, created_at DESC
                LIMIT {limit}
            """
            
            results = self.bigquery_client.query(query).to_dataframe()
            logger.info(f"✅ Retrieved {len(results)} indicators")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying data: {e}")
            return None

def main():
    """Main function for demo"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SARB Economic Pipeline Demo')
    parser.add_argument('--project-id', default='brendon-presentation', help='GCP Project ID')
    parser.add_argument('--upload-sample-data', action='store_true', help='Upload sample data')
    parser.add_argument('--query-data', action='store_true', help='Query latest data')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    print("🏦 SARB Economic Data Pipeline - Demo Version")
    print("=" * 50)
    
    pipeline = SARBDataPipelineDemo(project_id=args.project_id)
    
    # Create dataset and table
    print("📊 Setting up BigQuery infrastructure...")
    pipeline.create_dataset_and_table()
    
    if args.upload_sample_data:
        print("📈 Uploading sample economic indicators...")
        success = pipeline.upload_sample_data()
        if success:
            print("✅ Sample data uploaded successfully!")
        else:
            print("❌ Failed to upload sample data")
            return
    
    if args.query_data or args.upload_sample_data:
        print("🔍 Querying latest economic indicators...")
        results = pipeline.query_latest_indicators()
        if results is not None and not results.empty:
            print("\n📋 Latest Economic Indicators:")
            print(results.to_string(index=False))
        else:
            print("❌ No data found or query failed")
    
    print("\n🎯 Demo completed successfully!")
    print(f"BigQuery Console: https://console.cloud.google.com/bigquery?project={args.project_id}")

if __name__ == "__main__":
    main()