#!/usr/bin/env python3
"""
SARB Economic Pipeline - Comprehensive Data Report Generator
Generate executive reports from the complete 15-year economic dataset
"""

import os
import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import google.generativeai as genai
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SARBEconomicReportGenerator:
    """Generate comprehensive reports from SARB economic data"""
    
    def __init__(self, project_id='brendon-presentation', gemini_api_key=None):
        self.project_id = project_id
        self.bigquery_client = bigquery.Client(project=self.project_id)
        
        # Initialize AI for enhanced insights
        self.ai_ready = False
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.ai_model = genai.GenerativeModel('gemini-2.5-flash')
                self.ai_ready = True
                logger.info("✅ AI ready for report enhancement")
            except Exception as e:
                logger.warning(f"⚠️ AI not available: {e}")
    
    def generate_executive_summary_report(self):
        """Generate executive summary report from the 15-year dataset"""
        
        print("📊 GENERATING EXECUTIVE SUMMARY REPORT")
        print("=" * 60)
        
        # 1. Get latest indicators summary
        print("🔍 Fetching executive 15-year summary...")
        
        summary_query = """
        SELECT 
            indicator,
            current_value,
            year_over_year_change,
            year_over_year_percent,
            trend_direction,
            fifteen_year_average,
            historical_min,
            historical_max,
            historical_performance,
            executive_interpretation
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
        
        summary_df = self.bigquery_client.query(summary_query).to_dataframe()
        
        # 2. Get economic cycles analysis
        print("🔄 Fetching economic cycles analysis...")
        
        cycles_query = """
        SELECT 
            economic_period,
            avg_gdp_growth,
            avg_inflation,
            avg_unemployment,
            avg_prime_rate,
            period_narrative,
            period_performance_rating
        FROM `brendon-presentation.sarb_gold_reporting.economic_cycles_analysis`
        ORDER BY 
            CASE economic_period
                WHEN 'Post-Crisis Recovery' THEN 1
                WHEN 'Commodity Decline' THEN 2
                WHEN 'Political Uncertainty' THEN 3
                WHEN 'COVID-19 Impact' THEN 4
                WHEN 'Load Shedding Crisis' THEN 5
            END
        """
        
        cycles_df = self.bigquery_client.query(cycles_query).to_dataframe()
        
        # 3. Get load shedding impact (recent years)
        print("⚡ Fetching load shedding impact analysis...")
        
        loadshedding_query = """
        SELECT 
            year,
            AVG(loadshedding_hours) as avg_monthly_hours,
            AVG(manufacturing_pmi) as avg_pmi,
            COUNT(CASE WHEN loadshedding_severity = 'HIGH_IMPACT' THEN 1 END) as high_impact_months,
            COUNT(*) as total_months
        FROM `brendon-presentation.sarb_gold_reporting.load_shedding_impact_analysis`
        WHERE year >= 2019
        GROUP BY year
        ORDER BY year DESC
        """
        
        loadshedding_df = self.bigquery_client.query(loadshedding_query).to_dataframe()
        
        # 4. Generate comprehensive report
        report = self._format_executive_report(summary_df, cycles_df, loadshedding_df)
        
        # 5. Save report
        report_path = Path("analysis/SARB_Executive_Economic_Report.md")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Executive report saved: {report_path}")
        return report_path
    
    def _format_executive_report(self, summary_df, cycles_df, loadshedding_df):
        """Format comprehensive executive report"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        report = f"""# 🏛️ SARB Economic Pipeline - Executive Summary Report
**Generated:** {current_date}  
**Data Period:** January 2010 - October 2024 (15 Years)  
**Total Records Analyzed:** 930+ economic data points

---

## 📈 **Current Economic Indicators Summary**

| Indicator | Current Value | YoY Change | Historical Context | Trend | Interpretation |
|-----------|---------------|------------|-------------------|-------|----------------|
"""
        
        # Add current indicators
        for _, row in summary_df.iterrows():
            yoy_change = f"{row['year_over_year_change']:+.1f}" if pd.notna(row['year_over_year_change']) else "N/A"
            yoy_percent = f"({row['year_over_year_percent']:+.1f}%)" if pd.notna(row['year_over_year_percent']) else ""
            
            report += f"| **{row['indicator'].replace('_', ' ')}** | {row['current_value']:.1f} | {yoy_change} {yoy_percent} | {row['historical_performance']} | {row['trend_direction']} | {row['executive_interpretation']} |\n"
        
        report += "\n---\n\n"
        
        # Economic Cycles Analysis
        report += "## 🔄 **15-Year Economic Cycles Analysis**\n\n"
        
        for _, period in cycles_df.iterrows():
            performance_emoji = {
                'HIGH_PERFORMANCE': '🟢',
                'MODERATE_PERFORMANCE': '🟡', 
                'CHALLENGING_PERFORMANCE': '🔴'
            }.get(period['period_performance_rating'], '⚪')
            
            report += f"### {performance_emoji} **{period['economic_period']}**\n"
            report += f"**Context:** {period['period_narrative']}\n\n"
            report += f"**Key Metrics:**\n"
            report += f"- GDP Growth: {period['avg_gdp_growth']:.1f}%\n"
            report += f"- Inflation: {period['avg_inflation']:.1f}%\n"
            report += f"- Unemployment: {period['avg_unemployment']:.1f}%\n"
            report += f"- Prime Rate: {period['avg_prime_rate']:.1f}%\n"
            report += f"- **Performance Rating:** {period['period_performance_rating']}\n\n"
        
        report += "---\n\n"
        
        # Load Shedding Impact
        report += "## ⚡ **Infrastructure Crisis Impact (2019-2024)**\n\n"
        report += "**Load Shedding Impact on Economic Activity:**\n\n"
        
        for _, year_data in loadshedding_df.iterrows():
            high_impact_pct = (year_data['high_impact_months'] / year_data['total_months']) * 100
            
            impact_level = "🔴 SEVERE" if high_impact_pct > 50 else "🟡 MODERATE" if high_impact_pct > 25 else "🟢 LIMITED"
            
            report += f"**{int(year_data['year'])}:** {year_data['avg_monthly_hours']:.0f} avg hours/month | PMI: {year_data['avg_pmi']:.1f} | {impact_level} ({high_impact_pct:.0f}% high-impact months)\n"
        
        report += "\n---\n\n"
        
        # Key Insights
        report += "## 🎯 **Key Strategic Insights**\n\n"
        
        # Calculate some insights from the data
        latest_gdp = summary_df[summary_df['indicator'] == 'GDP_Growth_Rate']['current_value'].iloc[0] if len(summary_df[summary_df['indicator'] == 'GDP_Growth_Rate']) > 0 else None
        latest_unemployment = summary_df[summary_df['indicator'] == 'Unemployment_Rate']['current_value'].iloc[0] if len(summary_df[summary_df['indicator'] == 'Unemployment_Rate']) > 0 else None
        latest_inflation = summary_df[summary_df['indicator'] == 'Inflation_Rate']['current_value'].iloc[0] if len(summary_df[summary_df['indicator'] == 'Inflation_Rate']) > 0 else None
        
        report += "### 🔍 **Economic Performance Analysis**\n\n"
        
        if latest_gdp:
            if latest_gdp > 2.5:
                report += "✅ **Growth Momentum:** Economy showing strong growth momentum above 2.5%\n"
            elif latest_gdp > 1.0:
                report += "⚠️ **Moderate Growth:** Economic growth present but below optimal levels\n"
            else:
                report += "🔴 **Growth Concerns:** Economic growth insufficient for development needs\n"
        
        if latest_unemployment:
            if latest_unemployment > 30.0:
                report += "🔴 **Employment Crisis:** Unemployment at crisis levels requiring urgent intervention\n"
            elif latest_unemployment > 25.0:
                report += "⚠️ **Employment Challenge:** Elevated unemployment constraining economic potential\n"
            else:
                report += "✅ **Employment Stability:** Unemployment within manageable ranges\n"
        
        if latest_inflation:
            if 3.0 <= latest_inflation <= 6.0:
                report += "✅ **Price Stability:** Inflation within SARB target range\n"
            elif latest_inflation > 6.0:
                report += "🔴 **Inflation Risk:** Above-target inflation requiring monetary policy attention\n"
            else:
                report += "⚠️ **Deflationary Risk:** Below-target inflation may signal economic weakness\n"
        
        report += "\n### 🏗️ **Infrastructure Impact**\n\n"
        
        recent_avg_hours = loadshedding_df[loadshedding_df['year'] >= 2022]['avg_monthly_hours'].mean()
        if recent_avg_hours > 100:
            report += "🔴 **Critical Infrastructure Constraint:** Load shedding severely impacting economic activity\n"
            report += "📋 **Recommendation:** Accelerate renewable energy investment and grid stability programs\n"
        elif recent_avg_hours > 50:
            report += "⚠️ **Moderate Infrastructure Risk:** Load shedding creating business uncertainty\n"
            report += "📋 **Recommendation:** Implement energy security measures and backup systems\n"
        else:
            report += "✅ **Infrastructure Stability:** Load shedding at manageable levels\n"
        
        report += "\n---\n\n"
        
        # Policy Recommendations
        report += "## 📋 **Strategic Policy Recommendations**\n\n"
        
        report += "### 🎯 **Immediate Priorities (0-12 months)**\n"
        report += "1. **Infrastructure Resilience:** Accelerate renewable energy deployment\n"
        report += "2. **Employment Creation:** Implement targeted job creation programs\n"
        report += "3. **Inflation Management:** Monitor price pressures and adjust monetary policy\n\n"
        
        report += "### 🚀 **Medium-term Strategy (1-3 years)**\n"
        report += "1. **Structural Reforms:** Address regulatory constraints on growth\n"
        report += "2. **Skills Development:** Align education with economic transformation\n"
        report += "3. **Investment Climate:** Improve ease of doing business metrics\n\n"
        
        report += "### 🌟 **Long-term Vision (3-10 years)**\n"
        report += "1. **Economic Diversification:** Reduce commodity dependence\n"
        report += "2. **Technology Adoption:** Embrace 4IR technologies\n"
        report += "3. **Regional Integration:** Leverage AfCFTA opportunities\n\n"
        
        report += "---\n\n"
        
        # Data Sources and Methodology
        report += "## 📊 **Data Sources & Methodology**\n\n"
        report += "**Data Sources:**\n"
        report += "- Statistics South Africa (StatsSA)\n"
        report += "- South African Reserve Bank (SARB)\n"
        report += "- Bureau for Economic Research\n"
        report += "- Eskom Holdings\n\n"
        
        report += "**Analysis Period:** 15 years (January 2010 - October 2024)\n"
        report += "**Total Data Points:** 930+ economic indicators\n"
        report += "**Economic Periods Analyzed:** 5 distinct cycles\n"
        report += "**Indicators Tracked:** GDP, Inflation, Unemployment, Interest Rates, Exchange Rates, PMI, Load Shedding\n\n"
        
        report += "**Methodology:**\n"
        report += "- Medallion Architecture (Bronze → Silver → Gold)\n"
        report += "- 15-year historical context analysis\n"
        report += "- Economic cycle-based segmentation\n"
        report += "- Infrastructure impact correlation\n"
        report += "- AI-enhanced insights (Gemini 2.5 Flash)\n\n"
        
        report += "---\n\n"
        report += f"*Report generated by SARB Economic Pipeline on {current_date}*\n"
        report += "*For technical questions, contact the Data Engineering team*"
        
        return report
    
    def generate_detailed_charts(self):
        """Generate detailed visualization charts"""
        
        print("📈 GENERATING DETAILED VISUALIZATION CHARTS")
        print("=" * 60)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create charts directory
        charts_dir = Path("analysis/charts")
        charts_dir.mkdir(exist_ok=True)
        
        # 1. Economic Indicators Time Series
        print("📊 Creating economic indicators time series...")
        self._create_time_series_chart(charts_dir)
        
        # 2. Economic Cycles Comparison
        print("🔄 Creating economic cycles comparison...")
        self._create_cycles_comparison_chart(charts_dir)
        
        # 3. Load Shedding Impact Analysis
        print("⚡ Creating load shedding impact visualization...")
        self._create_loadshedding_impact_chart(charts_dir)
        
        print(f"✅ All charts saved to: {charts_dir}")
        return charts_dir
    
    def _create_time_series_chart(self, charts_dir):
        """Create time series chart for key indicators"""
        
        query = """
        SELECT 
            date,
            indicator,
            value,
            economic_period
        FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        WHERE indicator IN ('GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate', 'Prime_Interest_Rate')
        AND date >= '2015-01-01'
        ORDER BY date, indicator
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        df['date'] = pd.to_datetime(df['date'])
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Key Economic Indicators (2015-2024)', fontsize=16, fontweight='bold')
        
        indicators = ['GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate', 'Prime_Interest_Rate']
        titles = ['GDP Growth Rate (%)', 'Inflation Rate (%)', 'Unemployment Rate (%)', 'Prime Interest Rate (%)']
        
        for i, (indicator, title) in enumerate(zip(indicators, titles)):
            ax = axes[i//2, i%2]
            indicator_data = df[df['indicator'] == indicator]
            
            if not indicator_data.empty:
                ax.plot(indicator_data['date'], indicator_data['value'], linewidth=2, marker='o', markersize=2)
                ax.set_title(title, fontweight='bold')
                ax.set_xlabel('Year')
                ax.set_ylabel('Percentage')
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(charts_dir / 'economic_indicators_timeseries.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_cycles_comparison_chart(self, charts_dir):
        """Create economic cycles comparison chart"""
        
        query = """
        SELECT 
            economic_period,
            avg_gdp_growth,
            avg_inflation,
            avg_unemployment,
            avg_prime_rate
        FROM `brendon-presentation.sarb_gold_reporting.economic_cycles_analysis`
        ORDER BY 
            CASE economic_period
                WHEN 'Post-Crisis Recovery' THEN 1
                WHEN 'Commodity Decline' THEN 2
                WHEN 'Political Uncertainty' THEN 3
                WHEN 'COVID-19 Impact' THEN 4
                WHEN 'Load Shedding Crisis' THEN 5
            END
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        if not df.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            x = range(len(df))
            width = 0.2
            
            ax.bar([i - 1.5*width for i in x], df['avg_gdp_growth'], width, label='GDP Growth', alpha=0.8)
            ax.bar([i - 0.5*width for i in x], df['avg_inflation'], width, label='Inflation', alpha=0.8)
            ax.bar([i + 0.5*width for i in x], df['avg_unemployment'], width, label='Unemployment', alpha=0.8)
            ax.bar([i + 1.5*width for i in x], df['avg_prime_rate'], width, label='Prime Rate', alpha=0.8)
            
            ax.set_xlabel('Economic Period')
            ax.set_ylabel('Rate (%)')
            ax.set_title('Economic Indicators by Period (2010-2024)', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([period.replace(' ', '\n') for period in df['economic_period']], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(charts_dir / 'economic_cycles_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_loadshedding_impact_chart(self, charts_dir):
        """Create load shedding impact visualization"""
        
        query = """
        SELECT 
            year,
            month,
            loadshedding_hours,
            manufacturing_pmi,
            loadshedding_severity
        FROM `brendon-presentation.sarb_gold_reporting.load_shedding_impact_analysis`
        WHERE year >= 2019
        ORDER BY year, month
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        if not df.empty:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Create date column
            df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
            
            # Plot 1: Load shedding hours over time
            colors = {'LOW_IMPACT': 'green', 'MODERATE_IMPACT': 'orange', 'HIGH_IMPACT': 'red'}
            for severity in df['loadshedding_severity'].unique():
                severity_data = df[df['loadshedding_severity'] == severity]
                ax1.scatter(severity_data['date'], severity_data['loadshedding_hours'], 
                           c=colors.get(severity, 'gray'), label=severity, alpha=0.7, s=30)
            
            ax1.set_title('Load Shedding Hours by Severity (2019-2024)', fontweight='bold')
            ax1.set_ylabel('Hours per Month')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: PMI correlation
            ax2.scatter(df['loadshedding_hours'], df['manufacturing_pmi'], alpha=0.6, c='steelblue')
            ax2.set_xlabel('Load Shedding Hours')
            ax2.set_ylabel('Manufacturing PMI')
            ax2.set_title('Manufacturing PMI vs Load Shedding Correlation', fontweight='bold')
            ax2.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='PMI 50 (Expansion/Contraction)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(charts_dir / 'loadshedding_impact_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_ai_enhanced_insights(self):
        """Generate AI-enhanced insights using Gemini"""
        
        if not self.ai_ready:
            print("⚠️ AI not available for enhanced insights")
            return None
        
        print("🤖 GENERATING AI-ENHANCED INSIGHTS")
        print("=" * 60)
        
        # Get latest economic data for AI analysis
        data_query = """
        SELECT 
            indicator,
            current_value,
            year_over_year_change,
            trend_direction,
            executive_interpretation,
            historical_performance
        FROM `brendon-presentation.sarb_gold_reporting.executive_15_year_summary`
        """
        
        data_df = self.bigquery_client.query(data_query).to_dataframe()
        
        # Prepare context for AI
        context = "South African Economic Analysis - 15 Year Dataset (2010-2024)\n\n"
        context += "Current Economic Indicators:\n"
        
        for _, row in data_df.iterrows():
            context += f"- {row['indicator']}: {row['current_value']:.1f} "
            if pd.notna(row['year_over_year_change']):
                context += f"(YoY: {row['year_over_year_change']:+.1f}) "
            context += f"| {row['trend_direction']} | {row['executive_interpretation']}\n"
        
        prompt = f"""As a senior economic analyst, provide strategic insights on South Africa's economy based on this 15-year dataset:

{context}

Please provide:
1. Three key strategic concerns for policymakers
2. Two investment opportunities emerging from the data
3. One critical risk that requires immediate attention
4. Policy recommendations for the next 12 months

Keep responses concise and actionable for executive decision-making."""
        
        try:
            response = self.ai_model.generate_content(prompt)
            
            ai_insights_path = Path("analysis/AI_Enhanced_Economic_Insights.md")
            ai_insights_path.parent.mkdir(exist_ok=True)
            
            ai_report = f"""# 🤖 AI-Enhanced Economic Insights
**Generated:** {datetime.now().strftime("%B %d, %Y")}
**Model:** Gemini 2.5 Flash
**Data Source:** SARB 15-Year Economic Dataset (2010-2024)

---

## 🎯 Strategic Analysis

{response.text}

---

*AI Analysis based on 930+ economic data points spanning 15 years*
*Generated by SARB Economic Pipeline with Gemini 2.5 Flash*
"""
            
            with open(ai_insights_path, 'w', encoding='utf-8') as f:
                f.write(ai_report)
            
            print(f"✅ AI insights saved: {ai_insights_path}")
            return ai_insights_path
            
        except Exception as e:
            print(f"❌ AI insights generation failed: {e}")
            return None

def main():
    """Generate comprehensive economic reports"""
    
    print("🏛️ SARB ECONOMIC PIPELINE - COMPREHENSIVE REPORTING")
    print("=" * 70)
    
    # Initialize report generator
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    report_generator = SARBEconomicReportGenerator(gemini_api_key=gemini_api_key)
    
    # Generate executive summary report
    print("📊 Step 1: Generating Executive Summary Report...")
    executive_report = report_generator.generate_executive_summary_report()
    
    # Generate detailed charts
    print("📈 Step 2: Creating Detailed Visualization Charts...")
    charts_directory = report_generator.generate_detailed_charts()
    
    # Generate AI-enhanced insights
    print("🤖 Step 3: Creating AI-Enhanced Strategic Insights...")
    ai_insights = report_generator.generate_ai_enhanced_insights()
    
    print("\n🎉 COMPREHENSIVE REPORTING COMPLETE!")
    print("=" * 70)
    print(f"📋 Executive Report: {executive_report}")
    print(f"📈 Charts Directory: {charts_directory}")
    if ai_insights:
        print(f"🤖 AI Insights: {ai_insights}")
    print(f"📊 Data Source: 930+ records spanning 15 years (2010-2024)")
    print(f"🏗️ Architecture: 5 datasets, 14 tables, 4 analytical views")

if __name__ == "__main__":
    main()