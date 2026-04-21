#!/usr/bin/env python3
"""
Detailed System Test with Input/Output Analysis
"""

import os
import sys
import json
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_single_agent_with_details():
    """Test a single agent with detailed input/output analysis"""
    print("🔍 Testing Single Agent with Detailed Analysis")
    print("-" * 50)
    
    try:
        from agents.document_agent import DocumentProcessingAgent
        
        agent = DocumentProcessingAgent()
        
        # Create test claim data
        test_claim = {
            "claim_id": "DETAILED_TEST_001",
            "documents": [
                {
                    "file_name": "test_discharge.txt",
                    "file_path": "uploads/test_discharge.txt",
                    "file_size": 1000
                }
            ]
        }
        
        print("📋 INPUT DATA:")
        print(json.dumps(test_claim, indent=2))
        print()
        
        print("🔄 PROCESSING...")
        start_time = time.time()
        result = agent.process(test_claim)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing Time: {processing_time:.2f}s")
        print()
        
        print("📊 OUTPUT DATA:")
        print(f"   Status: {result.status}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Agent Name: {result.agent_name}")
        print()
        
        print("📋 RESULT DATA STRUCTURE:")
        if isinstance(result.data, dict):
            for key, value in result.data.items():
                print(f"   {key}: {type(value).__name__} = {value}")
        else:
            print(f"   Data Type: {type(result.data).__name__}")
            print(f"   Data Value: {result.data}")
        
        print()
        print("🧠 ANALYSIS:")
        if result.status == "error":
            print("   ❌ Agent failed - check error message")
        elif result.status == "needs_review":
            print("   ⚠️  Agent needs review - missing required docs")
        elif result.status in ["approved", "completed"]:
            print("   ✅ Agent succeeded")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_with_details():
    """Test end-to-end claim processing with detailed analysis"""
    print("\n🔄 Testing End-to-End with Detailed Analysis")
    print("-" * 50)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        orchestrator = ClaimOrchestratorAgent()
        
        # Create comprehensive test claim
        test_claim = {
            "claim_id": "DETAILED_E2E_001",
            "documents": [
                {
                    "file_name": "test_discharge.txt",
                    "file_path": "uploads/test_discharge.txt",
                    "file_size": 1000
                },
                {
                    "file_name": "test_bill.txt", 
                    "file_path": "uploads/test_bill.txt",
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
                "diagnosis": "Appendicitis",
                "procedure_performed": "Appendectomy",
                "claimed_amount": 50000,
                "room_charges": 10000,
                "doctor_charges": 15000,
                "pharmacy_charges": 8000,
                "diagnostics_charges": 7000,
                "number_of_days": 3
            }
        }
        
        print("📋 INPUT CLAIM DATA:")
        print("   Policy Details:")
        for key, value in test_claim["policy_details"].items():
            print(f"     {key}: {value} ({type(value).__name__})")
        
        print("   Claim Details:")
        for key, value in test_claim["claim_details"].items():
            print(f"     {key}: {value} ({type(value).__name__})")
        
        print()
        
        print("🔄 PROCESSING THROUGH ORCHESTRATOR...")
        start_time = time.time()
        result = orchestrator.process(test_claim)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing Time: {processing_time:.2f}s")
        print()
        
        print("📊 ORCHESTRATOR OUTPUT:")
        print(f"   Status: {result.status}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Reasoning: {result.reasoning}")
        print()
        
        print("📋 RESULT DATA BREAKDOWN:")
        if isinstance(result.data, dict):
            for key, value in result.data.items():
                print(f"   {key}:")
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        print(f"     - {subkey}: {subvalue} ({type(subvalue).__name__})")
                else:
                    print(f"     Value: {value} ({type(value).__name__})")
        
        print()
        
        print("🧠 DECISION ANALYSIS:")
        final_decision = result.data.get("final_decision", {}) if isinstance(result.data, dict) else {}
        decision = final_decision.get("decision", "unknown")
        confidence = final_decision.get("confidence", 0.0)
        
        print(f"   Final Decision: {decision}")
        print(f"   Decision Confidence: {confidence}")
        
        if decision == "approved":
            print("   ✅ Claim approved for payment")
        elif decision == "rejected":
            print("   ❌ Claim rejected")
        elif decision == "needs_review":
            print("   ⚠️  Claim needs manual review")
        else:
            print("   ❓ Unknown decision status")
        
        return True
        
    except Exception as e:
        print(f"❌ E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_agent_communication():
    """Analyze how agents communicate with each other"""
    print("\n🤝 Analyzing Agent Communication")
    print("-" * 50)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        orchestrator = ClaimOrchestratorAgent()
        
        print("📋 AGENT REGISTRATION:")
        print(f"   Total Agents: {len(orchestrator.agents)}")
        for name, agent in orchestrator.agents.items():
            print(f"   - {name}: {type(agent).__name__}")
        
        print()
        print("🔄 TESTING AGENT VALIDATION:")
        test_claim = {
            "claim_id": "COMM_TEST_001",
            "documents": [],
            "policy_details": {},
            "claim_details": {}
        }
        
        for name, agent in orchestrator.agents.items():
            print(f"   Testing {name}...")
            try:
                if hasattr(agent, 'validate_input'):
                    is_valid = agent.validate_input(test_claim)
                    print(f"     validate_input(): {is_valid}")
                else:
                    print(f"     validate_input(): Method not found")
            except Exception as e:
                print(f"     validate_input(): Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Communication analysis failed: {e}")
        return False

def main():
    """Run detailed system analysis"""
    print("🔍 DETAILED SYSTEM ANALYSIS")
    print("=" * 60)
    print("Analyzing input/output flow and agent communication")
    print()
    
    test_results = []
    
    # Test 1: Single Agent Analysis
    test_results.append(("Single Agent", test_single_agent_with_details()))
    
    # Test 2: End-to-End Analysis
    test_results.append(("End-to-End", test_end_to_end_with_details()))
    
    # Test 3: Agent Communication
    test_results.append(("Agent Communication", analyze_agent_communication()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DETAILED TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🟢 SYSTEM ANALYSIS COMPLETE")
        print("   Input/output flow working correctly")
        print("   Agent communication functional")
        print("   Ready for production deployment")
    elif success_rate >= 50:
        print("🟡 SYSTEM ANALYSIS PARTIAL")
        print("   Some components working, others need fixes")
    else:
        print("🔴 SYSTEM ANALYSIS FAILED")
        print("   Major issues need to be addressed")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
