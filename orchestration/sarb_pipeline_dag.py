"""
SARB Economic Pipeline - Airflow DAG with Orchestration Control
Implements automated pipeline with pause/resume capabilities
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.sql_sensor import SqlSensor
from airflow.models import Variable
from airflow.utils.dates import days_ago
import logging

# DAG Configuration
DEFAULT_ARGS = {
    'owner': 'sarb-data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1
}

# Pipeline Control Variables (set via Airflow UI)
PIPELINE_ENABLED = Variable.get("sarb_pipeline_enabled", default_var=True, deserialize_json=True)
AI_ANALYSIS_ENABLED = Variable.get("sarb_ai_enabled", default_var=True, deserialize_json=True)
DASHBOARD_UPDATE_ENABLED = Variable.get("sarb_dashboard_enabled", default_var=True, deserialize_json=True)

def check_pipeline_status(**context):
    """Check if pipeline should continue execution"""
    enabled = Variable.get("sarb_pipeline_enabled", default_var=True, deserialize_json=True)
    if not enabled:
        logging.info("🛑 Pipeline execution paused via control variable")
        return "pipeline_paused"
    return "continue_pipeline"

def ingest_raw_data(**context):
    """Bronze Layer: Ingest raw economic data"""
    logging.info("📥 Starting raw data ingestion...")
    
    # Import our pipeline class
    from src.main import SARBDataPipeline
    
    pipeline = SARBDataPipeline()
    
    # Simulate data ingestion (replace with actual data sources)
    raw_data = pipeline.fetch_economic_indicators()
    result = pipeline.ingest_to_bronze_layer(raw_data)
    
    logging.info(f"✅ Ingested {result['records_count']} records to Bronze layer")
    return result

def process_silver_layer(**context):
    """Silver Layer: Clean and validate data"""
    logging.info("🔄 Processing Silver layer...")
    
    from src.main import SARBDataPipeline
    pipeline = SARBDataPipeline()
    
    result = pipeline.process_silver_layer()
    logging.info(f"✅ Processed {result['records_processed']} records in Silver layer")
    return result

def create_gold_analytics(**context):
    """Gold Layer: Create business analytics"""
    logging.info("📊 Creating Gold layer analytics...")
    
    from src.main import SARBDataPipeline
    pipeline = SARBDataPipeline()
    
    result = pipeline.create_gold_views()
    logging.info(f"✅ Created {result['views_created']} analytical views")
    return result

def generate_ai_insights(**context):
    """AI Layer: Generate intelligent insights"""
    ai_enabled = Variable.get("sarb_ai_enabled", default_var=True, deserialize_json=True)
    
    if not ai_enabled:
        logging.info("🤖 AI analysis disabled via control variable")
        return {"status": "skipped", "reason": "AI disabled"}
    
    logging.info("🤖 Generating AI insights...")
    
    from src.main import SARBDataPipeline
    pipeline = SARBDataPipeline()
    
    result = pipeline.generate_ai_insights()
    logging.info(f"✅ Generated AI insights for {result['indicators_analyzed']} indicators")
    return result

def update_dashboards(**context):
    """Update visualization dashboards"""
    dashboard_enabled = Variable.get("sarb_dashboard_enabled", default_var=True, deserialize_json=True)
    
    if not dashboard_enabled:
        logging.info("📊 Dashboard updates disabled via control variable")
        return {"status": "skipped", "reason": "Dashboard updates disabled"}
    
    logging.info("📊 Updating dashboards...")
    
    from src.comprehensive_report_generator import SARBEconomicReportGenerator
    from src.looker_report_embedder import LookerReportEmbedder
    
    # Update reports
    report_gen = SARBEconomicReportGenerator()
    report_gen.generate_all_reports()
    
    # Update embeddable components
    embedder = LookerReportEmbedder()
    embedder.generate_all_embeds()
    
    logging.info("✅ Dashboards updated successfully")
    return {"status": "completed", "components_updated": 4}

def pipeline_health_check(**context):
    """Check pipeline health and data quality"""
    logging.info("🏥 Running pipeline health check...")
    
    from google.cloud import bigquery
    client = bigquery.Client(project='brendon-presentation')
    
    # Check data freshness
    freshness_query = """
    SELECT 
        MAX(date) as latest_date,
        COUNT(*) as total_records
    FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
    """
    
    result = list(client.query(freshness_query).result())[0]
    
    health_status = {
        "latest_data_date": str(result.latest_date),
        "total_records": result.total_records,
        "pipeline_healthy": result.total_records > 900,
        "data_fresh": (datetime.now().date() - result.latest_date).days < 7
    }
    
    if not health_status["pipeline_healthy"]:
        raise ValueError(f"Pipeline health check failed: {health_status}")
    
    logging.info(f"✅ Pipeline healthy: {health_status}")
    return health_status

def send_completion_notification(**context):
    """Send pipeline completion notification"""
    logging.info("📧 Sending completion notification...")
    
    # Get pipeline run statistics
    task_instances = context['dag_run'].get_task_instances()
    
    stats = {
        "total_tasks": len(task_instances),
        "successful_tasks": len([ti for ti in task_instances if ti.state == 'success']),
        "failed_tasks": len([ti for ti in task_instances if ti.state == 'failed']),
        "execution_time": str(datetime.now() - context['dag_run'].start_date)
    }
    
    logging.info(f"📊 Pipeline execution completed: {stats}")
    return stats

# Create the DAG
dag = DAG(
    'sarb_economic_pipeline',
    default_args=DEFAULT_ARGS,
    description='SARB Economic Data Pipeline with Orchestration Control',
    schedule_interval='0 6 * * 1-5',  # 6 AM weekdays
    catchup=False,
    max_active_runs=1,
    tags=['sarb', 'economics', 'data-pipeline', 'ai']
)

# Define tasks
pipeline_check = PythonOperator(
    task_id='check_pipeline_status',
    python_callable=check_pipeline_status,
    dag=dag
)

health_check = PythonOperator(
    task_id='pipeline_health_check',
    python_callable=pipeline_health_check,
    dag=dag
)

ingest_bronze = PythonOperator(
    task_id='ingest_raw_data',
    python_callable=ingest_raw_data,
    dag=dag
)

process_silver = PythonOperator(
    task_id='process_silver_layer',
    python_callable=process_silver_layer,
    dag=dag
)

create_gold = PythonOperator(
    task_id='create_gold_analytics',
    python_callable=create_gold_analytics,
    dag=dag
)

ai_insights = PythonOperator(
    task_id='generate_ai_insights',
    python_callable=generate_ai_insights,
    dag=dag
)

update_viz = PythonOperator(
    task_id='update_dashboards',
    python_callable=update_dashboards,
    dag=dag
)

completion_notification = PythonOperator(
    task_id='send_completion_notification',
    python_callable=send_completion_notification,
    dag=dag,
    trigger_rule='all_done'  # Run even if some tasks fail
)

# Pause points for manual intervention
manual_approval_bronze = DummyOperator(
    task_id='approve_bronze_data',
    dag=dag
)

manual_approval_ai = DummyOperator(
    task_id='approve_ai_analysis',
    dag=dag
)

# Data quality sensors
data_quality_sensor = SqlSensor(
    task_id='check_data_quality',
    conn_id='bigquery_default',
    sql="""
    SELECT COUNT(*) as record_count 
    FROM `brendon-presentation.sarb_silver_staging.economic_indicators_validated`
    WHERE date >= CURRENT_DATE() - 1
    """,
    mode='poke',
    timeout=300,
    poke_interval=60,
    dag=dag
)

# Define task dependencies
pipeline_check >> health_check >> ingest_bronze
ingest_bronze >> manual_approval_bronze >> process_silver
process_silver >> data_quality_sensor >> create_gold
create_gold >> manual_approval_ai >> ai_insights
ai_insights >> update_viz >> completion_notification

# Add parallel health monitoring
health_check >> data_quality_sensor