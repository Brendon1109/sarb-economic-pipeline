-- SARB Economic Pipeline - 3-Tier Medallion Architecture
-- Bronze Layer (Raw Data) → Silver Layer (Cleansed) → Gold Layer (Business Ready)

-- ====================================
-- BRONZE LAYER - Raw Data Landing Zone
-- ====================================

-- Raw economic indicators table (exact copy of source data)
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.bronze_raw_indicators` (
    indicator_name STRING NOT NULL,
    value NUMERIC NOT NULL,
    date DATE NOT NULL,
    category STRING,
    unit STRING,
    source STRING,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    file_source STRING,
    row_hash STRING  -- For data lineage and deduplication
)
PARTITION BY DATE(date)
CLUSTER BY indicator_name, source;

-- Raw data quality audit table
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.bronze_data_quality_log` (
    audit_id STRING NOT NULL,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file STRING,
    total_records INT64,
    valid_records INT64,
    invalid_records INT64,
    data_quality_score NUMERIC,
    issues_detected ARRAY<STRING>
);

-- ====================================
-- SILVER LAYER - Cleansed & Standardized
-- ====================================

-- Cleansed and validated economic indicators
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.silver_economic_indicators` (
    indicator_id STRING NOT NULL,  -- Generated unique ID
    indicator_name STRING NOT NULL,
    indicator_category STRING NOT NULL,
    value NUMERIC NOT NULL,
    unit STRING NOT NULL,
    date DATE NOT NULL,
    source STRING NOT NULL,
    
    -- Data quality flags
    is_validated BOOLEAN DEFAULT TRUE,
    confidence_score NUMERIC DEFAULT 1.0,
    
    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_row_hash STRING,
    
    -- Business logic fields
    previous_value NUMERIC,
    period_change NUMERIC,
    period_change_percent NUMERIC
)
PARTITION BY DATE(date)
CLUSTER BY indicator_category, indicator_name;

-- Reference data for indicator definitions
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.silver_indicator_metadata` (
    indicator_name STRING NOT NULL,
    display_name STRING NOT NULL,
    category STRING NOT NULL,
    unit STRING NOT NULL,
    frequency STRING,  -- Daily, Monthly, Quarterly
    source STRING NOT NULL,
    description STRING,
    target_range_min NUMERIC,
    target_range_max NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- ====================================
-- GOLD LAYER - Business Ready / Reporting
-- ====================================

-- Executive dashboard view - latest key indicators
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.gold_executive_dashboard` (
    dashboard_date DATE NOT NULL,
    
    -- Key Economic Indicators
    gdp_growth_rate NUMERIC,
    inflation_rate NUMERIC,
    prime_interest_rate NUMERIC,
    unemployment_rate NUMERIC,
    usd_zar_exchange_rate NUMERIC,
    
    -- Calculated KPIs
    inflation_target_variance NUMERIC,  -- Distance from 4.5% target
    monetary_policy_stance STRING,      -- Accommodative/Neutral/Restrictive
    economic_health_score NUMERIC,     -- Composite score 0-100
    
    -- Trends (compared to previous period)
    gdp_trend STRING,                   -- Improving/Stable/Declining
    inflation_trend STRING,
    exchange_rate_trend STRING,
    
    -- Risk Indicators
    inflation_risk_level STRING,       -- Low/Medium/High
    exchange_rate_volatility NUMERIC,
    policy_uncertainty_index NUMERIC,
    
    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    data_freshness_hours NUMERIC
)
PARTITION BY dashboard_date
CLUSTER BY dashboard_date;

-- Monthly economic analysis summary
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.gold_monthly_analysis` (
    analysis_month DATE NOT NULL,  -- First day of month
    
    -- Monthly Aggregates
    avg_inflation_rate NUMERIC,
    avg_gdp_growth NUMERIC,
    avg_exchange_rate NUMERIC,
    avg_interest_rate NUMERIC,
    
    -- Monthly Statistics
    inflation_volatility NUMERIC,
    exchange_rate_volatility NUMERIC,
    max_inflation NUMERIC,
    min_inflation NUMERIC,
    
    -- Business KPIs
    inflation_target_compliance BOOLEAN,  -- Within 3-6% range
    months_above_target INT64,
    economic_stability_rating STRING,     -- Excellent/Good/Fair/Poor
    
    -- Policy Analysis
    policy_changes_count INT64,
    cumulative_rate_changes NUMERIC,
    
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY analysis_month
CLUSTER BY analysis_month;

-- Correlation analysis for economic relationships
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.gold_correlation_analysis` (
    analysis_date DATE NOT NULL,
    analysis_period STRING NOT NULL,  -- 3M, 6M, 12M, 24M
    
    -- Correlation Coefficients
    inflation_exchange_rate_corr NUMERIC,
    interest_rate_exchange_rate_corr NUMERIC,
    gdp_inflation_corr NUMERIC,
    unemployment_gdp_corr NUMERIC,
    
    -- Statistical Significance
    inflation_exchange_p_value NUMERIC,
    interest_exchange_p_value NUMERIC,
    
    -- Interpretation
    strongest_correlation STRING,
    correlation_strength STRING,  -- Strong/Moderate/Weak
    
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY analysis_date
CLUSTER BY analysis_period;

-- ====================================
-- AI INSIGHTS LAYER - Separate Summary Table
-- ====================================

-- AI-generated economic insights and recommendations
CREATE OR REPLACE TABLE `brendon-presentation.sarb_economic_data.ai_economic_insights` (
    insight_id STRING NOT NULL,
    analysis_date DATE NOT NULL,
    
    -- AI Analysis Components
    executive_summary STRING,
    monetary_policy_assessment STRING,
    exchange_rate_analysis STRING,
    risk_factors ARRAY<STRING>,
    policy_recommendations ARRAY<STRING>,
    
    -- AI Metadata
    ai_model_version STRING,
    ai_provider STRING,  -- vertex_ai, gemini_api, fallback
    confidence_score NUMERIC,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    -- Data Context
    data_points_analyzed INT64,
    analysis_period_start DATE,
    analysis_period_end DATE,
    
    -- Business Impact
    priority_level STRING,  -- High/Medium/Low
    actionable_items ARRAY<STRING>,
    
    PRIMARY KEY (insight_id) NOT ENFORCED
)
PARTITION BY analysis_date
CLUSTER BY analysis_date, ai_provider;

-- Final optimized reporting view
CREATE OR REPLACE VIEW `brendon-presentation.sarb_economic_data.reporting_economic_dashboard` AS
SELECT 
    ed.dashboard_date,
    
    -- Current Indicators
    ed.gdp_growth_rate,
    ed.inflation_rate,
    ed.prime_interest_rate,
    ed.unemployment_rate,
    ed.usd_zar_exchange_rate,
    
    -- Business KPIs
    ed.inflation_target_variance,
    ed.monetary_policy_stance,
    ed.economic_health_score,
    
    -- Trends
    ed.gdp_trend,
    ed.inflation_trend,
    ed.exchange_rate_trend,
    
    -- Risk Assessment
    ed.inflation_risk_level,
    ed.exchange_rate_volatility,
    
    -- Latest AI Insights (if available)
    ai.executive_summary,
    ai.policy_recommendations,
    ai.confidence_score as ai_confidence,
    
    -- Data Quality
    ed.data_freshness_hours,
    ed.created_timestamp
    
FROM `brendon-presentation.sarb_economic_data.gold_executive_dashboard` ed
LEFT JOIN `brendon-presentation.sarb_economic_data.ai_economic_insights` ai
    ON ed.dashboard_date = ai.analysis_date
    AND ai.insight_id = (
        SELECT insight_id 
        FROM `brendon-presentation.sarb_economic_data.ai_economic_insights` ai2 
        WHERE ai2.analysis_date = ed.dashboard_date 
        ORDER BY ai2.analysis_timestamp DESC 
        LIMIT 1
    )
ORDER BY ed.dashboard_date DESC;