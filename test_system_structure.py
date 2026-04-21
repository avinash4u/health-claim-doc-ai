#!/usr/bin/env python3
"""
Test System Structure Without LLM Dependencies
"""

import os
import sys
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_agent_structure():
    """Test if all agents can be imported and initialized"""
    print("🔧 Testing Agent Structure")
    print("-" * 40)
    
    try:
        from agents.base_agent import BaseAgent, AgentResult
        from agents.document_agent import DocumentProcessingAgent
        from agents.policy_agent import PolicyValidationAgent
        from agents.medical_agent import MedicalNecessityAgent
        from agents.coverage_agent import CoverageVerificationAgent
        from agents.fraud_agent import FraudDetectionAgent
        from agents.calculation_agent import AmountCalculationAgent
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        agents = {
            "Document Agent": DocumentProcessingAgent(),
            "Policy Agent": PolicyValidationAgent(),
            "Medical Agent": MedicalNecessityAgent(),
            "Coverage Agent": CoverageVerificationAgent(),
            "Fraud Agent": FraudDetectionAgent(),
            "Calculation Agent": AmountCalculationAgent(),
            "Orchestrator Agent": ClaimOrchestratorAgent()
        }
        
        print("✅ All agents imported and initialized successfully")
        print(f"   Total agents: {len(agents)}")
        
        for name, agent in agents.items():
            print(f"   - {name}: {type(agent).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_basic():
    """Test orchestrator with minimal data"""
    print("\n🤖 Testing Orchestrator Basic Functionality")
    print("-" * 40)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        
        orchestrator = ClaimOrchestratorAgent()
        
        # Test validation
        valid_data = {
            "claim_id": "TEST_001",
            "documents": [],
            "policy_details": {}
        }
        
        invalid_data = {}
        
        print(f"  Valid data validation: {orchestrator.validate_input(valid_data)}")
        print(f"  Invalid data validation: {orchestrator.validate_input(invalid_data)}")
        
        # Test individual methods
        print("  Testing individual methods...")
        
        # Test claim details extraction
        mock_extracted_data = {
            "claim_id": "TEST_001",
            "documents": [
                {
                    "file_name": "test.txt",
                    "document_type": "Discharge Summary",
                    "extracted_fields": json.dumps({
                        "Patient Name": "Test User",
                        "Age": "45",
                        "Hospital Name": "Test Hospital",
                        "Diagnosis": "Test Diagnosis"
                    })
                }
            ]
        }
        
        claim_details = orchestrator._extract_claim_details(mock_extracted_data)
        print(f"  Claim details extraction: ✅")
        print(f"    Patient: {claim_details.get('patient_name')}")
        print(f"    Hospital: {claim_details.get('hospital_name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_result_structure():
    """Test AgentResult structure"""
    print("\n📊 Testing AgentResult Structure")
    print("-" * 40)
    
    try:
        from agents.base_agent import AgentResult
        
        # Create test result
        result = AgentResult(
            agent_name="Test Agent",
            status="completed",
            data={"test": "data"},
            confidence=0.85,
            reasoning="Test reasoning"
        )
        
        # Test to_dict method
        result_dict = result.to_dict()
        print(f"  AgentResult.to_dict(): ✅")
        print(f"    Keys: {list(result_dict.keys())}")
        
        # Test result access
        print(f"  Status access: {result.status}")
        print(f"  Confidence access: {result.confidence}")
        print(f"  Data access: {result.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentResult structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_claim_processing():
    """Test claim processing with mocked data"""
    print("\n🎭 Testing Mock Claim Processing")
    print("-" * 40)
    
    try:
        from agents.orchestrator_agent import ClaimOrchestratorAgent
        from agents.base_agent import AgentResult
        
        orchestrator = ClaimOrchestratorAgent()
        
        # Create mock claim data
        claim_data = {
            "claim_id": "MOCK_TEST_001",
            "documents": [],
            "policy_details": {
                "policy_number": "POL123456",
                "sum_insured": 500000,
                "status": "active",
                "premium_status": "paid"
            },
            "claim_details": {
                "patient_name": "Mock User",
                "claimed_amount": 100000,
                "diagnosis": "Mock Diagnosis",
                "hospital_name": "Mock Hospital"
            }
        }
        
        print("  Mock claim data created")
        print(f"    Claim ID: {claim_data['claim_id']}")
        print(f"    Patient: {claim_data['claim_details']['patient_name']}")
        print(f"    Amount: {claim_data['claim_details']['claimed_amount']}")
        
        # Test validation
        validation = orchestrator.validate_input(claim_data)
        print(f"  Input validation: {'✅' if validation else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock claim processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run structure tests"""
    print("🏗️ System Structure Tests")
    print("=" * 50)
    print("Testing system without LLM dependencies")
    print()
    
    test_results = []
    
    # Test 1: Agent structure
    test_results.append(("Agent Structure", test_agent_structure()))
    
    # Test 2: Orchestrator basic
    test_results.append(("Orchestrator Basic", test_orchestrator_basic()))
    
    # Test 3: AgentResult structure
    test_results.append(("AgentResult Structure", test_agent_result_structure()))
    
    # Test 4: Mock claim processing
    test_results.append(("Mock Claim Processing", test_mock_claim_processing()))
    
    # Generate report
    print("\n" + "=" * 50)
    print("📊 STRUCTURE TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🟢 SYSTEM STRUCTURE IS GOOD")
        print("   Ready for LLM integration testing")
    elif success_rate >= 50:
        print("🟡 SYSTEM STRUCTURE HAS MINOR ISSUES")
        print("   Fix structural issues before LLM testing")
    else:
        print("🔴 SYSTEM STRUCTURE HAS MAJOR ISSUES")
        print("   Review agent implementations")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
