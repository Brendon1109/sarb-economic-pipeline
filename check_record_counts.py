#!/usr/bin/env python3
"""
Check record counts across all comprehensive dataset tables
"""

from google.cloud import bigquery

def main():
    client = bigquery.Client(project='brendon-presentation')
    
    print('📊 COMPREHENSIVE DATASET RECORD COUNTS')
    print('=' * 50)
    
    # Query each major table for record counts
    tables_to_check = [
        'sarb_gold_reporting.comprehensive_economic_history',
        'sarb_gold_reporting.executive_15_year_summary', 
        'sarb_gold_reporting.economic_cycles_analysis',
        'sarb_bronze_raw.economic_indicators_raw',
        'sarb_silver_staging.economic_indicators_validated'
    ]
    
    total_records = 0
    
    for table_name in tables_to_check:
        try:
            query = f"SELECT COUNT(*) as record_count FROM `brendon-presentation.{table_name}`"
            results = client.query(query).to_dataframe()
            count = results['record_count'].iloc[0]
            print(f"📋 {table_name:50} | {count:,} records")
            total_records += count
        except Exception as e:
            print(f"❌ {table_name:50} | Error: {str(e)[:60]}...")
    
    print('=' * 70)
    print(f"🎯 TOTAL COMPREHENSIVE RECORDS: {total_records:,}")
    
    # Check date coverage in main comprehensive table
    try:
        print('\n📅 DATE COVERAGE ANALYSIS')
        print('=' * 30)
        
        date_query = """
        SELECT 
            MIN(data_date) as earliest_date,
            MAX(data_date) as latest_date,
            COUNT(DISTINCT data_date) as unique_dates,
            COUNT(DISTINCT indicator_type) as indicator_types,
            COUNT(*) as total_records
        FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        """
        
        date_results = client.query(date_query).to_dataframe()
        
        for col in date_results.columns:
            value = date_results[col].iloc[0] 
            print(f"{col}: {value}")
            
        # Show sample data
        print('\n📋 SAMPLE DATA FROM COMPREHENSIVE HISTORY')
        print('=' * 40)
        
        sample_query = """
        SELECT 
            data_date,
            indicator_type,
            value,
            economic_period
        FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        ORDER BY data_date DESC
        LIMIT 10
        """
        
        sample_results = client.query(sample_query).to_dataframe()
        print(sample_results.to_string(index=False))
        
    except Exception as e:
        print(f"Date analysis error: {e}")

if __name__ == "__main__":
    main()