#!/usr/bin/env python3
"""
Simple Chart Viewer - View PNG charts using existing Python packages
No additional installations required!
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import os

def view_sarb_charts():
    """View SARB economic charts using matplotlib (already installed)"""
    
    print("📊 SARB ECONOMIC CHARTS VIEWER")
    print("=" * 40)
    
    charts_dir = Path("analysis/charts")
    
    if not charts_dir.exists():
        print(f"❌ Charts directory not found: {charts_dir}")
        return
    
    # Chart files to display
    chart_files = [
        ("Economic Indicators Time Series", "economic_indicators_timeseries.png"),
        ("Economic Cycles Comparison", "economic_cycles_comparison.png"), 
        ("Load Shedding Impact Analysis", "loadshedding_impact_analysis.png")
    ]
    
    # Check which charts exist
    available_charts = []
    for title, filename in chart_files:
        chart_path = charts_dir / filename
        if chart_path.exists():
            available_charts.append((title, chart_path))
            print(f"✅ Found: {filename}")
        else:
            print(f"❌ Missing: {filename}")
    
    if not available_charts:
        print("❌ No chart files found!")
        return
    
    # Display charts
    num_charts = len(available_charts)
    
    if num_charts == 1:
        # Single chart
        fig, ax = plt.subplots(figsize=(12, 8))
        title, chart_path = available_charts[0]
        img = mpimg.imread(str(chart_path))
        ax.imshow(img)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')
    
    elif num_charts == 2:
        # Two charts side by side
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        for i, (title, chart_path) in enumerate(available_charts):
            img = mpimg.imread(str(chart_path))
            axes[i].imshow(img)
            axes[i].set_title(title, fontsize=12, fontweight='bold')
            axes[i].axis('off')
    
    else:
        # Three or more charts
        fig, axes = plt.subplots(1, 3, figsize=(24, 8))
        for i, (title, chart_path) in enumerate(available_charts[:3]):
            img = mpimg.imread(str(chart_path))
            axes[i].imshow(img)
            axes[i].set_title(title, fontsize=10, fontweight='bold')
            axes[i].axis('off')
    
    fig.suptitle('SARB Economic Pipeline - Visual Analytics Dashboard', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    print(f"\\n🎯 Displayed {len(available_charts)} charts")
    print("💡 Charts are also available as individual PNG files in analysis/charts/")

def open_charts_folder():
    """Open the charts folder in Windows Explorer"""
    charts_dir = Path("analysis/charts").resolve()
    if charts_dir.exists():
        os.startfile(str(charts_dir))
        print(f"📁 Opened charts folder: {charts_dir}")
    else:
        print(f"❌ Charts folder not found: {charts_dir}")

def list_chart_info():
    """List information about available charts"""
    print("📋 CHART INFORMATION")
    print("=" * 30)
    
    charts_dir = Path("analysis/charts")
    chart_descriptions = {
        "economic_indicators_timeseries.png": {
            "title": "📈 Economic Indicators Time Series (2015-2024)",
            "description": "4-panel view showing GDP Growth, Inflation, Unemployment, and Prime Interest Rate trends over time",
            "use_case": "Trend analysis and correlation identification"
        },
        "economic_cycles_comparison.png": {
            "title": "🔄 Economic Cycles Comparison", 
            "description": "Bar chart comparing economic performance across 5 periods from 2010-2024",
            "use_case": "Period-by-period performance analysis"
        },
        "loadshedding_impact_analysis.png": {
            "title": "⚡ Load Shedding Impact Analysis (2019-2024)",
            "description": "Dual-panel analysis showing load shedding severity and correlation with Manufacturing PMI",
            "use_case": "Infrastructure crisis impact assessment"
        }
    }
    
    for filename, info in chart_descriptions.items():
        chart_path = charts_dir / filename
        if chart_path.exists():
            file_size = chart_path.stat().st_size / 1024  # KB
            print(f"\\n{info['title']}")
            print(f"   📄 File: {filename}")
            print(f"   📊 Description: {info['description']}")
            print(f"   🎯 Use Case: {info['use_case']}")
            print(f"   💾 Size: {file_size:.1f} KB")
            print(f"   ✅ Status: Available")
        else:
            print(f"\\n{info['title']}")
            print(f"   ❌ Status: Missing")

def main():
    """Main menu for chart viewing options"""
    print("🏛️ SARB ECONOMIC PIPELINE - CHART VIEWER")
    print("=" * 50)
    print("Choose an option:")
    print("1. 🖼️  View all charts in Python")
    print("2. 📁 Open charts folder in Explorer") 
    print("3. 📋 List chart information")
    print("4. 🌐 Show Looker Studio guide")
    print("0. ❌ Exit")
    
    while True:
        choice = input("\\nEnter your choice (0-4): ").strip()
        
        if choice == "1":
            view_sarb_charts()
            break
        elif choice == "2":
            open_charts_folder()
            break
        elif choice == "3":
            list_chart_info()
            break
        elif choice == "4":
            print("\\n🌐 LOOKER STUDIO GUIDE:")
            print("📋 Check the file: LOOKER_STUDIO_SETUP.md")
            print("🔗 Direct link: https://lookerstudio.google.com/")
            print("📊 Connect to: brendon-presentation.sarb_gold_reporting.comprehensive_economic_history")
            break
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 0-4.")

if __name__ == "__main__":
    main()