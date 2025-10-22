#!/usr/bin/env python3
"""
Quick test for Gemini API key
"""

import os
import google.generativeai as genai

def test_gemini_api():
    """Test Gemini API with your key"""
    
    # Get API key from environment or prompt
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("🔑 Please set your Gemini API key:")
        print("$env:GEMINI_API_KEY=\"your-api-key-here\"")
        print("Then run this script again.")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content("Say 'Hello from Gemini API!' if you can read this.")
        
        print("✅ SUCCESS! Gemini API is working!")
        print(f"🤖 Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_api()