#!/usr/bin/env python3
"""
SARB Economic Pipeline - Interactive Chart Viewer
View and interact with economic charts in Python
"""

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import pandas as pd
from google.cloud import bigquery
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Note: streamlit import moved to function level to avoid dependency issues

class SARBChartViewer:
    """Interactive chart viewer for SARB economic data"""
    
    def __init__(self, project_id='brendon-presentation'):
        self.project_id = project_id
        self.bigquery_client = bigquery.Client(project=self.project_id)
        self.charts_dir = Path("analysis/charts")
    
    def display_static_charts(self):
        """Display the generated PNG charts in Python"""
        
        print("📊 DISPLAYING SARB ECONOMIC CHARTS")
        print("=" * 50)
        
        # Define chart files
        chart_files = [
            ("Economic Indicators Time Series (2015-2024)", "economic_indicators_timeseries.png"),
            ("Economic Cycles Comparison", "economic_cycles_comparison.png"),
            ("Load Shedding Impact Analysis", "loadshedding_impact_analysis.png")
        ]
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('SARB Economic Pipeline - Visual Analytics Dashboard', fontsize=16, fontweight='bold')
        
        for i, (title, filename) in enumerate(chart_files):
            chart_path = self.charts_dir / filename
            
            if chart_path.exists():
                img = mpimg.imread(chart_path)
                axes[i].imshow(img)
                axes[i].set_title(title, fontsize=10, fontweight='bold')
                axes[i].axis('off')
                print(f"✅ Loaded: {filename}")
            else:
                axes[i].text(0.5, 0.5, f'Chart not found:\n{filename}', 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(title, fontsize=10)
                print(f"❌ Missing: {filename}")
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def create_interactive_plotly_charts(self):
        """Create interactive Plotly charts from BigQuery data"""
        
        print("\n🎯 CREATING INTERACTIVE PLOTLY CHARTS")
        print("=" * 50)
        
        # 1. Interactive Economic Indicators Time Series
        print("📈 Creating interactive time series...")
        timeseries_fig = self._create_interactive_timeseries()
        
        # 2. Interactive Economic Cycles
        print("🔄 Creating interactive cycles comparison...")
        cycles_fig = self._create_interactive_cycles()
        
        # 3. Interactive Load Shedding Analysis
        print("⚡ Creating interactive load shedding analysis...")
        loadshedding_fig = self._create_interactive_loadshedding()
        
        return timeseries_fig, cycles_fig, loadshedding_fig
    
    def _create_interactive_timeseries(self):
        """Create interactive time series with Plotly"""
        
        query = """
        SELECT 
            date,
            indicator,
            value,
            economic_period,
            trend_direction
        FROM `brendon-presentation.sarb_gold_reporting.comprehensive_economic_history`
        WHERE indicator IN ('GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate', 'Prime_Interest_Rate')
        AND date >= '2015-01-01'
        ORDER BY date, indicator
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        df['date'] = pd.to_datetime(df['date'])
        
        # Create subplot figure
        indicators = ['GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate', 'Prime_Interest_Rate']
        titles = ['GDP Growth Rate (%)', 'Inflation Rate (%)', 'Unemployment Rate (%)', 'Prime Interest Rate (%)']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=titles,
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        colors = ['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c']
        
        for i, (indicator, title, color) in enumerate(zip(indicators, titles, colors)):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            indicator_data = df[df['indicator'] == indicator]
            
            if not indicator_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=indicator_data['date'],
                        y=indicator_data['value'],
                        mode='lines+markers',
                        name=indicator.replace('_', ' '),
                        line=dict(color=color, width=2),
                        marker=dict(size=4),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                    'Date: %{x}<br>' +
                                    'Value: %{y:.1f}%<br>' +
                                    '<extra></extra>'
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            title_text="SARB Economic Indicators - Interactive Dashboard (2015-2024)",
            title_x=0.5,
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Percentage (%)")
        
        return fig
    
    def _create_interactive_cycles(self):
        """Create interactive economic cycles chart"""
        
        query = """
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
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        if df.empty:
            return None
        
        # Create grouped bar chart
        fig = go.Figure()
        
        metrics = ['avg_gdp_growth', 'avg_inflation', 'avg_unemployment', 'avg_prime_rate']
        metric_names = ['GDP Growth', 'Inflation', 'Unemployment', 'Prime Rate']
        colors = ['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c']
        
        for metric, name, color in zip(metrics, metric_names, colors):
            fig.add_trace(go.Bar(
                name=name,
                x=df['economic_period'],
                y=df[metric],
                marker_color=color,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Period: %{x}<br>' +
                             'Value: %{y:.1f}%<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            title='Economic Performance by Period (2010-2024)',
            title_x=0.5,
            xaxis_title='Economic Period',
            yaxis_title='Rate (%)',
            barmode='group',
            height=500,
            hovermode='x unified'
        )
        
        # Add performance rating annotations
        for i, row in df.iterrows():
            rating_color = {
                'HIGH_PERFORMANCE': 'green',
                'MODERATE_PERFORMANCE': 'orange',
                'CHALLENGING_PERFORMANCE': 'red'
            }.get(row['period_performance_rating'], 'gray')
            
            fig.add_annotation(
                x=i,
                y=max(row[metrics]) + 2,
                text=f"🔸 {row['period_performance_rating']}",
                showarrow=False,
                font=dict(color=rating_color, size=10)
            )
        
        return fig
    
    def _create_interactive_loadshedding(self):
        """Create interactive load shedding analysis"""
        
        query = """
        SELECT 
            year,
            month,
            loadshedding_hours,
            manufacturing_pmi,
            loadshedding_severity,
            seasonal_pattern
        FROM `brendon-presentation.sarb_gold_reporting.load_shedding_impact_analysis`
        WHERE year >= 2019
        ORDER BY year, month
        """
        
        df = self.bigquery_client.query(query).to_dataframe()
        
        if df.empty:
            return None
        
        # Create date column
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Load Shedding Hours by Severity', 'Manufacturing PMI vs Load Shedding Correlation'],
            vertical_spacing=0.1
        )
        
        # Plot 1: Load shedding over time
        severity_colors = {'LOW_IMPACT': 'green', 'MODERATE_IMPACT': 'orange', 'HIGH_IMPACT': 'red'}
        
        for severity in df['loadshedding_severity'].unique():
            severity_data = df[df['loadshedding_severity'] == severity]
            fig.add_trace(
                go.Scatter(
                    x=severity_data['date'],
                    y=severity_data['loadshedding_hours'],
                    mode='markers',
                    name=severity,
                    marker=dict(
                        color=severity_colors.get(severity, 'gray'),
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 'Hours: %{y}<br>' +
                                 '<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Plot 2: PMI correlation
        fig.add_trace(
            go.Scatter(
                x=df['loadshedding_hours'],
                y=df['manufacturing_pmi'],
                mode='markers',
                name='PMI vs Load Shedding',
                marker=dict(color='steelblue', size=6, opacity=0.6),
                hovertemplate='Load Shedding: %{x} hours<br>' +
                             'PMI: %{y}<br>' +
                             '<extra></extra>',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Add PMI 50 line (expansion/contraction threshold)
        fig.add_hline(y=50, line_dash="dash", line_color="red", 
                     annotation_text="PMI 50 (Expansion/Contraction)", row=2, col=1)
        
        fig.update_layout(
            title='Load Shedding Impact Analysis (2019-2024)',
            title_x=0.5,
            height=700
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Load Shedding Hours", row=2, col=1)
        fig.update_yaxes(title_text="Hours per Month", row=1, col=1)
        fig.update_yaxes(title_text="Manufacturing PMI", row=2, col=1)
        
        return fig
    
    def save_interactive_charts(self, timeseries_fig, cycles_fig, loadshedding_fig):
        """Save interactive charts as HTML files"""
        
        print("\n💾 SAVING INTERACTIVE CHARTS")
        print("=" * 40)
        
        # Create interactive charts directory
        interactive_dir = Path("analysis/interactive_charts")
        interactive_dir.mkdir(exist_ok=True)
        
        if timeseries_fig:
            timeseries_path = interactive_dir / "interactive_economic_indicators.html"
            timeseries_fig.write_html(timeseries_path)
            print(f"✅ Saved: {timeseries_path}")
        
        if cycles_fig:
            cycles_path = interactive_dir / "interactive_economic_cycles.html"
            cycles_fig.write_html(cycles_path)
            print(f"✅ Saved: {cycles_path}")
        
        if loadshedding_fig:
            loadshedding_path = interactive_dir / "interactive_loadshedding_analysis.html"
            loadshedding_fig.write_html(loadshedding_path)
            print(f"✅ Saved: {loadshedding_path}")
        
        print(f"\n🌐 Interactive charts available at: {interactive_dir}")
        return interactive_dir

def create_streamlit_dashboard():
    """Create Streamlit dashboard code for interactive viewing"""
    
    streamlit_code = '''
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="SARB Economic Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# Dashboard header
st.title("🏛️ SARB Economic Pipeline - Interactive Dashboard")
st.markdown("**15-Year Economic Analysis (2010-2024) | 930+ Data Points**")

# Sidebar for navigation
st.sidebar.title("📊 Navigation")
view_option = st.sidebar.selectbox(
    "Select View:",
    ["📈 Economic Indicators", "🔄 Economic Cycles", "⚡ Load Shedding Impact", "📋 Static Charts"]
)

# Load and display charts based on selection
if view_option == "📈 Economic Indicators":
    st.header("📈 Economic Indicators Time Series")
    
    # Load interactive chart
    chart_path = Path("analysis/interactive_charts/interactive_economic_indicators.html")
    if chart_path.exists():
        with open(chart_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600)
    else:
        st.error("Interactive chart not found. Please run the chart generator first.")

elif view_option == "🔄 Economic Cycles":
    st.header("🔄 Economic Cycles Analysis")
    
    chart_path = Path("analysis/interactive_charts/interactive_economic_cycles.html")
    if chart_path.exists():
        with open(chart_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=500)
    else:
        st.error("Interactive chart not found. Please run the chart generator first.")

elif view_option == "⚡ Load Shedding Impact":
    st.header("⚡ Load Shedding Impact Analysis")
    
    chart_path = Path("analysis/interactive_charts/interactive_loadshedding_analysis.html")
    if chart_path.exists():
        with open(chart_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=700)
    else:
        st.error("Interactive chart not found. Please run the chart generator first.")

elif view_option == "📋 Static Charts":
    st.header("📋 Static Chart Gallery")
    
    # Display static PNG charts
    charts_dir = Path("analysis/charts")
    chart_files = [
        ("Economic Indicators Time Series", "economic_indicators_timeseries.png"),
        ("Economic Cycles Comparison", "economic_cycles_comparison.png"),
        ("Load Shedding Impact Analysis", "loadshedding_impact_analysis.png")
    ]
    
    for title, filename in chart_files:
        chart_path = charts_dir / filename
        if chart_path.exists():
            st.subheader(title)
            st.image(str(chart_path), use_column_width=True)
        else:
            st.error(f"Chart not found: {filename}")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Info")
st.sidebar.markdown("**Period:** 2010-2024")
st.sidebar.markdown("**Records:** 930+")
st.sidebar.markdown("**Indicators:** 7 major")
st.sidebar.markdown("**Architecture:** Medallion (Bronze→Silver→Gold)")
'''
    
    # Save Streamlit app
    streamlit_path = Path("analysis/streamlit_dashboard.py")
    with open(streamlit_path, 'w', encoding='utf-8') as f:
        f.write(streamlit_code)
    
    print(f"✅ Streamlit dashboard created: {streamlit_path}")
    print("🚀 To run: streamlit run analysis/streamlit_dashboard.py")
    
    return streamlit_path

def main():
    """Main function to demonstrate all chart viewing options"""
    
    print("🎯 SARB ECONOMIC CHARTS - MULTIPLE VIEWING OPTIONS")
    print("=" * 60)
    
    # Initialize chart viewer
    viewer = SARBChartViewer()
    
    # Option 1: Display static charts in Python
    print("\\n1️⃣ DISPLAYING STATIC CHARTS IN PYTHON")
    static_fig = viewer.display_static_charts()
    
    # Option 2: Create interactive Plotly charts
    print("\\n2️⃣ CREATING INTERACTIVE PLOTLY CHARTS")
    timeseries_fig, cycles_fig, loadshedding_fig = viewer.create_interactive_plotly_charts()
    
    # Save interactive charts
    interactive_dir = viewer.save_interactive_charts(timeseries_fig, cycles_fig, loadshedding_fig)
    
    # Option 3: Create Streamlit dashboard
    print("\\n3️⃣ CREATING STREAMLIT DASHBOARD")
    streamlit_path = create_streamlit_dashboard()
    
    print("\\n🎉 ALL CHART VIEWING OPTIONS READY!")
    print("=" * 60)
    print("📁 Static Charts: analysis/charts/")
    print("🌐 Interactive Charts: analysis/interactive_charts/")
    print("🚀 Streamlit Dashboard: analysis/streamlit_dashboard.py")
    print("\\n🔧 Usage Options:")
    print("   • Python: Run this script to view in matplotlib/plotly")
    print("   • Browser: Open HTML files in analysis/interactive_charts/")
    print("   • Streamlit: streamlit run analysis/streamlit_dashboard.py")
    print("   • Looker Studio: Connect to BigQuery views for live dashboards")

if __name__ == "__main__":
    main()