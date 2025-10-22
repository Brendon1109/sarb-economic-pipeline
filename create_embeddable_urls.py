#!/usr/bin/env python3
"""
🔗 Convert HTML Reports to Embeddable URLs for Looker Studio
Creates web-hosted versions of HTML reports with direct embeddable URLs
"""

import os
import shutil
import json
from datetime import datetime

class HTMLToEmbeddableURL:
    def __init__(self):
        self.reports_dir = "analysis/reports"
        self.output_dir = "analysis/embeddable_reports"
        self.urls_file = "analysis/embeddable_urls.json"
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Created directory: {self.output_dir}")
    
    def create_simple_hosting_files(self):
        """Create files optimized for simple hosting services"""
        hosting_urls = {}
        
        # Find all HTML files in reports directory
        html_files = [f for f in os.listdir(self.reports_dir) if f.endswith('.html')]
        
        print(f"\n🔍 Found {len(html_files)} HTML files to convert:")
        
        for html_file in html_files:
            source_path = os.path.join(self.reports_dir, html_file)
            
            # Create optimized version for hosting
            optimized_content = self.optimize_html_for_embedding(source_path)
            
            # Create embeddable version
            base_name = html_file.replace('.html', '')
            embeddable_filename = f"{base_name}_embeddable.html"
            embeddable_path = os.path.join(self.output_dir, embeddable_filename)
            
            with open(embeddable_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            print(f"   ✅ {html_file} → {embeddable_filename}")
            
            # Store placeholder URL (to be replaced with actual hosting URL)
            hosting_urls[base_name] = {
                "filename": embeddable_filename,
                "local_path": embeddable_path,
                "placeholder_url": f"https://YOUR-HOSTING-SERVICE.com/{embeddable_filename}",
                "description": self.get_file_description(base_name)
            }
        
        return hosting_urls
    
    def optimize_html_for_embedding(self, file_path):
        """Optimize HTML for embedding in Looker Studio"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add responsive meta tags and optimize for embedding
        optimized_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SARB Economic Report</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: transparent;
        }}
        .container {{
            width: 100%;
            max-width: 100%;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
        return optimized_html
    
    def get_file_description(self, base_name):
        """Get description for each file type"""
        descriptions = {
            "executive_summary_embed": "Executive Economic Summary with AI insights",
            "economic_alerts_embed": "Real-time Economic Alerts and Indicators",
            "sarb_correlation_analysis": "Economic Correlation Analysis Charts",
            "sarb_timeseries_chart": "Time Series Economic Data Visualization"
        }
        return descriptions.get(base_name, "SARB Economic Report")
    
    def create_github_pages_setup(self, hosting_urls):
        """Create setup for GitHub Pages hosting"""
        
        # Create index.html for GitHub Pages
        index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SARB Economic Reports</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .report-link { 
            display: block; 
            padding: 10px; 
            margin: 10px 0; 
            background: #f0f0f0; 
            text-decoration: none; 
            border-radius: 5px; 
        }
    </style>
</head>
<body>
    <h1>🏛️ SARB Economic Reports</h1>
    <p>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
"""
        
        for key, info in hosting_urls.items():
            index_content += f"""
    <a href="{info['filename']}" class="report-link">
        📊 {info['description']}
    </a>"""
        
        index_content += """
</body>
</html>"""
        
        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"   📄 Created index.html for GitHub Pages")
    
    def generate_hosting_instructions(self, hosting_urls):
        """Generate instructions for different hosting options"""
        
        instructions = f"""
# 🔗 HTML Reports to Embeddable URLs

## 📁 Generated Files
Your HTML reports have been optimized and saved to: `{self.output_dir}/`

"""
        
        for key, info in hosting_urls.items():
            instructions += f"- **{info['description']}**: `{info['filename']}`\n"
        
        instructions += """

## 🌐 Hosting Options

### Option 1: GitHub Pages (Recommended - Free)

1. **Create a new GitHub repository:**
   ```
   Repository name: sarb-reports
   Make it public
   ```

2. **Upload files:**
   ```
   Upload all files from analysis/embeddable_reports/ to the repository
   ```

3. **Enable GitHub Pages:**
   ```
   Settings → Pages → Source: Deploy from a branch → main → / (root)
   ```

4. **Your URLs will be:**
   ```"""
        
        for key, info in hosting_urls.items():
            instructions += f"""
   https://YOUR-USERNAME.github.io/sarb-reports/{info['filename']}"""
        
        instructions += """
   ```

### Option 2: Netlify (Free hosting)

1. **Go to:** https://www.netlify.com/
2. **Drag and drop** the `embeddable_reports` folder
3. **Get URLs:** https://YOUR-SITE.netlify.app/filename.html

### Option 3: Vercel (Free hosting)

1. **Go to:** https://vercel.com/
2. **Import** the `embeddable_reports` folder
3. **Get URLs:** https://YOUR-SITE.vercel.app/filename.html

## 🔗 Using in Looker Studio

1. **Add Component** → "Embed"
2. **Select** "URL Embed" 
3. **Paste** the hosted URL
4. **Adjust** size and positioning

## 📊 Example URLs for Looker Studio:
"""
        
        for key, info in hosting_urls.items():
            instructions += f"""
**{info['description']}:**
```
https://YOUR-HOSTING-SERVICE.com/{info['filename']}
```
"""
        
        return instructions
    
    def save_configuration(self, hosting_urls, instructions):
        """Save configuration and instructions"""
        
        # Save URLs configuration
        config = {
            "generated_date": datetime.now().isoformat(),
            "reports": hosting_urls,
            "instructions": "See EMBEDDABLE_URLS_GUIDE.md for setup instructions"
        }
        
        with open(self.urls_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Save instructions
        with open("analysis/EMBEDDABLE_URLS_GUIDE.md", 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"💾 Configuration saved: {self.urls_file}")
        print(f"📖 Instructions saved: analysis/EMBEDDABLE_URLS_GUIDE.md")
    
    def run(self):
        """Main execution function"""
        print("🔗 CONVERTING HTML REPORTS TO EMBEDDABLE URLS")
        print("=" * 60)
        
        # Setup
        self.setup_directories()
        
        # Process HTML files
        hosting_urls = self.create_simple_hosting_files()
        
        # Create GitHub Pages setup
        self.create_github_pages_setup(hosting_urls)
        
        # Generate instructions
        instructions = self.generate_hosting_instructions(hosting_urls)
        
        # Save everything
        self.save_configuration(hosting_urls, instructions)
        
        print(f"\n🎉 CONVERSION COMPLETE!")
        print("=" * 60)
        print(f"📁 Embeddable files: {self.output_dir}/")
        print(f"📖 Setup guide: analysis/EMBEDDABLE_URLS_GUIDE.md")
        print(f"💾 Configuration: {self.urls_file}")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Choose a hosting service (GitHub Pages recommended)")
        print(f"2. Upload files from {self.output_dir}/")
        print(f"3. Get the hosted URLs")
        print(f"4. Use URLs in Looker Studio embed components")
        
        return hosting_urls

def main():
    converter = HTMLToEmbeddableURL()
    urls = converter.run()
    
    print(f"\n📋 Files ready for hosting:")
    for key, info in urls.items():
        print(f"   📊 {info['description']}")
        print(f"      File: {info['filename']}")
        print(f"      URL Pattern: https://YOUR-HOST.com/{info['filename']}")
        print()

if __name__ == "__main__":
    main()