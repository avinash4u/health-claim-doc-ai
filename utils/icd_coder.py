#!/usr/bin/env python3
"""
ICD-10 Medical Coding System
Converts medical conditions from text to ICD-10 codes
"""

import json
import re
from typing import Dict, Any, List, Optional
import logging

class ICD10Coder:
    """ICD-10 Medical Condition Coder"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_icd_mappings()
    
    def _load_icd_mappings(self):
        """Load ICD-10 code mappings"""
        # Common ICD-10 codes for medical conditions
        self.icd_mappings = {
            # Cardiovascular
            "heart attack": "I21",
            "myocardial infarction": "I21",
            "heart disease": "I25",
            "coronary artery disease": "I25",
            "angina": "I20",
            "hypertension": "I10",
            "high blood pressure": "I10",
            "stroke": "I63",
            "cerebrovascular accident": "I63",
            
            # Respiratory
            "pneumonia": "J18",
            "asthma": "J45",
            "copd": "J44",
            "chronic obstructive pulmonary disease": "J44",
            "bronchitis": "J42",
            "tuberculosis": "A15",
            
            # Gastrointestinal
            "appendicitis": "K35",
            "acute appendicitis": "K35",
            "gastritis": "K29",
            "ulcer": "K27",
            "peptic ulcer": "K27",
            "gastroenteritis": "K52",
            "ibs": "K58",
            "irritable bowel syndrome": "K58",
            
            # Endocrine/Metabolic
            "diabetes": "E11",
            "type 2 diabetes": "E11",
            "type 1 diabetes": "E10",
            "hypothyroidism": "E03",
            "hyperthyroidism": "E05",
            "thyroid": "E03",
            
            # Cancer/Oncology
            "cancer": "C80",
            "malignancy": "C80",
            "carcinoma": "C80",
            "tumor": "D49",
            "neoplasm": "D49",
            "leukemia": "C91",
            "lymphoma": "C85",
            "breast cancer": "C50",
            "lung cancer": "C78",
            "colon cancer": "C78",
            
            # Musculoskeletal
            "fracture": "S72",
            "bone fracture": "S72",
            "osteoporosis": "M81",
            "arthritis": "M19",
            "osteoarthritis": "M19",
            "rheumatoid arthritis": "M06",
            "back pain": "M54",
            "low back pain": "M54",
            
            # Neurological
            "migraine": "G43",
            "headache": "G44",
            "epilepsy": "G40",
            "seizure": "G40",
            "parkinson": "G20",
            "alzheimer": "G30",
            "dementia": "F03",
            
            # Infectious Diseases
            "covid-19": "U07.1",
            "coronavirus": "U07.1",
            "influenza": "J11",
            "flu": "J11",
            "malaria": "B54",
            "dengue": "A91",
            "typhoid": "A01",
            "cholera": "A00",
            
            # Mental Health
            "depression": "F32",
            "anxiety": "F41",
            "bipolar": "F31",
            "schizophrenia": "F20",
            
            # Pregnancy/Childbirth
            "pregnancy": "O80",
            "childbirth": "O80",
            "delivery": "O80",
            "cesarean": "O82",
            
            # Injuries
            "burn": "T30",
            "injury": "T07",
            "trauma": "T07",
            "wound": "T14",
            
            # Symptoms/Signs
            "fever": "R50",
            "cough": "R05",
            "chest pain": "R07",
            "abdominal pain": "R10",
            "headache": "G44",
            "fatigue": "R53",
            "nausea": "R11",
            "vomiting": "R11",
            "diarrhea": "R19"
        }
        
        # Multi-word patterns for better matching
        self.pattern_mappings = {
            r'\b(acute|chronic)\s+(appendicitis|gastritis|bronchitis|pancreatitis)\b': lambda m: f"K{35 if 'appendicitis' in m.group(2) else 29 if 'gastritis' in m.group(2) else 42 if 'bronchitis' in m.group(2) else 85}",
            r'\b(type\s+[12])\s+diabetes\b': lambda m: "E10" if "1" in m.group(1) else "E11",
            r'\b(breast|lung|colon|prostate)\s+(cancer|carcinoma)\b': lambda m: f"C{50 if 'breast' in m.group(1) else 78 if 'lung' in m.group(1) else 78 if 'colon' in m.group(1) else 61}",
            r'\b(heart|cardiac)\s+(attack|failure)\b': lambda m: "I21" if "attack" in m.group(2) else "I50",
            r'\b(acute|chronic)\s+(kidney|renal)\s+(failure|insufficiency)\b': lambda m: "N17" if "acute" in m.group(1) else "N18",
        }
        
        # Simple pattern replacements for complex cases
        self.simple_patterns = {
            r'\b(acute|chronic)\s+appendicitis\b': "K35",
            r'\b(acute|chronic)\s+gastritis\b': "K29", 
            r'\b(acute|chronic)\s+bronchitis\b': "J42",
            r'\b(type\s+1)\s+diabetes\b': "E10",
            r'\b(type\s+2)\s+diabetes\b': "E11",
            r'\bbreast\s+cancer\b': "C50",
            r'\blung\s+cancer\b': "C78",
            r'\bheart\s+attack\b': "I21",
            r'\bheart\s+failure\b': "I50",
            r'\bacute\s+kidney\s+failure\b': "N17",
            r'\bchronic\s+kidney\s+failure\b': "N18"
        }
    
    def code_medical_condition(self, condition_text: str) -> Dict[str, Any]:
        """
        Convert medical condition text to ICD-10 codes
        
        Args:
            condition_text: Medical condition description
            
        Returns:
            Dictionary with ICD codes and confidence scores
        """
        if not condition_text or not isinstance(condition_text, str):
            return {
                "original_text": "",
                "icd_codes": [],
                "primary_code": "",
                "confidence": 0.0,
                "coding_method": "none"
            }
        
        original_text = condition_text.strip().lower()
        found_codes = []
        code_confidence = {}
        
        # Method 1: Direct mapping
        for condition, code in self.icd_mappings.items():
            if condition in original_text:
                if code not in found_codes:
                    found_codes.append(code)
                    code_confidence[code] = 0.9
        
        # Method 2: Simple pattern matching
        for pattern, code in self.simple_patterns.items():
            matches = re.findall(pattern, original_text, re.IGNORECASE)
            if matches and code not in found_codes:
                found_codes.append(code)
                code_confidence[code] = 0.85
        
        # Method 3: Complex pattern matching (with error handling)
        for pattern, code_func in self.pattern_mappings.items():
            try:
                matches = re.findall(pattern, original_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        code = code_func(match)
                    else:
                        code = code_func(match)
                    if code not in found_codes:
                        found_codes.append(code)
                        code_confidence[code] = 0.85
            except Exception as e:
                # Skip problematic patterns
                continue
        
        # Method 4: Word-based matching
        words = original_text.split()
        for word in words:
            if word in self.icd_mappings:
                code = self.icd_mappings[word]
                if code not in found_codes:
                    found_codes.append(code)
                    code_confidence[code] = 0.7
        
        # Determine primary code (highest confidence)
        primary_code = ""
        max_confidence = 0.0
        for code, confidence in code_confidence.items():
            if confidence > max_confidence:
                max_confidence = confidence
                primary_code = code
        
        # Determine coding method
        coding_method = "none"
        if found_codes:
            if max_confidence >= 0.9:
                coding_method = "direct_mapping"
            elif max_confidence >= 0.85:
                coding_method = "pattern_matching"
            else:
                coding_method = "word_matching"
        
        return {
            "original_text": condition_text,
            "icd_codes": found_codes,
            "primary_code": primary_code,
            "confidence": max_confidence,
            "coding_method": coding_method,
            "all_codes_with_confidence": code_confidence
        }
    
    def get_icd_description(self, icd_code: str) -> str:
        """Get description for ICD-10 code"""
        descriptions = {
            "I21": "Acute myocardial infarction",
            "I25": "Chronic ischemic heart disease",
            "I20": "Angina pectoris",
            "I10": "Essential (primary) hypertension",
            "I63": "Cerebral infarction",
            "J18": "Pneumonia, unspecified organism",
            "J45": "Asthma",
            "J44": "Other chronic obstructive pulmonary disease",
            "J42": "Unspecified chronic bronchitis",
            "A15": "Respiratory tuberculosis",
            "K35": "Acute appendicitis",
            "K29": "Gastritis and duodenitis",
            "K27": "Peptic ulcer",
            "K52": "Other gastroenteritis and colitis",
            "K58": "Irritable bowel syndrome",
            "E11": "Type 2 diabetes mellitus",
            "E10": "Type 1 diabetes mellitus",
            "E03": "Other hypothyroidism",
            "E05": "Thyrotoxicosis",
            "C80": "Malignant neoplasm, unspecified",
            "D49": "Neoplasms of unspecified behavior",
            "C91": "Leukemia",
            "C85": "Non-Hodgkin lymphoma",
            "C50": "Malignant neoplasm of breast",
            "C78": "Secondary malignant neoplasm of respiratory and digestive organs",
            "S72": "Fracture of femur",
            "M81": "Osteoporosis",
            "M19": "Osteoarthritis",
            "M06": "Rheumatoid arthritis",
            "M54": "Dorsalgia",
            "G43": "Migraine",
            "G44": "Other headache syndromes",
            "G40": "Epilepsy",
            "G20": "Parkinson's disease",
            "G30": "Alzheimer's disease",
            "F03": "Unspecified dementia",
            "U07.1": "COVID-19",
            "J11": "Influenza due to unidentified influenza virus",
            "B54": "Malaria",
            "A91": "Dengue fever",
            "A01": "Typhoid and paratyphoid fevers",
            "A00": "Cholera",
            "F32": "Depressive episode",
            "F41": "Anxiety disorders",
            "F31": "Bipolar affective disorder",
            "F20": "Schizophrenia",
            "O80": "Encounter for full-term uncomplicated delivery",
            "O82": "Encounter for cesarean delivery",
            "T30": "Burns",
            "T07": "Unspecified multiple injuries",
            "T14": "Injury of unspecified body region",
            "R50": "Fever",
            "R05": "Cough",
            "R07": "Pain in throat and chest",
            "R10": "Abdominal and pelvic pain",
            "R53": "Fatigue",
            "R11": "Nausea and vomiting",
            "R19": "Other symptoms and signs involving digestive system"
        }
        
        return descriptions.get(icd_code, "Unknown ICD-10 code")
    
    def validate_policy_coverage(self, condition_codes: List[str], policy_coverage: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if medical conditions are covered under policy
        
        Args:
            condition_codes: List of ICD-10 codes from medical documents
            policy_coverage: Policy coverage configuration with ICD codes
            
        Returns:
            Coverage validation result
        """
        covered_codes = policy_coverage.get("covered_icd_codes", [])
        excluded_codes = policy_coverage.get("excluded_icd_codes", [])
        limited_coverage_codes = policy_coverage.get("limited_coverage_icd_codes", {})
        
        coverage_results = []
        
        for code in condition_codes:
            result = {
                "icd_code": code,
                "description": self.get_icd_description(code),
                "covered": False,
                "excluded": False,
                "limited": False,
                "coverage_percentage": 0,
                "notes": []
            }
            
            # Check if excluded
            if code in excluded_codes:
                result["excluded"] = True
                result["covered"] = False
                result["notes"].append("Explicitly excluded under policy")
            
            # Check if covered
            elif code in covered_codes:
                result["covered"] = True
                result["coverage_percentage"] = 100
                result["notes"].append("Fully covered under policy")
            
            # Check if limited coverage
            elif code in limited_coverage_codes:
                result["limited"] = True
                result["covered"] = True
                result["coverage_percentage"] = limited_coverage_codes[code]
                result["notes"].append(f"Limited coverage: {limited_coverage_codes[code]}%")
            
            # Default case
            else:
                result["notes"].append("Coverage not specified in policy")
            
            coverage_results.append(result)
        
        # Overall coverage assessment
        total_codes = len(coverage_results)
        fully_covered = sum(1 for r in coverage_results if r["covered"] and not r["excluded"] and not r["limited"])
        excluded_count = sum(1 for r in coverage_results if r["excluded"])
        limited_count = sum(1 for r in coverage_results if r["limited"])
        
        overall_coverage = {
            "total_conditions": total_codes,
            "fully_covered": fully_covered,
            "excluded": excluded_count,
            "limited": limited_count,
            "overall_status": "covered" if excluded_count == 0 else "partially_covered" if fully_covered > 0 else "not_covered",
            "coverage_percentage": (fully_covered / total_codes * 100) if total_codes > 0 else 0,
            "detailed_results": coverage_results
        }
        
        return overall_coverage

# Global instance
icd_coder = ICD10Coder()

def code_medical_conditions_from_text(text: str) -> Dict[str, Any]:
    """Convenience function to code medical conditions from text"""
    return icd_coder.code_medical_condition(text)

def validate_icd_coverage(icd_codes: List[str], policy_coverage: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate ICD code coverage"""
    return icd_coder.validate_policy_coverage(icd_codes, policy_coverage)
