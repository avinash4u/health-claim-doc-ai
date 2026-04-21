#!/usr/bin/env python3
"""
Health Claim Document Intelligence - Startup Script
"""

import uvicorn
import os
import sys

def main():
    print("🏥 Health Claim Document Intelligence System")
    print("=" * 50)
    print("Starting server with the following features:")
    print("✅ Document Upload & Processing")
    print("✅ AI-Powered Classification (Ollama)")
    print("✅ Field Extraction")
    print("✅ Fraud Detection")
    print("✅ Readability Analysis")
    print("✅ Modern Web UI")
    print("=" * 50)
    
    # Check if Ollama is available
    try:
        import ollama
        models = ollama.list()
        print(f"🤖 Ollama connected - Available models: {len(models['models'])}")
    except Exception as e:
        print("❌ Ollama not available. Please ensure Ollama is running:")
        print("   - Install: brew install ollama")
        print("   - Start: ollama serve")
        print("   - Pull model: ollama pull mistral")
        sys.exit(1)
    
    # Check if upload directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        print("📁 Created uploads directory")
    
    # Start server
    print("\n🚀 Starting server on http://localhost:8000")
    print("📱 Web UI will be available at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
