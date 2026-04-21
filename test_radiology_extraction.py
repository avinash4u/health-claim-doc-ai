#!/usr/bin/env python3
"""
Test radiology report extraction
"""

import os
import json
from utils.ocr import extract_text
from utils.classifier import classify_document
from utils.extractors import extract_fields

def test_radiology_extraction():
    print("🔍 Testing Radiology Report Extraction")
    print("=" * 50)
    
    # Use our created test radiology file
    test_file = "test_radiology.txt"
    uploads_dir = "uploads"
    file_path = os.path.join(uploads_dir, test_file)
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        print("Run: python3 create_test_documents.py")
        return
    
    print(f"📁 File: {test_file}")
    print(f"📍 Path: {file_path}")
    print(f"📏 Size: {os.path.getsize(file_path)} bytes")
    print()
    
    # Extract text
    text = extract_text(file_path)
    print(f"📝 Text length: {len(text)} characters")
    print()
    
    # Classify
    doc_type = classify_document(text)
    print(f"🏷️  Document Type: {doc_type}")
    print()
    
    # Extract fields
    try:
        extracted = extract_fields(text, doc_type)
        print(f"📊 Raw Extraction Result:")
        print(extracted)
        print()
        
        # Try to parse as JSON
        try:
            if isinstance(extracted, str):
                parsed = json.loads(extracted)
            else:
                parsed = extracted
            
            print("✅ Successfully parsed JSON:")
            for key, value in parsed.items():
                print(f"   {key}: {value}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("📝 Raw response preview:")
            print(str(extracted)[:500] + "..." if len(str(extracted)) > 500 else str(extracted))
            
    except Exception as e:
        print(f"❌ Extraction error: {e}")

if __name__ == "__main__":
    test_radiology_extraction()
