-- BigQuery Infrastructure Setup for SARB Economic Pipeline
-- This script creates the dataset and tables required for the Assessment
-- Project ID: brendon-presentation (provided by assessor)

-- Create the main dataset for the assessment project
CREATE SCHEMA IF NOT EXISTS `brendon-presentation.sarb_economic_data`
OPTIONS (
  description = "SARB Economic Pipeline Assessment - Economic Indicators Dataset",
  location = "US"
);

-- Economic Indicators Table for Assessment Demo
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.economic_indicators` (
  indicator_id STRING NOT NULL,
  indicator_name STRING NOT NULL,
  value NUMERIC NOT NULL,
  date_recorded DATE NOT NULL,
  source STRING NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(date_recorded)
CLUSTER BY indicator_name, source
OPTIONS (
  description = "Silver layer table containing cleaned and standardized economic indicators from SARB",
  partition_expiration_days = NULL,
  require_partition_filter = false
);

-- Add table constraints and metadata
ALTER TABLE `sarb_economic_data.silver_economic_indicators`
SET OPTIONS (
  labels = [
    ("layer", "silver"),
    ("source", "sarb"),
    ("update_frequency", "daily")
  ]
);

-- Gold Layer: Macroeconomic Report View (Business-Ready)
CREATE OR REPLACE VIEW `sarb_economic_data.gold_macroeconomic_report` AS
WITH monthly_data AS (
  SELECT 
    DATE_TRUNC(observation_date, MONTH) as observation_month,
    indicator_code,
    AVG(value) as avg_value,
    COUNT(*) as data_points
  FROM `sarb_economic_data.silver_economic_indicators`
  WHERE observation_date >= '2010-01-01'
  GROUP BY observation_month, indicator_code
  HAVING COUNT(*) > 0  -- Ensure we have data points
),
pivoted_data AS (
  SELECT 
    observation_month,
    MAX(CASE WHEN indicator_code = 'KBP1005M' THEN avg_value END) as prime_rate,
    MAX(CASE WHEN indicator_code = 'KBP6006M' THEN avg_value END) as headline_cpi,
    MAX(CASE WHEN indicator_code = 'KBP1004M' THEN avg_value END) as zar_usd_exchange_rate,
    -- Additional metadata for data quality
    MAX(CASE WHEN indicator_code = 'KBP1005M' THEN data_points END) as prime_rate_data_points,
    MAX(CASE WHEN indicator_code = 'KBP6006M' THEN data_points END) as cpi_data_points,
    MAX(CASE WHEN indicator_code = 'KBP1004M' THEN data_points END) as exchange_rate_data_points
  FROM monthly_data
  GROUP BY observation_month
)
SELECT 
  observation_month,
  ROUND(prime_rate, 4) as prime_rate,
  ROUND(headline_cpi, 2) as headline_cpi,
  ROUND(zar_usd_exchange_rate, 4) as zar_usd_exchange_rate
FROM pivoted_data
WHERE observation_month IS NOT NULL
  AND (prime_rate IS NOT NULL OR headline_cpi IS NOT NULL OR zar_usd_exchange_rate IS NOT NULL)
ORDER BY observation_month;

-- Add view metadata
ALTER VIEW `sarb_economic_data.gold_macroeconomic_report`
SET OPTIONS (
  description = "Gold layer view providing business-ready macroeconomic indicators with monthly aggregation. Pivoted format with one row per month.",
  labels = [
    ("layer", "gold"),
    ("business_ready", "true"),
    ("aggregation", "monthly")
  ]
);

-- Optional Extension: AI Insights Table
CREATE OR REPLACE TABLE `sarb_economic_data.gold_automated_insights` (
  analysis_date DATE NOT NULL,
  generated_insight JSON NOT NULL,
  model_version STRING NOT NULL,
  load_timestamp TIMESTAMP NOT NULL
)
PARTITION BY analysis_date
OPTIONS (
  description = "Gold layer table storing AI-generated insights and analysis from Vertex AI Gemini",
  partition_expiration_days = 730  -- Keep insights for 2 years
);

-- Add primary key constraint (soft constraint for documentation)
ALTER TABLE `sarb_economic_data.gold_automated_insights`
SET OPTIONS (
  labels = [
    ("layer", "gold"),
    ("ai_generated", "true"),
    ("model", "gemini")
  ]
);

-- Create audit table for pipeline runs
CREATE OR REPLACE TABLE `sarb_economic_data.pipeline_audit_log` (
  run_id STRING NOT NULL,
  run_timestamp TIMESTAMP NOT NULL,
  pipeline_status STRING NOT NULL,
  bronze_files_count INT64,
  silver_records_count INT64,
  gold_view_updated BOOL,
  ai_analysis_completed BOOL,
  error_message STRING,
  execution_duration_seconds FLOAT64
)
PARTITION BY DATE(run_timestamp)
OPTIONS (
  description = "Audit log for pipeline execution tracking and monitoring",
  partition_expiration_days = 365
);

-- Performance optimization: Create materialized view for frequently accessed gold data
CREATE MATERIALIZED VIEW `sarb_economic_data.gold_macroeconomic_report_mv`
PARTITION BY DATE_TRUNC(observation_month, YEAR)
AS
SELECT * FROM `sarb_economic_data.gold_macroeconomic_report`
WHERE observation_month >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 YEAR);

-- Set up refresh schedule for materialized view
-- Note: This would typically be done through the BigQuery UI or REST API
-- ALTER MATERIALIZED VIEW `sarb_economic_data.gold_macroeconomic_report_mv`
-- SET OPTIONS (
--   enable_refresh = true,
--   refresh_interval_minutes = 1440  -- Daily refresh
-- );

-- Grant necessary permissions (to be customized based on service accounts)
-- These would typically be handled by your infrastructure as code
/*
-- Example permission grants (adjust project and service account names)
GRANT `roles/bigquery.dataEditor` ON SCHEMA `sarb_economic_data` 
TO "serviceAccount:sarb-pipeline@your-project.iam.gserviceaccount.com";

GRANT `roles/bigquery.dataViewer` ON SCHEMA `sarb_economic_data` 
TO "serviceAccount:bi-reporting@your-project.iam.gserviceaccount.com";
*/