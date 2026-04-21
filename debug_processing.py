#!/usr/bin/env python3
"""
Debug script to test individual processing steps
"""

import os
import sys
import time
from utils.ocr import extract_text
from utils.classifier import classify_document
from utils.extractors import extract_fields

def test_processing():
    print("🔍 Debug Processing Script")
    print("=" * 50)
    
    # Find most recent file in uploads
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ Uploads directory not found")
        return
    
    files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
    if not files:
        print("❌ No files found in uploads directory")
        return
    
    latest_file = sorted(files)[-1]
    file_path = os.path.join(uploads_dir, latest_file)
    
    print(f"📁 Testing file: {latest_file}")
    print(f"📍 Path: {file_path}")
    print(f"📏 Size: {os.path.getsize(file_path)} bytes")
    print()
    
    # Test 1: OCR
    print("1️⃣ Testing OCR...")
    start_time = time.time()
    try:
        text = extract_text(file_path)
        ocr_time = time.time() - start_time
        print(f"   ✅ OCR completed in {ocr_time:.2f}s")
        print(f"   📝 Text length: {len(text)} characters")
        print(f"   👀 Preview: {text[:200]}...")
    except Exception as e:
        print(f"   ❌ OCR failed: {e}")
        return
    
    print()
    
    # Test 2: Classification
    print("2️⃣ Testing Classification...")
    start_time = time.time()
    try:
        doc_type = classify_document(text)
        classification_time = time.time() - start_time
        print(f"   ✅ Classification completed in {classification_time:.2f}s")
        print(f"   📋 Document type: {doc_type}")
    except Exception as e:
        print(f"   ❌ Classification failed: {e}")
        return
    
    print()
    
    # Test 3: Extraction
    print("3️⃣ Testing Extraction...")
    start_time = time.time()
    try:
        extracted = extract_fields(text, doc_type)
        extraction_time = time.time() - start_time
        print(f"   ✅ Extraction completed in {extraction_time:.2f}s")
        print(f"   📊 Result: {extracted}")
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return
    
    print()
    print("🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_processing()
