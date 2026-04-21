#!/usr/bin/env python3
"""
Test Document Processing Agent with Created Test Documents
"""

import os
import json
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.document_agent import DocumentProcessingAgent

def test_document_processing():
    """Test document processing agent with various document types"""
    print("📄 Testing Document Processing Agent")
    print("=" * 50)
    
    try:
        agent = DocumentProcessingAgent()
        
        # Test files to process
        test_files = [
            ("Discharge Summary", "test_discharge.txt"),
            ("Final Bill", "test_bill.txt"),
            ("Claim Form", "test_claim.txt"),
            ("Radiology Report", "test_radiology.txt")
        ]
        
        results = []
        
        for doc_type, filename in test_files:
            print(f"\n🔍 Testing {doc_type}: {filename}")
            print("-" * 40)
            
            file_path = os.path.join("uploads", filename)
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                print("Run: python3 create_test_documents.py")
                continue
            
            # Create claim data for this document
            claim_data = {
                "claim_id": f"TEST_{doc_type.replace(' ', '_').upper()}",
                "documents": [
                    {
                        "file_name": filename,
                        "file_path": file_path,
                        "file_size": os.path.getsize(file_path)
                    }
                ]
            }
            
            print(f"📁 Processing: {filename}")
            
            # Process the document
            result = agent.process(claim_data)
            
            print(f"📊 Status: {result.status}")
            print(f"📈 Confidence: {result.confidence:.2f}")
            
            if result.status != "error":
                data = result.data
                if "documents" in data and data["documents"]:
                    doc = data["documents"][0]
                    print(f"🏷️  Classified as: {doc.get('document_type', 'Unknown')}")
                    print(f"📝 Text length: {doc.get('text_length', 0)}")
                    
                    # Show extracted fields summary
                    fields_str = doc.get("extracted_fields", "{}")
                    if isinstance(fields_str, str):
                        try:
                            fields = json.loads(fields_str)
                            field_count = len(fields)
                            print(f"📋 Fields extracted: {field_count}")
                            
                            # Show key fields
                            key_fields = ["Patient Name", "Age", "Hospital Name", "Diagnosis", "Amount"]
                            for field in key_fields:
                                value = fields.get(field, "Not Found")
                                print(f"   - {field}: {value}")
                        except json.JSONDecodeError:
                            print("📋 Fields: Invalid JSON")
                    else:
                        print(f"📋 Fields: {field_count}")
                
                if "summary" in data:
                    summary = data["summary"]
                    print(f"📈 Document Summary: {summary}")
                
                if "errors" in data and data["errors"]:
                    print(f"⚠️  Errors: {data['errors']}")
            else:
                print(f"❌ Error: {result.data.get('error', 'Unknown error')}")
            
            results.append({
                "document_type": doc_type,
                "filename": filename,
                "status": result.status,
                "confidence": result.confidence,
                "success": result.status != "error"
            })
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 DOCUMENT PROCESSING SUMMARY")
        print("=" * 50)
        
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_confidence = sum(r["confidence"] for r in results) / total if total > 0 else 0
        
        print(f"📈 Total Documents: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {total - successful}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"📈 Average Confidence: {avg_confidence:.2f}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['document_type']}: {result['status']} (Confidence: {result['confidence']:.2f})")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_documents():
    """Test processing multiple documents at once"""
    print("\n🔄 Testing Multiple Document Processing")
    print("-" * 40)
    
    try:
        agent = DocumentProcessingAgent()
        
        # Create claim with multiple documents
        claim_data = {
            "claim_id": "TEST_MULTIPLE_DOCS",
            "documents": [
                {
                    "file_name": "test_discharge.txt",
                    "file_path": os.path.join("uploads", "test_discharge.txt"),
                    "file_size": os.path.getsize(os.path.join("uploads", "test_discharge.txt"))
                },
                {
                    "file_name": "test_bill.txt",
                    "file_path": os.path.join("uploads", "test_bill.txt"),
                    "file_size": os.path.getsize(os.path.join("uploads", "test_bill.txt"))
                },
                {
                    "file_name": "test_claim.txt",
                    "file_path": os.path.join("uploads", "test_claim.txt"),
                    "file_size": os.path.getsize(os.path.join("uploads", "test_claim.txt"))
                }
            ]
        }
        
        print(f"📁 Processing {len(claim_data['documents'])} documents...")
        
        result = agent.process(claim_data)
        
        print(f"📊 Status: {result.status}")
        print(f"📈 Confidence: {result.confidence:.2f}")
        
        if result.status != "error":
            data = result.data
            if "summary" in data:
                summary = data["summary"]
                print(f"📈 Document Summary: {summary}")
            
            if "errors" in data and data["errors"]:
                print(f"⚠️  Errors: {data['errors']}")
            else:
                print("✅ All documents processed successfully")
        
        return result.status != "error"
        
    except Exception as e:
        print(f"❌ Multiple document test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run document processing tests"""
    print("🚀 Document Processing Agent Test Suite")
    print("=" * 60)
    
    # Check if test documents exist
    test_files = ["test_discharge.txt", "test_bill.txt", "test_claim.txt", "test_radiology.txt"]
    missing_files = [f for f in test_files if not os.path.exists(os.path.join("uploads", f))]
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        print("Run: python3 create_test_documents.py")
        return False
    
    # Run tests
    test_results = []
    
    # Test 1: Individual document processing
    test_results.append(("Individual Documents", test_document_processing()))
    
    # Test 2: Multiple document processing
    test_results.append(("Multiple Documents", test_multiple_documents()))
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🟢 DOCUMENT PROCESSING AGENT IS WORKING WELL")
        print("   Ready for end-to-end claim testing")
    elif success_rate >= 50:
        print("🟡 DOCUMENT PROCESSING AGENT HAS MINOR ISSUES")
        print("   Some documents processing, others failing")
    else:
        print("🔴 DOCUMENT PROCESSING AGENT NEEDS FIXES")
        print("   Major issues with document processing")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
