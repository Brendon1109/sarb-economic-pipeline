@echo off
echo 🚀 UPLOADING SARB REPORTS TO GITHUB
echo ================================

echo 📂 Current directory: %cd%
dir

echo.
echo 🔗 Adding GitHub repository as remote...
git remote add origin https://github.com/Brendon1109/sarb-reports.git

echo.
echo 📤 Pushing files to GitHub...
git push -u origin main

echo.
echo ✅ UPLOAD COMPLETE!
echo.
echo 🌐 Your repository will be available at:
echo https://github.com/Brendon1109/sarb-reports
echo.
echo 📋 Enable GitHub Pages:
echo 1. Go to repository Settings
echo 2. Scroll to "Pages" section  
echo 3. Source: "Deploy from a branch"
echo 4. Branch: main
echo 5. Folder: / (root)
echo 6. Click Save
echo.
echo 🔗 Your Looker Studio URLs will be:
echo https://Brendon1109.github.io/sarb-reports/executive_summary_embed_embeddable.html
echo https://Brendon1109.github.io/sarb-reports/economic_alerts_embed_embeddable.html
echo https://Brendon1109.github.io/sarb-reports/sarb_correlation_analysis_embeddable.html
echo https://Brendon1109.github.io/sarb-reports/sarb_timeseries_chart_embeddable.html

pause