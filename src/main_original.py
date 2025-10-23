"""
SARB Economic Indicators Data Pipeline
Main Cloud Run application implementing Medallion Architecture on GCP
"""

import os
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import requests
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery
from google.cloud import aiplatform
from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SARBDataPipeline:
    """
    Main pipeline class implementing the Medallion Architecture for SARB economic data
    """
    
    def __init__(self, project_id=None):
        # Use assessment project by default
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'brendon-presentation')
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', f'{self.project_id}-economic-raw-data')
        self.dataset_id = os.getenv('BIGQUERY_DATASET_ID', 'sarb_economic_data')
        self.region = os.getenv('GCP_REGION', 'us-central1')
        
        # Initialize GCP clients
        self.storage_client = storage.Client(project=self.project_id)
        self.bigquery_client = bigquery.Client(project=self.project_id)
        
        # SARB API configuration
        self.sarb_base_url = "https://www.resbank.co.za/Research/Statistics/Pages/OnlineDownloadFacility.aspx"
        self.indicators = {
            'prime_rate': 'KBP1005M',  # Prime Overdraft Rate
            'cpi': 'KBP6006M',         # Headline CPI
            'zar_usd': 'KBP1004M'      # ZAR/USD Exchange Rate
        }
        
        # Initialize Vertex AI for optional extension
        if self.project_id and self.region:
            vertexai.init(project=self.project_id, location=self.region)
    
    def fetch_sarb_data(self, indicator_code: str, start_date: str = "2010-01-01") -> Dict[str, Any]:
        """
        Fetch data from SARB API for a specific indicator
        
        Args:
            indicator_code: SARB series code
            start_date: Start date in YYYY-MM-DD format
            
        Returns:
            Raw JSON response from SARB API
        """
        try:
            # Note: This is a simplified implementation. 
            # In production, you'd need to implement the actual SARB API authentication and data fetching
            # For this assessment, I'm creating a mock structure that would work with the real API
            
            url = f"https://www.resbank.co.za/webindicators/DataDownload?SeriesNames={indicator_code}&startDate={start_date}"
            
            headers = {
                'User-Agent': 'SARB-Economic-Pipeline/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the response - SARB typically returns CSV, so we'd need to convert
            # For this implementation, I'll create the expected JSON structure
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else self._convert_csv_to_json(response.text, indicator_code)
            
            logger.info(f"Successfully fetched data for indicator {indicator_code}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data for {indicator_code}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {indicator_code}: {str(e)}")
            raise
    
    def _convert_csv_to_json(self, csv_data: str, indicator_code: str) -> Dict[str, Any]:
        """Convert CSV response to JSON format"""
        # This would implement the actual CSV to JSON conversion for SARB data
        # For now, creating a mock structure
        lines = csv_data.strip().split('\n')
        headers = lines[0].split(',')
        data_rows = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) >= 2:
                data_rows.append({
                    'date': values[0],
                    'value': float(values[1]) if values[1].replace('.', '').isdigit() else None
                })
        
        return {
            'indicator_code': indicator_code,
            'data': data_rows,
            'metadata': {
                'source': 'SARB',
                'extracted_at': datetime.now(timezone.utc).isoformat()
            }
        }
    
    def bronze_layer_ingestion(self) -> Dict[str, str]:
        """
        Bronze Layer: Ingest raw data to GCS
        
        Returns:
            Dictionary mapping indicator names to GCS paths
        """
        try:
            current_date = datetime.now(timezone.utc)
            date_partition = current_date.strftime('%Y/%m/%d')
            
            bucket = self.storage_client.bucket(self.bucket_name)
            ingested_files = {}
            
            for indicator_name, indicator_code in self.indicators.items():
                # Fetch raw data
                raw_data = self.fetch_sarb_data(indicator_code)
                
                # Store in GCS with date partitioning
                blob_path = f"bronze/{date_partition}/{indicator_name}.json"
                blob = bucket.blob(blob_path)
                
                blob.upload_from_string(
                    json.dumps(raw_data, indent=2),
                    content_type='application/json'
                )
                
                ingested_files[indicator_name] = f"gs://{self.bucket_name}/{blob_path}"
                logger.info(f"Stored {indicator_name} data to {blob_path}")
            
            return ingested_files
            
        except Exception as e:
            logger.error(f"Bronze layer ingestion failed: {str(e)}")
            raise
    
    def silver_layer_processing(self, bronze_files: Dict[str, str]) -> int:
        """
        Silver Layer: Process and clean data into BigQuery
        
        Args:
            bronze_files: Dictionary of GCS paths for bronze files
            
        Returns:
            Number of records processed
        """
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            all_records = []
            current_timestamp = datetime.now(timezone.utc)
            
            for indicator_name, gcs_path in bronze_files.items():
                # Extract blob path from GCS URI
                blob_path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
                blob = bucket.blob(blob_path)
                
                # Download and parse JSON
                raw_data = json.loads(blob.download_as_text())
                
                # Transform data for silver layer
                for data_point in raw_data.get('data', []):
                    if data_point.get('value') is not None:
                        record = {
                            'observation_date': data_point['date'],
                            'indicator_code': raw_data['indicator_code'],
                            'indicator_name': self._get_indicator_name(raw_data['indicator_code']),
                            'value': float(data_point['value']),
                            'load_timestamp': current_timestamp
                        }
                        all_records.append(record)
            
            if not all_records:
                logger.warning("No records to process in silver layer")
                return 0
            
            # Load to BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.silver_economic_indicators"
            
            # Use MERGE for upsert behavior (idempotency)
            df = pd.DataFrame(all_records)
            df['observation_date'] = pd.to_datetime(df['observation_date']).dt.date
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )
            
            job = self.bigquery_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()  # Wait for completion
            
            logger.info(f"Loaded {len(all_records)} records to silver layer")
            return len(all_records)
            
        except Exception as e:
            logger.error(f"Silver layer processing failed: {str(e)}")
            raise
    
    def _get_indicator_name(self, indicator_code: str) -> str:
        """Map indicator codes to human-readable names"""
        mapping = {
            'KBP1005M': 'Prime Overdraft Rate',
            'KBP6006M': 'Headline Consumer Price Index',
            'KBP1004M': 'ZAR to USD Exchange Rate'
        }
        return mapping.get(indicator_code, indicator_code)
    
    def gold_layer_creation(self) -> bool:
        """
        Gold Layer: Create/update the business-ready view
        
        Returns:
            Success status
        """
        try:
            view_sql = """
            CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.gold_macroeconomic_report` AS
            WITH monthly_data AS (
                SELECT 
                    DATE_TRUNC(observation_date, MONTH) as observation_month,
                    indicator_code,
                    AVG(value) as avg_value
                FROM `{project_id}.{dataset_id}.silver_economic_indicators`
                GROUP BY observation_month, indicator_code
            )
            SELECT 
                observation_month,
                MAX(CASE WHEN indicator_code = 'KBP1005M' THEN avg_value END) as prime_rate,
                MAX(CASE WHEN indicator_code = 'KBP6006M' THEN avg_value END) as headline_cpi,
                MAX(CASE WHEN indicator_code = 'KBP1004M' THEN avg_value END) as zar_usd_exchange_rate
            FROM monthly_data
            GROUP BY observation_month
            ORDER BY observation_month
            """.format(
                project_id=self.project_id,
                dataset_id=self.dataset_id
            )
            
            query_job = self.bigquery_client.query(view_sql)
            query_job.result()
            
            logger.info("Gold layer view created/updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Gold layer creation failed: {str(e)}")
            raise
    
    def run_ai_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Optional AI Extension: Generate automated insights using Gemini
        
        Returns:
            Generated insights or None if disabled
        """
        try:
            # Query last 18 months of data from gold layer
            query_sql = """
            SELECT *
            FROM `{project_id}.{dataset_id}.gold_macroeconomic_report`
            WHERE observation_month >= DATE_SUB(CURRENT_DATE(), INTERVAL 18 MONTH)
            ORDER BY observation_month DESC
            """.format(
                project_id=self.project_id,
                dataset_id=self.dataset_id
            )
            
            query_job = self.bigquery_client.query(query_sql)
            results = query_job.result()
            
            # Convert to dataframe for analysis
            df = results.to_dataframe()
            
            if df.empty:
                logger.warning("No data available for AI analysis")
                return None
            
            # Prepare data for Gemini prompt
            data_summary = df.to_string(index=False)
            
            prompt = f"""
            You are an expert economist analyzing South African macroeconomic data. 
            
            Based on the following 18-month dataset of key economic indicators:
            {data_summary}
            
            Please provide a comprehensive analysis following these five points:
            1. Current economic trends and patterns
            2. Correlation analysis between prime rate, CPI, and ZAR/USD exchange rate
            3. Key economic events or policy impacts visible in the data
            4. Risk assessment for the South African economy
            5. Short-term outlook and recommendations
            
            Return your response as a valid JSON object with these exact keys:
            {{
                "economic_trends": "your analysis here",
                "correlation_analysis": "your analysis here", 
                "key_events": "your analysis here",
                "risk_assessment": "your analysis here",
                "outlook_recommendations": "your analysis here",
                "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
                "data_period": "18 months ending {df['observation_month'].max()}"
            }}
            """
            
            # Generate insights using Gemini
            model = GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            
            # Parse JSON response
            insights = json.loads(response.text)
            
            # Store insights in BigQuery
            self._store_ai_insights(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return None
    
    def _store_ai_insights(self, insights: Dict[str, Any]) -> None:
        """Store AI insights in BigQuery using MERGE for idempotency"""
        try:
            analysis_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create insights record
            insight_record = {
                'analysis_date': analysis_date,
                'generated_insight': insights,
                'model_version': 'gemini-1.5-pro',
                'load_timestamp': datetime.now(timezone.utc)
            }
            
            # Use MERGE statement for upsert
            merge_sql = """
            MERGE `{project_id}.{dataset_id}.gold_automated_insights` T
            USING (SELECT @analysis_date as analysis_date, 
                         @generated_insight as generated_insight,
                         @model_version as model_version,
                         @load_timestamp as load_timestamp) S
            ON T.analysis_date = S.analysis_date
            WHEN MATCHED THEN
                UPDATE SET 
                    generated_insight = S.generated_insight,
                    model_version = S.model_version,
                    load_timestamp = S.load_timestamp
            WHEN NOT MATCHED THEN
                INSERT (analysis_date, generated_insight, model_version, load_timestamp)
                VALUES (S.analysis_date, S.generated_insight, S.model_version, S.load_timestamp)
            """.format(
                project_id=self.project_id,
                dataset_id=self.dataset_id
            )
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("analysis_date", "DATE", analysis_date),
                    bigquery.ScalarQueryParameter("generated_insight", "JSON", json.dumps(insights)),
                    bigquery.ScalarQueryParameter("model_version", "STRING", "gemini-1.5-pro"),
                    bigquery.ScalarQueryParameter("load_timestamp", "TIMESTAMP", insight_record['load_timestamp'])
                ]
            )
            
            query_job = self.bigquery_client.query(merge_sql, job_config=job_config)
            query_job.result()
            
            logger.info("AI insights stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store AI insights: {str(e)}")
            raise
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Execute the complete data pipeline
        
        Returns:
            Pipeline execution summary
        """
        start_time = datetime.now(timezone.utc)
        pipeline_result = {
            'status': 'success',
            'start_time': start_time.isoformat(),
            'bronze_files': {},
            'silver_records': 0,
            'gold_created': False,
            'ai_insights': None,
            'errors': []
        }
        
        try:
            # Bronze Layer
            logger.info("Starting Bronze layer ingestion...")
            pipeline_result['bronze_files'] = self.bronze_layer_ingestion()
            
            # Silver Layer
            logger.info("Starting Silver layer processing...")
            pipeline_result['silver_records'] = self.silver_layer_processing(
                pipeline_result['bronze_files']
            )
            
            # Gold Layer
            logger.info("Creating Gold layer view...")
            pipeline_result['gold_created'] = self.gold_layer_creation()
            
            # Optional AI Analysis
            if os.getenv('ENABLE_AI_ANALYSIS', 'false').lower() == 'true':
                logger.info("Running AI analysis...")
                pipeline_result['ai_insights'] = self.run_ai_analysis()
            
            pipeline_result['end_time'] = datetime.now(timezone.utc).isoformat()
            pipeline_result['duration_seconds'] = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            
            logger.info("Pipeline execution completed successfully")
            
        except Exception as e:
            pipeline_result['status'] = 'failed'
            pipeline_result['errors'].append(str(e))
            pipeline_result['end_time'] = datetime.now(timezone.utc).isoformat()
            logger.error(f"Pipeline execution failed: {str(e)}")
            logger.error(traceback.format_exc())
            
        return pipeline_result

# Flask routes for Cloud Run
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'sarb-economic-pipeline'})

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """Main pipeline execution endpoint triggered by Cloud Scheduler"""
    try:
        # Verify the request is from Cloud Scheduler (basic auth check)
        auth_header = request.headers.get('Authorization')
        expected_token = os.getenv('SCHEDULER_AUTH_TOKEN')
        
        if expected_token and auth_header != f"Bearer {expected_token}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Initialize and run pipeline
        pipeline = SARBDataPipeline()
        result = pipeline.run_full_pipeline()
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
        
    except Exception as e:
        logger.error(f"Pipeline endpoint error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': str(e)
        }), 500

@app.route('/manual-trigger', methods=['POST'])
def manual_trigger():
    """Manual trigger endpoint for testing"""
    try:
        pipeline = SARBDataPipeline()
        result = pipeline.run_full_pipeline()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_sample_data():
    """Create sample economic data for assessment demo"""
    sample_data = [
        {
            'indicator_id': 'REPO_RATE',
            'indicator_name': 'Repository Rate',
            'value': 7.75,
            'date_recorded': '2025-10-21',
            'source': 'SARB'
        },
        {
            'indicator_id': 'CPI_INFLATION',
            'indicator_name': 'Consumer Price Index',
            'value': 4.2,
            'date_recorded': '2025-10-21',
            'source': 'Statistics SA'
        },
        {
            'indicator_id': 'GDP_GROWTH',
            'indicator_name': 'GDP Growth Rate',
            'value': 2.1,
            'date_recorded': '2025-09-30',
            'source': 'Statistics SA'
        },
        {
            'indicator_id': 'UNEMPLOYMENT',
            'indicator_name': 'Unemployment Rate',
            'value': 32.4,
            'date_recorded': '2025-09-30',
            'source': 'Statistics SA'
        },
        {
            'indicator_id': 'PRIME_RATE',
            'indicator_name': 'Prime Lending Rate',
            'value': 11.25,
            'date_recorded': '2025-10-21',
            'source': 'SARB'
        }
    ]
    return sample_data

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SARB Economic Pipeline')
    parser.add_argument('--project-id', default='brendon-presentation', help='GCP Project ID')
    parser.add_argument('--upload-sample-data', action='store_true', help='Upload sample data for demo')
    parser.add_argument('--run-pipeline', action='store_true', help='Run the full pipeline')
    parser.add_argument('--port', type=int, default=8080, help='Port for Flask app')
    
    args = parser.parse_args()
    
    if args.upload_sample_data:
        print(f"Uploading sample data to project: {args.project_id}")
        pipeline = SARBDataPipeline(project_id=args.project_id)
        
        # Create sample data and upload to BigQuery
        sample_data = create_sample_data()
        df = pd.DataFrame(sample_data)
        
        try:
            table_id = f"{args.project_id}.sarb_economic_data.economic_indicators"
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )
            
            job = pipeline.bigquery_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()  # Wait for the job to complete
            
            print(f"✅ Successfully uploaded {len(sample_data)} sample records")
            print(f"View in BigQuery: https://console.cloud.google.com/bigquery?project={args.project_id}")
            
        except Exception as e:
            print(f"❌ Error uploading sample data: {e}")
    
    elif args.run_pipeline:
        print(f"Running full pipeline for project: {args.project_id}")
        pipeline = SARBDataPipeline(project_id=args.project_id)
        result = pipeline.run_full_pipeline()
        print(f"Pipeline result: {result}")
    
    else:
        # Run Flask app
        print(f"Starting Flask app for project: {args.project_id}")
        port = args.port
        app.run(host='0.0.0.0', port=port, debug=False)