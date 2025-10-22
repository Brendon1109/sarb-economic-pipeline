"""
SARB Economic Pipeline - Full Demo with AI
Complete version including Vertex AI for assessment demonstration
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

# Try to import AI components - graceful fallback if not available
try:
    from google.cloud import aiplatform
    import vertexai
    from vertexai.generative_models import GenerativeModel
    AI_AVAILABLE = True
    logger.info("✅ AI components loaded successfully")
except ImportError as e:
    AI_AVAILABLE = False
    logger.warning(f"⚠️ AI components not available: {e}")
    logger.info("📊 Running in data-only mode (still impressive for demo!)")

class SARBDataPipelineFullDemo:
    """Full demo version with AI capabilities for assessment"""
    
    def __init__(self, project_id='brendon-presentation'):
        self.project_id = project_id
        self.dataset_id = 'sarb_economic_data'
        self.table_id = 'economic_indicators'
        self.region = 'us-central1'
        
        # Initialize GCP clients
        try:
            self.storage_client = storage.Client(project=self.project_id)
            self.bigquery_client = bigquery.Client(project=self.project_id)
            logger.info(f"✅ Connected to GCP project: {self.project_id}")
            
            # Initialize AI if available
            if AI_AVAILABLE:
                try:
                    vertexai.init(project=self.project_id, location=self.region)
                    # Use a more commonly available model
                    self.ai_model = GenerativeModel("gemini-1.5-flash")  # More widely available
                    logger.info("🤖 AI model initialized successfully")
                except Exception as e:
                    logger.warning(f"⚠️ AI initialization failed: {e}")
                    self.ai_model = None
            else:
                self.ai_model = None
                
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
                bigquery.SchemaField("ai_insights", "STRING", mode="NULLABLE"),  # AI-generated insights
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

    def generate_ai_insights(self, indicator_name: str, value: float, category: str) -> str:
        """Generate AI-powered insights for economic indicators"""
        if not self.ai_model:
            return "AI analysis not available"
        
        try:
            prompt = f"""
            As a South African economic analyst, provide a brief insight (2-3 sentences) about this indicator:
            
            Indicator: {indicator_name}
            Current Value: {value}
            Category: {category}
            
            Focus on:
            - What this value means for South Africa's economy
            - Whether this is good/concerning for economic policy
            - Brief context for SARB decision-making
            """
            
            response = self.ai_model.generate_content(prompt)
            insight = response.text.strip()
            logger.info(f"🤖 Generated AI insight for {indicator_name}")
            return insight
            
        except Exception as e:
            logger.warning(f"⚠️ AI insight generation failed: {e}")
            return f"Economic indicator shows {value}% - analysis pending"

    def upload_sample_data_with_ai(self):
        """Upload sample SARB economic indicators with AI insights"""
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
            
            # Generate AI insights for each indicator
            for item in sample_data:
                if self.ai_model:
                    print(f"🤖 Generating AI insight for {item['indicator_name']}...")
                    item['ai_insights'] = self.generate_ai_insights(
                        item['indicator_name'], 
                        item['value'], 
                        item['category']
                    )
                else:
                    item['ai_insights'] = "AI analysis not available - core data processing working"
            
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
            
            ai_status = "with AI insights" if self.ai_model else "without AI (still impressive!)"
            logger.info(f"✅ Uploaded {len(sample_data)} sample records {ai_status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading sample data: {e}")
            return False

    def query_latest_with_ai_insights(self, limit=10):
        """Query latest economic indicators including AI insights"""
        try:
            query = f"""
                SELECT 
                    indicator_name,
                    value,
                    date,
                    category,
                    unit,
                    source,
                    ai_insights
                FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                ORDER BY date DESC, created_at DESC
                LIMIT {limit}
            """
            
            results = self.bigquery_client.query(query).to_dataframe()
            logger.info(f"✅ Retrieved {len(results)} indicators with AI insights")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying data: {e}")
            return None

    def demonstrate_ai_analysis(self):
        """Demonstrate real-time AI analysis capabilities"""
        if not self.ai_model:
            print("⚠️ AI demonstration skipped - Vertex AI not available")
            print("💡 This would normally show Gemini-powered economic analysis")
            return
        
        print("🤖 Demonstrating AI-Powered Economic Analysis...")
        print("=" * 60)
        
        # Real-time analysis
        analysis_prompt = """
        As a senior economic analyst for the South African Reserve Bank, provide a brief economic outlook based on these current indicators:
        
        - GDP Growth: 2.3%
        - Inflation: 5.4% 
        - Prime Rate: 11.75%
        - USD/ZAR: 18.45
        - Unemployment: 32.1%
        
        Provide 3 key insights for monetary policy decisions.
        """
        
        try:
            response = self.ai_model.generate_content(analysis_prompt)
            print("📊 AI Economic Analysis:")
            print(response.text)
            print("=" * 60)
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")

def main():
    """Main function for full demo with AI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SARB Economic Pipeline - Full Demo with AI')
    parser.add_argument('--project-id', default='brendon-presentation', help='GCP Project ID')
    parser.add_argument('--upload-sample-data', action='store_true', help='Upload sample data with AI insights')
    parser.add_argument('--query-data', action='store_true', help='Query latest data with AI insights')
    parser.add_argument('--ai-demo', action='store_true', help='Demonstrate AI analysis capabilities')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    print("🏦 SARB Economic Data Pipeline - Full Demo with AI")
    print("=" * 60)
    print(f"🤖 AI Status: {'✅ Available' if AI_AVAILABLE else '⚠️ Not Available (Demo still works!)'}")
    print("=" * 60)
    
    pipeline = SARBDataPipelineFullDemo(project_id=args.project_id)
    
    # Create dataset and table
    print("📊 Setting up BigQuery infrastructure...")
    pipeline.create_dataset_and_table()
    
    if args.upload_sample_data:
        print("📈 Uploading sample economic indicators with AI insights...")
        success = pipeline.upload_sample_data_with_ai()
        if success:
            print("✅ Sample data with AI insights uploaded successfully!")
        else:
            print("❌ Failed to upload sample data")
            return
    
    if args.query_data or args.upload_sample_data:
        print("🔍 Querying latest economic indicators with AI insights...")
        results = pipeline.query_latest_with_ai_insights()
        if results is not None and not results.empty:
            print("\n📋 Latest Economic Indicators with AI Insights:")
            for _, row in results.iterrows():
                print(f"\n📊 {row['indicator_name']}: {row['value']} {row['unit']}")
                if pd.notna(row['ai_insights']) and row['ai_insights'] != "AI analysis not available":
                    print(f"🤖 AI Insight: {row['ai_insights']}")
        else:
            print("❌ No data found or query failed")
    
    if args.ai_demo:
        pipeline.demonstrate_ai_analysis()
    
    print("\n🎯 Full demo completed!")
    print(f"BigQuery Console: https://console.cloud.google.com/bigquery?project={args.project_id}")
    if AI_AVAILABLE:
        print("🤖 AI-powered insights available for real-time analysis")
    else:
        print("💡 Install AI packages for full capabilities: pip install google-cloud-aiplatform vertexai")

if __name__ == "__main__":
    main()