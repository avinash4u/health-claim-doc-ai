#!/usr/bin/env python3
"""
Debug Document Processing Issue
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_document_agent():
    """Test document agent in isolation"""
    print("🔍 Testing Document Agent in Isolation")
    print("-" * 40)
    
    try:
        from agents.document_agent import DocumentProcessingAgent
        
        agent = DocumentProcessingAgent()
        
        # Create simple test claim
        claim_data = {
            "claim_id": "DEBUG_TEST_001",
            "documents": [
                {
                    "file_name": "test_document.txt",
                    "file_path": "uploads/test_document.txt",
                    "file_size": 1000
                }
            ]
        }
        
        print(f"📋 Input claim data: {claim_data}")
        print()
        
        # Process documents
        result = agent.process(claim_data)
        
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result status: {result.status}")
        print(f"📊 Result confidence: {result.confidence}")
        print(f"📊 Result data type: {type(result.data)}")
        print(f"📊 Result data: {result.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document agent error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test orchestrator with minimal data"""
    print("\n🤖 Testing Orchestrator")
    print("-" * 40)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        orchestrator = ClaimOrchestratorAgent()
        
        # Create minimal test claim
        claim_data = {
            "claim_id": "DEBUG_TEST_002",
            "documents": [
                {
                    "file_name": "test_document.txt",
                    "file_path": "uploads/test_document.txt",
                    "file_size": 1000
                }
            ],
            "policy_details": {
                "policy_number": "POL123456",
                "policy_holder_name": "Test User",
                "sum_insured": 500000,
                "start_date": "2023-01-01",
                "end_date": "2024-12-31",
                "policy_type": "individual",
                "premium_status": "paid",
                "status": "active",
                "waiting_periods": {},
                "exclusions": [],
                "room_rent_limit": 5000,
                "co_payment_percentage": 20,
                "deductible_amount": 10000,
                "remaining_sum_insured": 400000
            }
        }
        
        print(f"📋 Input claim data: {claim_data}")
        print()
        
        # Process through orchestrator
        result = orchestrator.process(claim_data)
        
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result status: {result.status}")
        print(f"📊 Result confidence: {result.confidence}")
        print(f"📊 Result data: {result.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug tests"""
    print("🐛 Debug Document Processing Issues")
    print("=" * 50)
    
    # Create test file first
    print("📄 Creating test file...")
    os.makedirs("uploads", exist_ok=True)
    
    with open("uploads/test_document.txt", "w") as f:
        f.write("Test claim document content\n")
        f.write("Patient Name: Test User\n")
        f.write("Hospital: Test Hospital\n")
        f.write("Diagnosis: Test Diagnosis\n")
        f.write("Amount: 50000\n")
    
    print("✅ Test file created")
    print()
    
    # Test document agent
    doc_success = test_document_agent()
    
    # Test orchestrator
    orch_success = test_orchestrator()
    
    print("\n" + "=" * 50)
    print("📊 DEBUG RESULTS")
    print("=" * 50)
    print(f"Document Agent: {'✅ PASS' if doc_success else '❌ FAIL'}")
    print(f"Orchestrator: {'✅ PASS' if orch_success else '❌ FAIL'}")
    
    if doc_success and orch_success:
        print("🟢 Both components working correctly")
    else:
        print("🔴 Issues found - see above for details")

if __name__ == "__main__":
    main()
