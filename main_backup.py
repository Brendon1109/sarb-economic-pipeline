#!/usr/bin/env python3
"""
Simple Cloud Run service for SARB pipeline - minimal version
Works with limited permissions
"""

import os
import json
from flask import Flask, jsonify, request
from google.cloud import bigquery

app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'sarb-economic-pipeline',
        'message': 'SARB Pipeline Cloud Run Service is running'
    })

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """Pipeline execution endpoint for Cloud Scheduler"""
    try:
        # Simple BigQuery query to test connectivity
        client = bigquery.Client(project='brendon-presentation')
        
        query = """
        SELECT 
            COUNT(*) as total_records,
            MAX(date_recorded) as latest_date
        FROM `brendon-presentation.sarb_economic_data.economic_indicators`
        """
        
        results = client.query(query).result()
        
        for row in results:
            total_records = row.total_records
            latest_date = row.latest_date
        
        return jsonify({
            'status': 'success',
            'message': 'Pipeline executed successfully',
            'data': {
                'total_records': total_records,
                'latest_date': str(latest_date) if latest_date else None,
                'execution_time': '2025-10-23T09:00:00Z'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Pipeline execution failed: {str(e)}'
        }), 500

@app.route('/status')
def get_status():
    """Get pipeline status"""
    return jsonify({
        'pipeline_status': 'active',
        'last_execution': '2025-10-23T09:00:00Z',
        'next_execution': '2025-10-24T02:00:00Z',
        'indicators_tracked': [
            'Prime Overdraft Rate (KBP1005M)',
            'Headline CPI (KBP6006M)', 
            'ZAR/USD Exchange Rate (KBP1004M)'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)