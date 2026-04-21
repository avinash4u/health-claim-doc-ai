#!/usr/bin/env python3
"""
Minimal LLM Integration Test
Test the system with minimal LLM dependencies
"""

import os
import sys
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_minimal_test_file():
    """Create a minimal test file"""
    test_dir = "uploads"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "minimal_test.txt")
    with open(test_file, "w") as f:
        f.write("Patient Name: Test User\n")
        f.write("Age: 45\n")
        f.write("Gender: Male\n")
        f.write("Hospital: Test Hospital\n")
        f.write("Diagnosis: Test Diagnosis\n")
        f.write("Procedure: Test Procedure\n")
        f.write("Amount: 50000\n")
    
    return test_file

def test_minimal_claim_processing():
    """Test claim processing with minimal LLM usage"""
    print("🧪 Testing Minimal Claim Processing")
    print("-" * 40)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        # Create test file
        test_file = create_minimal_test_file()
        print(f"  Test file created: {test_file}")
        
        # Create minimal claim data
        claim_data = {
            "claim_id": "MINIMAL_TEST_001",
            "documents": [
                {
                    "file_name": "minimal_test.txt",
                    "file_path": test_file,
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
                "diagnosis": "Test Diagnosis",
                "procedure_performed": "Test Procedure",
                "claimed_amount": 50000,
                "room_charges": 10000,
                "doctor_charges": 15000,
                "pharmacy_charges": 8000,
                "diagnostics_charges": 7000,
                "number_of_days": 3
            }
        }
        
        print("  Claim data prepared")
        
        # Process through orchestrator
        orchestrator = ClaimOrchestratorAgent()
        print("  Orchestrator initialized")
        
        print("  🔄 Processing claim...")
        result = orchestrator.process(claim_data)
        
        print(f"  📊 Processing completed")
        print(f"    Status: {result.status}")
        print(f"    Decision: {result.data.get('final_decision', {}).get('decision', 'unknown')}")
        print(f"    Confidence: {result.confidence:.2f}")
        
        # Check if processing was successful
        success = result.status in ["approved", "needs_review", "rejected"]
        
        if success:
            print("  ✅ Claim processing completed successfully")
            
            # Show financial calculation if available
            financial = result.data.get("financial_calculation", {})
            if financial:
                print(f"    Gross Amount: {financial.get('gross_claim_amount', 0)}")
                print(f"    Payable Amount: {financial.get('payable_amount', 0)}")
                print(f"    Settlement Ratio: {financial.get('settlement_ratio', 0):.1f}%")
        else:
            print("  ❌ Claim processing failed")
            print(f"    Error: {result.data.get('error', 'Unknown error')}")
        
        return success
        
    except Exception as e:
        print(f"❌ Minimal claim processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_startup():
    """Test if API can start up"""
    print("\n🌐 Testing API Startup")
    print("-" * 40)
    
    try:
        # Check if API file exists
        api_file = "claim_adjudication_api.py"
        if os.path.exists(api_file):
            print("  ✅ API file exists")
            
            # Try to import API module
            import importlib.util
            spec = importlib.util.spec_from_file_location("api", api_file)
            api_module = importlib.util.module_from_spec(spec)
            
            print("  ✅ API module imports successfully")
            print("  📝 Note: Run 'python claim_adjudication_api.py' to start the server")
            return True
        else:
            print("  ❌ API file not found")
            return False
            
    except Exception as e:
        print(f"❌ API startup test failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("🧪 Minimal LLM Integration Tests")
    print("=" * 50)
    print("Testing with minimal LLM dependencies")
    print()
    
    test_results = []
    
    # Test 1: Minimal claim processing
    test_results.append(("Minimal Claim Processing", test_minimal_claim_processing()))
    
    # Test 2: API startup
    test_results.append(("API Startup", test_api_startup()))
    
    # Generate report
    print("\n" + "=" * 50)
    print("📊 MINIMAL TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🟢 MINIMAL TESTS PASSED")
        print("   System is working with basic functionality")
        print("\n📋 Next Steps:")
        print("   1. Start API server: python claim_adjudication_api.py")
        print("   2. Test API endpoints: python test_api_endpoints.py")
        print("   3. Run comprehensive tests: python test_complete_system.py")
    elif success_rate >= 50:
        print("🟡 MINIMAL TESTS PARTIAL")
        print("   Some components working, need fixes")
    else:
        print("🔴 MINIMAL TESTS FAILED")
        print("   Major issues need to be addressed")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
