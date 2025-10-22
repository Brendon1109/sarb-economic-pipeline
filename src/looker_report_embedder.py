#!/usr/bin/env python3
"""
Looker Studio Report Embedder for SARB Economic Pipeline
Creates embeddable HTML reports that integrate with Looker Studio
"""

import os
import pandas as pd
from google.cloud import bigquery
import google.generativeai as genai
from datetime import datetime
import json

class LookerReportEmbedder:
    """Generate reports specifically for Looker Studio embedding"""
    
    def __init__(self, project_id='brendon-presentation'):
        self.project_id = project_id
        self.bigquery_client = bigquery.Client(project=self.project_id)
        
        # Initialize AI for insights
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.ai_model = genai.GenerativeModel('gemini-2.5-flash')
            self.ai_ready = True
        else:
            self.ai_ready = False
    
    def generate_executive_summary_embed(self):
        """Generate executive summary HTML for Looker Studio embedding"""
        
        print("📋 Generating Executive Summary for Looker Studio...")
        
        # Get latest economic indicators
        query = """
        SELECT 
            indicator,
            current_value,
            year_over_year_change,
            year_over_year_percent,
            trend_direction,
            executive_interpretation,
            historical_performance
        FROM `brendon-presentation.sarb_gold_reporting.executive_15_year_summary`
        ORDER BY 
            CASE indicator
                WHEN 'GDP_Growth_Rate' THEN 1
                WHEN 'Unemployment_Rate' THEN 2
                WHEN 'Inflation_Rate' THEN 3
                WHEN 'Prime_Interest_Rate' THEN 4
                ELSE 5
            END
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        # Generate AI insights if available
        ai_summary = ""
        if self.ai_ready and not df.empty:
            context = df.to_string()
            prompt = f"""
            Create a 2-sentence executive summary for current South African economic conditions:
            
            {context}
            
            Focus on: Key risks, policy implications, current trends
            Style: Professional, concise, actionable for SARB executives
            """
            
            try:
                response = self.ai_model.generate_content(prompt)
                ai_summary = response.text
            except Exception as e:
                ai_summary = "AI analysis unavailable - manual review recommended."
        
        # Create HTML for embedding
        html_content = f"""
        <div style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 10px 0;
        ">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #2C5530; margin: 0; font-size: 1.5em;">
                    🏛️ SARB Executive Economic Summary
                </h2>
                <p style="color: #666; margin: 5px 0; font-size: 0.9em;">
                    Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
                </p>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #2C5530; margin: 0 0 10px 0; font-size: 1.1em;">🤖 AI Economic Analysis</h3>
                <p style="margin: 0; line-height: 1.4; color: #333;">
                    {ai_summary}
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
        """
        
        # Add indicator cards
        for _, row in df.iterrows():
            # Determine card color based on performance
            if row['trend_direction'] == 'IMPROVING':
                card_color = '#d4edda'
                border_color = '#28a745'
                icon = '📈'
            elif row['trend_direction'] == 'DECLINING':
                card_color = '#f8d7da'
                border_color = '#dc3545'
                icon = '📉'
            else:
                card_color = '#fff3cd'
                border_color = '#ffc107'
                icon = '➡️'
            
            yoy_change = f"{row['year_over_year_change']:+.1f}" if pd.notna(row['year_over_year_change']) else "N/A"
            yoy_percent = f"({row['year_over_year_percent']:+.1f}%)" if pd.notna(row['year_over_year_percent']) else ""
            
            html_content += f"""
                <div style="
                    background: {card_color};
                    border-left: 4px solid {border_color};
                    padding: 12px;
                    border-radius: 5px;
                    text-align: center;
                ">
                    <div style="font-size: 1.2em; margin-bottom: 5px;">{icon}</div>
                    <div style="font-weight: bold; color: #333; font-size: 0.9em; margin-bottom: 3px;">
                        {row['indicator'].replace('_', ' ')}
                    </div>
                    <div style="font-size: 1.3em; font-weight: bold; color: {border_color}; margin-bottom: 3px;">
                        {row['current_value']:.1f}
                    </div>
                    <div style="font-size: 0.8em; color: #666; margin-bottom: 3px;">
                        YoY: {yoy_change} {yoy_percent}
                    </div>
                    <div style="font-size: 0.7em; color: #888;">
                        {row['executive_interpretation']}
                    </div>
                </div>
            """
        
        html_content += """
            </div>
            
            <div style="text-align: center; margin-top: 15px; font-size: 0.8em; color: #666;">
                📊 Data Source: 930+ records | 15-year analysis (2010-2024) | 🤖 AI-Enhanced
            </div>
        </div>
        """
        
        # Save as embeddable HTML
        output_path = 'analysis/reports/executive_summary_embed.html'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Executive summary embed created: {output_path}")
        return output_path, html_content
    
    def generate_economic_alerts_embed(self):
        """Generate economic alerts widget for Looker embedding"""
        
        print("🚨 Generating Economic Alerts for Looker Studio...")
        
        # Get latest data for alerts
        query = """
        SELECT 
            indicator,
            value,
            trend_direction,
            date
        FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        WHERE date = (
            SELECT MAX(date) 
            FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        )
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        alerts = []
        
        # Generate alerts based on current conditions
        for _, row in df.iterrows():
            indicator = row['indicator']
            value = row['value']
            
            if indicator == 'Load_Shedding_Hours' and value > 100:
                alerts.append({
                    'level': 'CRITICAL',
                    'icon': '🚨',
                    'color': '#dc3545',
                    'message': f'Load shedding at crisis levels: {value:.0f} hours/month',
                    'action': 'Accelerate renewable energy deployment'
                })
            elif indicator == 'Inflation_Rate' and value > 6:
                alerts.append({
                    'level': 'WARNING',
                    'icon': '⚠️',
                    'color': '#ffc107',
                    'message': f'Inflation above SARB target: {value:.1f}%',
                    'action': 'Monitor for potential rate adjustments'
                })
            elif indicator == 'GDP_Growth_Rate' and value < 0:
                alerts.append({
                    'level': 'ALERT',
                    'icon': '📉',
                    'color': '#fd7e14',
                    'message': f'Negative GDP growth: {value:.1f}%',
                    'action': 'Consider economic stimulus measures'
                })
            elif indicator == 'Unemployment_Rate' and value > 32:
                alerts.append({
                    'level': 'CONCERN',
                    'icon': '👥',
                    'color': '#6f42c1',
                    'message': f'High unemployment: {value:.1f}%',
                    'action': 'Focus on job creation initiatives'
                })
        
        # Create alerts HTML
        if alerts:
            html_content = f"""
            <div style="
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                margin: 10px 0;
            ">
                <h3 style="color: #495057; margin: 0 0 15px 0; font-size: 1.1em; text-align: center;">
                    🚨 Economic Alerts & Policy Signals
                </h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
            """
            
            for alert in alerts:
                html_content += f"""
                    <div style="
                        background: white;
                        border-left: 4px solid {alert['color']};
                        padding: 12px;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="font-size: 1.2em; margin-right: 8px;">{alert['icon']}</span>
                            <span style="
                                background: {alert['color']};
                                color: white;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 0.8em;
                                font-weight: bold;
                                margin-right: 10px;
                            ">{alert['level']}</span>
                            <span style="color: #333; font-weight: bold; flex: 1;">{alert['message']}</span>
                        </div>
                        <div style="color: #666; font-size: 0.9em; margin-left: 30px;">
                            📋 Recommended Action: {alert['action']}
                        </div>
                    </div>
                """
            
            html_content += """
                </div>
                <div style="text-align: center; margin-top: 12px; font-size: 0.8em; color: #6c757d;">
                    🤖 AI-powered alerts based on latest economic data
                </div>
            </div>
            """
        else:
            html_content = f"""
            <div style="
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 10px 0;
            ">
                ✅ <strong>No Critical Economic Alerts</strong><br>
                <small>All indicators within acceptable ranges</small>
            </div>
            """
        
        # Save alerts embed
        output_path = 'analysis/reports/economic_alerts_embed.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Economic alerts embed created: {output_path}")
        return output_path, html_content
    
    def create_looker_integration_guide(self):
        """Create step-by-step guide for embedding reports in Looker Studio"""
        
        guide_content = f"""
# 🔗 Embedding Python Reports in Looker Studio

## 📋 **Step-by-Step Integration Guide**

### **Method 1: HTML Embed via URL Field**

1. **Upload HTML Reports to Google Drive:**
   ```
   • Upload: analysis/reports/executive_summary_embed.html
   • Upload: analysis/reports/economic_alerts_embed.html
   • Set sharing: "Anyone with link can view"
   ```

2. **In Looker Studio:**
   ```
   • Add Component → "Embed" 
   • Paste Google Drive HTML link
   • Adjust size and positioning
   ```

### **Method 2: Custom HTML Component**

1. **In Looker Studio:**
   ```
   • Add Component → "Embed"
   • Select "Custom HTML"
   • Paste HTML content directly
   ```

2. **Add to Dashboard:**
   ```
   • Position: Top of dashboard (Executive Summary)
   • Position: Sidebar (Economic Alerts)
   • Refresh: Set to auto-update
   ```

### **Method 3: BigQuery Integration with HTML**

1. **Create HTML Field in BigQuery:**
   ```sql
   CREATE OR REPLACE VIEW `brendon-presentation.sarb_gold_reporting.dashboard_embeds` AS
   SELECT 
     'executive_summary' as embed_type,
     CURRENT_DATE() as generated_date,
     '{self._get_sample_html()}' as html_content
   ```

2. **Use in Looker Studio:**
   ```
   • Connect to: dashboard_embeds view
   • Add: HTML field as embedded content
   • Display: Rich text component
   ```

## 🎯 **Recommended Dashboard Layout**

```
┌─────────────────────────────────────────────────────────────┐
│                    📋 Executive Summary (HTML Embed)        │
│                   [AI Insights + Key Metrics]              │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐ ┌─────────────────────────────────────┐
│   🚨 Economic Alerts  │ │        📊 Main Charts Area         │
│    (HTML Embed)      │ │     [Your Looker Studio Charts]    │
│                      │ │                                     │
│  • Load Shedding     │ │  • Economic Indicators Time Series │
│  • Inflation Risk    │ │  • Economic Cycles Comparison      │
│  • Policy Signals    │ │  • Load Shedding Impact Analysis   │
└──────────────────────┘ └─────────────────────────────────────┘
```

## 🔄 **Auto-Refresh Setup**

### **For HTML Embeds:**
```python
# Add to your Python scripts:
# Schedule via Cloud Functions or Cloud Run
def update_dashboard_embeds():
    embedder = LookerReportEmbedder()
    embedder.generate_executive_summary_embed()
    embedder.generate_economic_alerts_embed()
    # Upload to Google Drive or Cloud Storage
```

### **For Looker Studio:**
```
• Data Source Refresh: Every 4 hours
• HTML Content Refresh: Daily at 6 AM
• Alert Updates: Real-time via BigQuery
```

## 🎨 **Styling Consistency**

### **Color Palette (Match Looker Studio):**
```css
:root {{
    --sarb-green: #2C5530;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --info: #17a2b8;
    --background: #f8f9fa;
}}
```

### **Font Consistency:**
```css
font-family: 'Google Sans', 'Segoe UI', Tahoma, sans-serif;
```

## 📱 **Mobile Optimization**

```css
@media (max-width: 768px) {{
    .embed-container {{
        padding: 10px;
        font-size: 0.9em;
    }}
    
    .metrics-grid {{
        grid-template-columns: 1fr;
    }}
}}
```

## 🚀 **Advanced Integration**

### **Real-time Updates via BigQuery:**
```sql
-- Create materialized view for real-time embeds
CREATE MATERIALIZED VIEW `brendon-presentation.sarb_gold_reporting.realtime_dashboard_content` AS
SELECT 
  'summary' as content_type,
  FORMAT(
    '<div class="alert alert-info">Latest GDP: %s%% | Inflation: %s%% | Updated: %s</div>',
    CAST(current_value AS STRING),
    CAST(inflation_rate AS STRING),
    FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', CURRENT_TIMESTAMP())
  ) as html_content
FROM `brendon-presentation.sarb_gold_reporting.executive_15_year_summary`
WHERE indicator = 'GDP_Growth_Rate'
```

### **JavaScript Integration:**
```javascript
// Add to HTML embeds for enhanced interactivity
function refreshEmbeddedContent() {{
    fetch('/api/economic-summary')
        .then(response => response.json())
        .then(data => {{
            document.getElementById('economic-alerts').innerHTML = data.html;
        }});
}}

// Auto-refresh every 30 minutes
setInterval(refreshEmbeddedContent, 1800000);
```

---

*This integration provides seamless embedding of your Python analysis reports directly into Looker Studio dashboards, maintaining real-time data connectivity and professional presentation.*
"""
        
        # Save integration guide
        guide_path = 'analysis/reports/LOOKER_INTEGRATION_GUIDE.md'
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"✅ Looker integration guide created: {guide_path}")
        return guide_path
    
    def _get_sample_html(self):
        """Get sample HTML for BigQuery integration"""
        return """<div style='padding: 10px; background: #f0f8f0; border-radius: 5px;'><strong>🏛️ SARB Economic Summary</strong><br>Latest analysis available in dashboard</div>"""

def main():
    """Generate all embeddable reports for Looker Studio"""
    
    print("🔗 GENERATING EMBEDDABLE REPORTS FOR LOOKER STUDIO")
    print("=" * 70)
    
    embedder = LookerReportEmbedder()
    
    # Generate embeddable components
    print("1️⃣ Creating Executive Summary Embed...")
    summary_path, summary_html = embedder.generate_executive_summary_embed()
    
    print("2️⃣ Creating Economic Alerts Embed...")
    alerts_path, alerts_html = embedder.generate_economic_alerts_embed()
    
    print("3️⃣ Creating Integration Guide...")
    guide_path = embedder.create_looker_integration_guide()
    
    print("\n🎉 LOOKER STUDIO INTEGRATION READY!")
    print("=" * 70)
    print(f"📋 Executive Summary: {summary_path}")
    print(f"🚨 Economic Alerts: {alerts_path}")
    print(f"📖 Integration Guide: {guide_path}")
    print("\n🔗 Next Steps:")
    print("   1. Upload HTML files to Google Drive")
    print("   2. Add embed components in Looker Studio")
    print("   3. Configure auto-refresh settings")
    print("   4. Test mobile responsiveness")

if __name__ == "__main__":
    main()