#!/usr/bin/env python3
"""
🔗 Generate Correct URLs for Looker Studio Embedding
"""

def convert_drive_url_for_embedding(drive_url):
    """Convert Google Drive URL to embeddable format"""
    # Extract file ID from the URL
    if "drive.google.com/file/d/" in drive_url:
        file_id = drive_url.split("/file/d/")[1].split("/")[0]
        # Return the embeddable URL format
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return drive_url

def main():
    print("🔗 LOOKER STUDIO URL CONVERTER")
    print("=" * 50)
    
    print("\n📋 Step 1: Upload your HTML files to Google Drive")
    print("   • executive_summary_embed.html")
    print("   • economic_alerts_embed.html")
    print("   • Set sharing to 'Anyone with link can view'")
    
    print("\n📋 Step 2: Get the shareable links from Google Drive")
    print("   Right-click file → 'Get link' → Copy")
    
    print("\n📋 Step 3: Convert URLs for Looker Studio")
    
    while True:
        url = input("\nPaste Google Drive URL (or 'done' to finish): ").strip()
        if url.lower() == 'done':
            break
        if url:
            embeddable_url = convert_drive_url_for_embedding(url)
            print(f"✅ Embeddable URL: {embeddable_url}")
            print("   👆 Use this URL in Looker Studio 'External Content URL' field")
    
    print("\n🎯 Alternative: Use Custom HTML Method")
    print("   Instead of URL embedding, try:")
    print("   1. Add Component → Embed")
    print("   2. Select 'Custom HTML'")
    print("   3. Copy-paste HTML content directly")
    
    print("\n📁 HTML Files Location:")
    print("   • analysis/reports/executive_summary_embed.html")
    print("   • analysis/reports/economic_alerts_embed.html")

if __name__ == "__main__":
    main()