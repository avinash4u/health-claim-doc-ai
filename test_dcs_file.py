#!/usr/bin/env python3
"""
Test the specific DCS file classification
"""

import os
from utils.ocr import extract_text
from utils.classifier import classify_document

def test_dcs_file():
    print("🔍 Testing DCS File Classification")
    print("=" * 50)
    
    # Find the specific DCS file
    uploads_dir = "uploads"
    files = [f for f in os.listdir(uploads_dir) if f.startswith("69fc0a79") and "DCS_afecaa69" in f]
    if not files:
        print("❌ DCS file not found")
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
    
    # Classify
    try:
        doc_type = classify_document(text)
        print(f"🏆 Classification: {doc_type}")
        
        if doc_type == "Discharge Summary":
            print("✅ SUCCESS: Correctly classified as Discharge Summary")
        elif doc_type == "Final Bill":
            print("❌ ISSUE: Incorrectly classified as Final Bill")
        else:
            print(f"⚠️  OTHER: Classified as {doc_type}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_dcs_file()
