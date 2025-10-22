
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
     '<div style='padding: 10px; background: #f0f8f0; border-radius: 5px;'><strong>🏛️ SARB Economic Summary</strong><br>Latest analysis available in dashboard</div>' as html_content
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
:root {
    --sarb-green: #2C5530;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --info: #17a2b8;
    --background: #f8f9fa;
}
```

### **Font Consistency:**
```css
font-family: 'Google Sans', 'Segoe UI', Tahoma, sans-serif;
```

## 📱 **Mobile Optimization**

```css
@media (max-width: 768px) {
    .embed-container {
        padding: 10px;
        font-size: 0.9em;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}
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
function refreshEmbeddedContent() {
    fetch('/api/economic-summary')
        .then(response => response.json())
        .then(data => {
            document.getElementById('economic-alerts').innerHTML = data.html;
        });
}

// Auto-refresh every 30 minutes
setInterval(refreshEmbeddedContent, 1800000);
```

---

*This integration provides seamless embedding of your Python analysis reports directly into Looker Studio dashboards, maintaining real-time data connectivity and professional presentation.*
