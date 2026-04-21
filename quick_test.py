#!/usr/bin/env python3
"""
Quick Test Script - Validate Complete System in 5 Minutes
"""

import os
import sys
import time
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ollama():
    """Test if Ollama is running"""
    print("🤖 Testing Ollama...")
    try:
        import ollama
        response = ollama.list()
        print("  ✅ Ollama is running")
        print(f"  Available models: {len(response.get('models', []))}")
        return True
    except Exception as e:
        print(f"  ❌ Ollama not running: {e}")
        print("  Start with: ollama serve")
        return False

def test_agents():
    """Test individual agents"""
    print("\n🤖 Testing Agents...")
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        orchestrator = ClaimOrchestratorAgent()
        print("  ✅ All agents initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Agent initialization failed: {e}")
        return False

def test_simple_claim():
    """Test a simple claim processing"""
    print("\n📋 Testing Simple Claim Processing...")
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        orchestrator = ClaimOrchestratorAgent()
        
        # Create minimal test claim
        claim_data = {
            "claim_id": "QUICK_TEST_001",
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
            },
            "claim_details": {
                "patient_name": "Test User",
                "age": 45,
                "gender": "Male",
                "hospital_name": "Test Hospital",
                "admission_date": "2024-03-15",
                "discharge_date": "2024-03-18",
                "diagnosis": "Test diagnosis",
                "procedure_performed": "Test procedure",
                "claimed_amount": 50000,
                "room_charges": 10000,
                "doctor_charges": 15000,
                "pharmacy_charges": 8000,
                "diagnostics_charges": 7000,
                "number_of_days": 3
            }
        }
        
        print("  🔄 Processing claim...")
        start_time = time.time()
        result = orchestrator.process(claim_data)
        processing_time = time.time() - start_time
        
        print(f"  ⏱️  Processing time: {processing_time:.2f}s")
        print(f"  📊 Status: {result.status}")
        print(f"  🎯 Decision: {result.data.get('final_decision', {}).get('decision', 'unknown')}")
        print(f"  💰 Payable Amount: {result.data.get('financial_calculation', {}).get('payable_amount', 0):.2f}")
        print(f"  📈 Confidence: {result.confidence:.2f}")
        
        # Check if processing was successful
        success = (
            result.status in ["approved", "needs_review", "rejected"] and
            processing_time < 60 and  # Should complete in under 60 seconds
            result.confidence > 0.5
        )
        
        if success:
            print("  ✅ Claim processing successful")
        else:
            print("  ❌ Claim processing has issues")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Claim processing failed: {e}")
        return False

def test_api():
    """Test API endpoints"""
    print("\n🌐 Testing API...")
    
    try:
        import requests
        
        # Test health check
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("  ✅ API health check passed")
        else:
            print(f"  ❌ API health check failed: {response.status_code}")
            return False
        
        # Test agent status
        response = requests.get("http://localhost:8001/agents/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agent_count = len(data)
            print(f"  ✅ Agent status endpoint working ({agent_count} agents)")
        else:
            print(f"  ❌ Agent status endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ❌ API not running")
        print("  Start with: python claim_adjudication_api.py")
        return False
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False

def create_test_file():
    """Create a test file for testing"""
    print("\n📄 Creating test file...")
    
    try:
        test_dir = "uploads"
        os.makedirs(test_dir, exist_ok=True)
        
        test_file = os.path.join(test_dir, "test_document.txt")
        with open(test_file, "w") as f:
            f.write("Test claim document content\n")
            f.write("Patient Name: Test User\n")
            f.write("Hospital: Test Hospital\n")
            f.write("Diagnosis: Test Diagnosis\n")
            f.write("Amount: 50000\n")
        
        print(f"  ✅ Test file created: {test_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Test file creation failed: {e}")
        return False

def main():
    """Run quick system test"""
    print("🚀 Quick System Test - Agentic AI Claim Adjudication")
    print("=" * 60)
    print("This test will validate the complete system in ~5 minutes")
    print()
    
    test_results = []
    
    # Test 1: Ollama
    test_results.append(("Ollama", test_ollama()))
    
    # Test 2: Create test file
    test_results.append(("Test File", create_test_file()))
    
    # Test 3: Agents
    test_results.append(("Agents", test_agents()))
    
    # Test 4: Simple claim processing
    test_results.append(("Claim Processing", test_simple_claim()))
    
    # Test 5: API (optional, may not be running)
    test_results.append(("API", test_api()))
    
    # Generate quick report
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🟢 SYSTEM IS WORKING WELL")
        print("   Ready for comprehensive testing")
    elif success_rate >= 60:
        print("🟡 SYSTEM HAS MINOR ISSUES")
        print("   Check failed tests above")
    else:
        print("🔴 SYSTEM HAS MAJOR ISSUES")
        print("   Review installation and dependencies")
    
    print("\n📋 Next Steps:")
    if success_rate >= 80:
        print("   1. Run comprehensive tests: python test_complete_system.py")
        print("   2. Test API endpoints: python test_api_endpoints.py")
        print("   3. Review TESTING_GUIDE.md for advanced testing")
    else:
        print("   1. Fix failed components")
        print("   2. Ensure Ollama is running: ollama serve")
        print("   3. Check agent imports and dependencies")
    
    print(f"\n💾 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
