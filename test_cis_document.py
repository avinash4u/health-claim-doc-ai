#!/usr/bin/env python3
"""
Test CIS document processing
"""

import os
import json
from utils.ocr import extract_text
from utils.classifier import classify_document
from utils.extractors import extract_fields

def test_cis_document():
    print("🔍 Testing CIS Document Processing")
    print("=" * 50)
    
    # Find CIS file
    uploads_dir = "uploads"
    files = [f for f in os.listdir(uploads_dir) if "CIS_4337667f" in f]
    if not files:
        print("❌ CIS file not found")
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
    print(text[:800] + "..." if len(text) > 800 else text)
    print()
    
    # Classify
    doc_type = classify_document(text)
    print(f"🏷️  Document Type: {doc_type}")
    print()
    
    # Extract fields
    try:
        extracted = extract_fields(text, doc_type)
        print(f"📊 Extraction Result Type: {type(extracted)}")
        
        # Try to parse as JSON
        if isinstance(extracted, str):
            try:
                parsed = json.loads(extracted)
                print("✅ Successfully parsed JSON:")
                
                # Check each field type
                for key, value in parsed.items():
                    print(f"   {key}: {value} (type: {type(value).__name__})")
                    
                    # Check if any field is not a string
                    if not isinstance(value, str):
                        print(f"      ⚠️  WARNING: {key} is not a string!")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"📝 Raw response: {extracted[:500]}...")
        else:
            print(f"📝 Raw extraction (not string): {extracted}")
            
    except Exception as e:
        print(f"❌ Extraction error: {e}")

if __name__ == "__main__":
    test_cis_document()
