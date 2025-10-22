#!/usr/bin/env python3
"""
Quick test to check if Vertex AI Gemini is accessible
"""

import os
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel

def test_vertex_ai():
    """Test Vertex AI access"""
    try:
        print("🧪 Testing Vertex AI Access...")
        
        # Initialize Vertex AI
        project_id = "brendon-presentation"
        location = "us-central1"
        
        print(f"📍 Project: {project_id}")
        print(f"📍 Location: {location}")
        
        vertexai.init(project=project_id, location=location)
        
        # Test model access
        model = GenerativeModel("gemini-1.5-flash-002")
        
        # Simple test prompt
        response = model.generate_content("Say 'Hello from Vertex AI!' if you can read this.")
        
        print("✅ SUCCESS! Vertex AI is working!")
        print(f"🤖 Model response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("💡 Vertex AI access may still be pending or needs API key fallback")
        return False

if __name__ == "__main__":
    test_vertex_ai()