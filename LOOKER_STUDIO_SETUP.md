# 📊 Looker Studio Dashboard Setup Guide

## 🎯 **Connecting Your SARB Economic Data to Looker Studio**

### **Step 1: Access Looker Studio**
1. Go to: https://lookerstudio.google.com/
2. Sign in with your Google account (same as your GCP account)

### **Step 2: Create New Report**
1. Click **"Create"** → **"Report"**
2. Choose **"BigQuery"** as data source
3. Select your project: **`brendon-presentation`**

### **Step 3: Connect to Your Economic Data**

#### **📈 For Economic Indicators Dashboard:**
```sql
-- Connect to: brendon-presentation.sarb_gold_reporting.comprehensive_economic_history
-- This table has 930+ records with full 15-year history
```

#### **🔄 For Economic Cycles Analysis:**
```sql
-- Connect to: brendon-presentation.sarb_gold_reporting.economic_cycles_analysis
-- This view shows period-by-period comparisons
```

#### **⚡ For Load Shedding Impact:**
```sql
-- Connect to: brendon-presentation.sarb_gold_reporting.load_shedding_impact_analysis
-- This view shows infrastructure crisis correlation
```

#### **📋 For Executive Summary:**
```sql
-- Connect to: brendon-presentation.sarb_gold_reporting.executive_15_year_summary
-- This view shows current indicators with historical context
```

### **Step 4: Recommended Chart Types**

#### **📊 Time Series Charts:**
- **Data Source:** `comprehensive_economic_history`
- **X-Axis:** `date`
- **Y-Axis:** `value`
- **Breakdown:** `indicator`
- **Filter:** Select specific indicators (GDP, Inflation, Unemployment, etc.)

#### **📈 Economic Cycles Comparison:**
- **Data Source:** `economic_cycles_analysis`
- **Chart Type:** Column Chart
- **X-Axis:** `economic_period`
- **Y-Axis:** `avg_gdp_growth`, `avg_inflation`, `avg_unemployment`
- **Color:** `period_performance_rating`

#### **⚡ Load Shedding Impact:**
- **Data Source:** `load_shedding_impact_analysis`
- **Chart Type:** Scatter Plot
- **X-Axis:** `loadshedding_hours`
- **Y-Axis:** `manufacturing_pmi`
- **Color:** `loadshedding_severity`

### **Step 5: Dashboard Features to Add**

#### **🎛️ Interactive Filters:**
- **Date Range Picker:** Filter by year/period
- **Economic Period:** Dropdown for specific periods
- **Indicator Type:** Multi-select for different indicators

#### **📊 Key Metrics Cards:**
- **Current GDP Growth**
- **Latest Unemployment Rate**
- **Inflation Status vs SARB Target**
- **Load Shedding Crisis Level**

#### **📈 Advanced Charts:**
- **Correlation Matrix:** Between different indicators
- **Trend Lines:** Show economic trajectories
- **Comparative Views:** Period-over-period changes

### **Step 6: Sharing Your Dashboard**
1. **Save Report:** Give it a name like "SARB Economic Analysis 2010-2024"
2. **Share:** Click share button and set permissions
3. **Embed:** Get embed code for presentations/websites
4. **Schedule:** Set up automated email reports

## 🎯 **Pre-Built Dashboard Queries**

### **Query 1: Economic Indicators Overview**
```sql
SELECT 
  date,
  indicator,
  value,
  economic_period,
  trend_direction
FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
WHERE date >= '2020-01-01'
ORDER BY date DESC
```

### **Query 2: Current Economic Health Score**
```sql
SELECT 
  indicator,
  current_value,
  year_over_year_change,
  historical_performance,
  executive_interpretation
FROM `brendon-presentation.sarb_gold_reporting.executive_15_year_summary`
```

### **Query 3: Load Shedding Crisis Analysis**
```sql
SELECT 
  year,
  AVG(loadshedding_hours) as avg_monthly_hours,
  AVG(manufacturing_pmi) as avg_pmi,
  COUNT(CASE WHEN loadshedding_severity = 'HIGH_IMPACT' THEN 1 END) as crisis_months
FROM `brendon-presentation.sarb_gold_reporting.load_shedding_impact_analysis`
GROUP BY year
ORDER BY year DESC
```

## 📱 **Mobile-Responsive Design Tips**
- Use **simple, clean layouts**
- **Large fonts** for mobile viewing
- **Color-coded** indicators (🟢 Good, 🟡 Moderate, 🔴 Concern)
- **Minimal scrolling** required

## 🔧 **Technical Notes**
- **Data Refresh:** Looker Studio will automatically refresh from BigQuery
- **Performance:** Views are optimized for dashboard queries
- **Security:** Inherits BigQuery permissions and access controls
- **Costs:** Looker Studio is free; only BigQuery query costs apply

## 🎨 **Styling Recommendations**
- **Colors:** Use South African flag colors (green, gold, red, blue)
- **Fonts:** Professional, readable fonts
- **Layout:** Clean, executive-friendly design
- **Branding:** Add SARB logo if available

---

*This guide creates professional, interactive dashboards using your 930+ economic records spanning 15 years (2010-2024)*