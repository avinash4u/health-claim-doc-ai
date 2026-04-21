#!/usr/bin/env python3
"""
Test PPC file classification
"""

import os
from utils.ocr import extract_text
from utils.classifier import classify_document

def test_ppc_classification():
    print("🔍 Testing PPC File Classification")
    print("=" * 50)
    
    # Find PPC file
    uploads_dir = "uploads"
    files = [f for f in os.listdir(uploads_dir) if "PPC_ff3b5bb4" in f]
    if not files:
        print("❌ PPC file not found")
        return
    
    file = files[0]
    file_path = os.path.join(uploads_dir, file)
    
    print(f"📁 File: {file}")
    print(f"📍 Path: {file_path}")
    print(f"📏 Size: {os.path.getsize(file_path)} bytes")
    print()
    
    # Extract text
    text = extract_text(file_path)
    print(f"📝 Text length: {len(text)} characters")
    print()
    
    # Show text preview
    print("📝 Text Preview:")
    print(text[:1000] + "..." if len(text) > 1000 else text)
    print()
    
    # Classify
    try:
        doc_type = classify_document(text)
        print(f"🏷️  Document Type: {doc_type}")
        
        if doc_type == "Cashless Authorization Letter":
            print("✅ SUCCESS: Correctly classified as Cashless Authorization Letter")
        elif doc_type == "Discharge Summary":
            print("❌ ISSUE: Incorrectly classified as Discharge Summary")
        else:
            print(f"⚠️  OTHER: Classified as {doc_type}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_ppc_classification()
