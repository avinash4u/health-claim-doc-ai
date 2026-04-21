#!/usr/bin/env python3
"""
Test ICD Coding System with Real Medical Documents
"""

import os
import sys
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_icd_coding():
    """Test ICD coding functionality"""
    print("🏥 TESTING ICD CODING SYSTEM")
    print("=" * 50)
    
    try:
        from utils.icd_coder import code_medical_conditions_from_text, validate_icd_coverage
        
        # Test cases with real medical conditions
        test_cases = [
            {
                "description": "Acute Appendicitis",
                "text": "Acute Appendicitis, Peritonitis",
                "expected_icd": "K35"
            },
            {
                "description": "Type 2 Diabetes",
                "text": "Type 2 Diabetes Mellitus with complications",
                "expected_icd": "E11"
            },
            {
                "description": "Heart Attack",
                "text": "Acute Myocardial Infarction",
                "expected_icd": "I21"
            },
            {
                "description": "Pneumonia",
                "text": "Community acquired pneumonia",
                "expected_icd": "J18"
            },
            {
                "description": "Fracture",
                "text": "Femur fracture due to fall",
                "expected_icd": "S72"
            },
            {
                "description": "COVID-19",
                "text": "COVID-19 pneumonia",
                "expected_icd": "U07.1"
            }
        ]
        
        print("🔍 TESTING ICD CODE GENERATION:")
        print("-" * 40)
        
        coding_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['description']}")
            print(f"   Input Text: '{test_case['text']}'")
            
            # Code the medical condition
            result = code_medical_conditions_from_text(test_case['text'])
            
            print(f"   Primary ICD Code: {result['primary_code']}")
            print(f"   All ICD Codes: {result['icd_codes']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Coding Method: {result['coding_method']}")
            
            # Check if expected code matches
            if result['primary_code'] == test_case['expected_icd']:
                print(f"   ✅ CORRECT - Expected {test_case['expected_icd']}")
            else:
                print(f"   ⚠️  MISMATCH - Expected {test_case['expected_icd']}, got {result['primary_code']}")
            
            coding_results.append({
                "condition": test_case['description'],
                "text": test_case['text'],
                "expected": test_case['expected_icd'],
                "actual": result['primary_code'],
                "confidence": result['confidence'],
                "correct": result['primary_code'] == test_case['expected_icd']
            })
        
        return coding_results
        
    except Exception as e:
        print(f"❌ ICD coding test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_policy_coverage_with_icd():
    """Test policy coverage validation with ICD codes"""
    print("\n🛡️ TESTING POLICY COVERAGE WITH ICD CODES")
    print("=" * 50)
    
    try:
        from utils.icd_coder import validate_icd_coverage
        
        # Sample policy configuration with ICD codes
        policy_coverage = {
            "covered_icd_codes": [
                "K35",  # Appendicitis
                "J18",  # Pneumonia
                "I21",  # Heart attack
                "E11",  # Type 2 diabetes
                "S72",  # Fracture
                "U07.1" # COVID-19
            ],
            "excluded_icd_codes": [
                "C80",  # Cancer (excluded)
                "F32"   # Depression (excluded)
            ],
            "limited_coverage_icd_codes": {
                "I10": 50,  # Hypertension - 50% coverage
                "M81": 70   # Osteoporosis - 70% coverage
            }
        }
        
        print("📋 POLICY COVERAGE CONFIGURATION:")
        print("-" * 40)
        print(f"   Fully Covered ICD Codes: {policy_coverage['covered_icd_codes']}")
        print(f"   Excluded ICD Codes: {policy_coverage['excluded_icd_codes']}")
        print(f"   Limited Coverage: {policy_coverage['limited_coverage_icd_codes']}")
        print()
        
        # Test cases
        test_scenarios = [
            {
                "description": "Fully Covered Condition",
                "icd_codes": ["K35", "J18"],
                "expected_status": "covered"
            },
            {
                "description": "Excluded Condition",
                "icd_codes": ["C80"],
                "expected_status": "not_covered"
            },
            {
                "description": "Mixed Coverage",
                "icd_codes": ["K35", "C80"],
                "expected_status": "partially_covered"
            },
            {
                "description": "Limited Coverage",
                "icd_codes": ["I10"],
                "expected_status": "covered"
            },
            {
                "description": "Unknown Condition",
                "icd_codes": ["Z99.9"],
                "expected_status": "not_covered"
            }
        ]
        
        coverage_results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['description']}")
            print(f"   ICD Codes: {scenario['icd_codes']}")
            
            # Validate coverage
            result = validate_icd_coverage(scenario['icd_codes'], policy_coverage)
            
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Coverage Percentage: {result['coverage_percentage']:.1f}%")
            print(f"   Fully Covered: {result['fully_covered']}")
            print(f"   Excluded: {result['excluded']}")
            print(f"   Limited: {result['limited']}")
            
            # Show detailed results
            for detail in result['detailed_results']:
                status_icon = "✅" if detail['covered'] and not detail['excluded'] else "❌" if detail['excluded'] else "⚠️"
                print(f"     {status_icon} {detail['icd_code']} ({detail['description']}): {detail['coverage_percentage']}% - {', '.join(detail['notes'])}")
            
            # Check if expected status matches
            if result['overall_status'] == scenario['expected_status']:
                print(f"   ✅ CORRECT - Expected {scenario['expected_status']}")
            else:
                print(f"   ⚠️  MISMATCH - Expected {scenario['expected_status']}, got {result['overall_status']}")
            
            coverage_results.append({
                "scenario": scenario['description'],
                "icd_codes": scenario['icd_codes'],
                "expected": scenario['expected_status'],
                "actual": result['overall_status'],
                "coverage_percentage": result['coverage_percentage'],
                "correct": result['overall_status'] == scenario['expected_status']
            })
        
        return coverage_results
        
    except Exception as e:
        print(f"❌ Policy coverage test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_document_extraction_with_icd():
    """Test document extraction with ICD coding"""
    print("\n📄 TESTING DOCUMENT EXTRACTION WITH ICD CODING")
    print("=" * 50)
    
    try:
        from agents.document_agent import DocumentProcessingAgent
        
        agent = DocumentProcessingAgent()
        
        # Test with discharge summary
        test_claim = {
            "claim_id": "ICD_TEST_001",
            "documents": [
                {
                    "file_name": "test_discharge.txt",
                    "file_path": "uploads/test_discharge.txt",
                    "file_size": 1000
                }
            ]
        }
        
        print("🔍 PROCESSING DISCHARGE SUMMARY WITH ICD CODING:")
        print("-" * 40)
        
        result = agent.process(test_claim)
        
        if result.status != "error" and isinstance(result.data, dict):
            documents = result.data.get("documents", [])
            if documents:
                doc = documents[0]
                
                print(f"   Document Type: {doc.get('document_type')}")
                print(f"   Processing Status: {doc.get('processing_status')}")
                print()
                
                # Parse extracted fields
                fields_str = doc.get("extracted_fields", "{}")
                if isinstance(fields_str, str):
                    try:
                        fields = json.loads(fields_str)
                        
                        print("🏥 EXTRACTED MEDICAL INFORMATION:")
                        print("-" * 40)
                        print(f"   Diagnosis: {fields.get('Diagnosis', 'Not Specified')}")
                        print(f"   Procedure: {fields.get('Procedure Performed', 'Not Specified')}")
                        print(f"   Patient: {fields.get('Patient Name', 'Not Specified')}")
                        print(f"   Hospital: {fields.get('Hospital Name', 'Not Specified')}")
                        print()
                        
                        # Show ICD coding results
                        icd_codes = fields.get("ICD_Codes", {})
                        if icd_codes:
                            print("🏥 ICD CODING RESULTS:")
                            print("-" * 40)
                            print(f"   Primary ICD Code: {icd_codes.get('primary_code', 'None')}")
                            print(f"   All ICD Codes: {icd_codes.get('all_codes', [])}")
                            print(f"   Confidence: {icd_codes.get('confidence', 0):.2f}")
                            print(f"   Coding Method: {icd_codes.get('coding_method', 'none')}")
                            
                            # Show ICD descriptions
                            from utils.icd_coder import icd_coder
                            for code in icd_codes.get('all_codes', []):
                                description = icd_coder.get_icd_description(code)
                                print(f"   - {code}: {description}")
                        else:
                            print("   ❌ No ICD codes generated")
                        
                        return True
                        
                    except json.JSONDecodeError:
                        print(f"   ❌ Error parsing fields: {fields_str}")
                        return False
                else:
                    print(f"   ❌ Invalid fields format: {type(fields_str)}")
                    return False
        else:
            print(f"   ❌ Document processing failed: {result.status}")
            return False
        
    except Exception as e:
        print(f"❌ Document extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive ICD coding tests"""
    print("🔍 COMPREHENSIVE ICD CODING TEST")
    print("=" * 60)
    print("Testing ICD code generation and policy coverage validation")
    print()
    
    test_results = []
    
    # Test 1: ICD Code Generation
    coding_results = test_icd_coding()
    coding_success = sum(1 for r in coding_results if r['correct']) / len(coding_results) * 100 if coding_results else 0
    test_results.append(("ICD Code Generation", coding_success >= 80))
    
    # Test 2: Policy Coverage Validation
    coverage_results = test_policy_coverage_with_icd()
    coverage_success = sum(1 for r in coverage_results if r['correct']) / len(coverage_results) * 100 if coverage_results else 0
    test_results.append(("Policy Coverage", coverage_success >= 80))
    
    # Test 3: Document Extraction with ICD
    extraction_success = test_document_extraction_with_icd()
    test_results.append(("Document Extraction", extraction_success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ICD CODING TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall Results: {passed}/{total} ({success_rate:.1f}%)")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    if coding_results:
        coding_accuracy = sum(1 for r in coding_results if r['correct']) / len(coding_results) * 100
        print(f"   ICD Coding Accuracy: {coding_accuracy:.1f}%")
    
    if coverage_results:
        coverage_accuracy = sum(1 for r in coverage_results if r['correct']) / len(coverage_results) * 100
        print(f"   Policy Coverage Accuracy: {coverage_accuracy:.1f}%")
    
    if success_rate >= 75:
        print("🟢 ICD CODING SYSTEM WORKING")
        print("   Medical conditions correctly coded to ICD-10")
        print("   Policy coverage validation accurate")
        print("   Document extraction with ICD coding functional")
    elif success_rate >= 50:
        print("🟡 ICD CODING SYSTEM PARTIAL")
        print("   Some components working, others need improvement")
    else:
        print("🔴 ICD CODING SYSTEM NEEDS FIXES")
        print("   Major issues in ICD coding or coverage validation")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
