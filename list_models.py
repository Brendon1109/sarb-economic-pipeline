#!/usr/bin/env python3
"""
Check available Gemini models
"""

import os
import google.generativeai as genai

def list_available_models():
    """List available models for the API key"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("🔑 No API key found")
        return
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        models = genai.list_models()
        
        print("📋 Available Gemini models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    list_available_models()