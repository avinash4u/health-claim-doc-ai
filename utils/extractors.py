import os
import json
import ollama
from dotenv import load_dotenv

# Import ICD coder
from .icd_coder import code_medical_conditions_from_text

load_dotenv()

EXTRACTION_PROMPTS = {
    "Discharge Summary": """
You are a medical document extraction expert. Extract ALL available information from this discharge summary.

Return ONLY valid JSON with these exact keys (use "Not Specified" if information is not found):
{
  "Patient Name": "extract full patient name",
  "Age": "extract patient age",
  "Gender": "extract Male/Female/Other",
  "UHID / IP Number": "extract hospital ID number",
  "Admission Date": "extract admission date",
  "Discharge Date": "extract discharge date", 
  "Diagnosis": "extract primary and secondary diagnoses",
  "Procedure Performed": "extract medical procedures/surgeries",
  "Treating Doctor": "extract attending physician name",
  "Hospital Name": "extract hospital name",
  "Hospital Address": "extract hospital address",
  "Total Amount": "extract total bill amount if available",
  "Room Charges": "extract room/accommodation charges if available",
  "Doctor Charges": "extract doctor/consultation fees if available",
  "Pharmacy Charges": "extract medicine/pharmacy costs if available",
  "Diagnostics Charges": "extract lab/test charges if available",
  "Bill Number": "extract bill/invoice number if available",
  "Bill Date": "extract bill date if available"
}

CRITICAL: 
- Return ONLY the JSON object above
- Do NOT include explanations or code blocks
- Extract ALL available information accurately
- Convert lists/arrays to comma-separated strings
- Use "Not Specified" for missing fields

Document text:
{text}

JSON Response:
""",
    
    "Final Bill": """
You are a medical billing expert. Extract ALL billing information from this hospital bill.

Return ONLY valid JSON with these exact keys (use "Not Specified" if information is not found):
{
  "Patient Name": "extract patient name",
  "Hospital Name": "extract hospital name",
  "Bill Number": "extract bill/invoice number",
  "Bill Date": "extract bill date",
  "Admission Date": "extract admission date",
  "Discharge Date": "extract discharge date",
  "Total Amount": "extract total bill amount",
  "Amount Paid": "extract amount already paid",
  "Amount Due": "extract remaining balance",
  "Room Charges": "extract room/accommodation charges",
  "Doctor Charges": "extract doctor/consultation fees",
  "Pharmacy Charges": "extract medicine/pharmacy costs",
  "Diagnostics Charges": "extract lab/test charges"
}

CRITICAL: 
- Return ONLY the JSON object above
- Do NOT include explanations or code blocks
- Extract ALL available billing details accurately
- Use "Not Specified" for missing fields

Document text:
{text}

JSON Response:
""",
    
    "Radiology Report": """
You are a radiology expert. Extract ALL diagnostic information from this radiology report.

CRITICAL: You MUST return ONLY a valid JSON object. No explanations, no paragraphs, no extra text.

Required JSON format:
{
  "Patient Name": "extract patient name",
  "Age": "extract patient age",
  "Gender": "extract Male/Female/Other",
  "Test Type": "extract X-ray/MRI/CT/Ultrasound etc",
  "Examination Date": "extract date of examination",
  "Clinical Indication": "extract reason for test/symptoms",
  "Findings": "extract detailed radiological findings",
  "Impression": "extract radiologist's conclusion/opinion",
  "Radiologist Name": "extract radiologist name",
  "Hospital Name": "extract hospital/facility name"
}

IMPORTANT:
- Return ONLY the JSON object shown above
- Replace "extract..." with actual values
- Use "Not Specified" if information not found
- Do NOT include any explanations or additional text

Document text:
{text}

JSON Response:
""",
    
    "Claim Form": """
You are an insurance expert. Extract ALL claim information from this insurance claim form.

Return ONLY valid JSON with these exact keys (use "Not Specified" if information is not found):
{
  "Insured Name": "extract patient/insured name",
  "Policy Number": "extract insurance policy number",
  "Claim Number": "extract claim reference number",
  "Hospital Name": "extract hospital name",
  "Admission Date": "extract admission date",
  "Discharge Date": "extract discharge date",
  "Diagnosis": "extract medical diagnosis",
  "Claimed Amount": "extract total claim amount",
  "Bank Account Details": "extract bank information for payment"
}

CRITICAL: 
- Return ONLY the JSON object above
- Do NOT include explanations or code blocks
- Extract ALL insurance details accurately
- Use "Not Specified" for missing fields

Document text:
{text}

JSON Response:
""",
    
    "Cashless Authorization Letter": """
You are an insurance authorization expert. Extract ALL authorization information from this cashless approval letter.

Return ONLY valid JSON with these exact keys (use "Not Specified" if information is not found):
{
  "Patient Name": "extract patient name",
  "Policy Number": "extract insurance policy number",
  "Authorization Number": "extract approval/reference number",
  "Approved Amount": "extract authorized amount",
  "Validity Period": "extract approval validity dates",
  "Hospital Name": "extract hospital name",
  "Treatment Details": "extract approved treatment/procedures"
}

CRITICAL: 
- Return ONLY the JSON object above
- Do NOT include explanations or code blocks
- Extract ALL authorization details accurately
- Use "Not Specified" for missing fields

Document text:
{text}

JSON Response:
"""
}

def extract_fields(text: str, doc_type: str) -> str:
    """
    Extract fields using LLM with enhanced prompts for better accuracy
    """
    
    # Check if Ollama is available
    try:
        ollama.list()
        ollama_available = True
    except:
        ollama_available = False
    
    if not ollama_available:
        return json.dumps({
            "error": "Ollama not available",
            "message": "LLM service is required for field extraction",
            "suggestion": "Please start Ollama service",
            "fallback_fields": get_fallback_fields(doc_type)
        })
    
    # Use document-specific prompt if available, otherwise use generic
    if doc_type in EXTRACTION_PROMPTS:
        prompt = EXTRACTION_PROMPTS[doc_type].replace("{text}", text)
    else:
        prompt = f"""
You are a medical document extraction expert. Extract ALL available information from this {doc_type}.

Return ONLY valid JSON with relevant fields for this document type.
Use "Not Specified" for any information that cannot be found.

Document text:
{text}

JSON Response:
"""
    
    try:
        # Use LLM for extraction
        response = ollama.chat(
            model='mistral',  # Using mistral for better JSON handling
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        result = response['message']['content'].strip()
        
        # Clean up the response
        if '```json' in result:
            start = result.find('```json') + 7
            end = result.find('```', start)
            if start > 6 and end > start:
                result = result[start:end].strip()
        
        # Remove common issues
        result = result.replace('[object Object]', '"Not Specified"')
        result = result.replace('undefined', '"Not Specified"')
        result = result.replace('null', '"Not Specified"')
        
        # Parse and validate JSON
        try:
            parsed = json.loads(result)
            
            # Ensure all values are strings
            def ensure_strings(obj):
                if isinstance(obj, dict):
                    return {k: ensure_strings(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return ", ".join(str(item) for item in obj) if obj else "Not Specified"
                else:
                    return str(obj) if obj is not None else "Not Specified"
            
            parsed_strings = ensure_strings(parsed)
            
            # Add ICD coding for medical conditions
            if "Diagnosis" in parsed_strings and parsed_strings["Diagnosis"] != "Not Specified":
                diagnosis_text = parsed_strings["Diagnosis"]
                icd_result = code_medical_conditions_from_text(diagnosis_text)
                parsed_strings["ICD_Codes"] = {
                    "primary_code": icd_result["primary_code"],
                    "all_codes": icd_result["icd_codes"],
                    "confidence": icd_result["confidence"],
                    "coding_method": icd_result["coding_method"]
                }
            else:
                parsed_strings["ICD_Codes"] = {
                    "primary_code": "",
                    "all_codes": [],
                    "confidence": 0.0,
                    "coding_method": "none"
                }
            
            return json.dumps(parsed_strings)
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            if '{' in result and '}' in result:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_candidate = result[start:end]
                    try:
                        parsed = json.loads(json_candidate)
                        parsed_strings = ensure_strings(parsed)
                        return json.dumps(parsed_strings)
                    except json.JSONDecodeError:
                        pass
            
            # For radiology reports, try regex extraction as additional fallback
            if doc_type == "Radiology Report":
                try:
                    from utils.radiology_extractor import extract_radiology_fields
                    regex_result = extract_radiology_fields(text)
                    return regex_result
                except ImportError:
                    pass
            
            return json.dumps({
                "error": "Failed to parse LLM response as JSON",
                "raw_response": result[:500] + "..." if len(result) > 500 else result,
                "parsing_error": str(e),
                "fallback_fields": get_fallback_fields(doc_type)
            })
            
    except Exception as e:
        # For radiology reports, try regex extraction as fallback
        if doc_type == "Radiology Report":
            try:
                from utils.radiology_extractor import extract_radiology_fields
                regex_result = extract_radiology_fields(text)
                return regex_result
            except ImportError:
                pass
        
        return json.dumps({
            "error": "LLM extraction failed",
            "message": str(e),
            "fallback_fields": get_fallback_fields(doc_type)
        })

def get_fallback_fields(doc_type: str) -> dict:
    """
    Provide fallback fields when LLM is not available
    """
    fallback_templates = {
        "Discharge Summary": {
            "Patient Name": "Not Specified",
            "Age": "Not Specified",
            "Gender": "Not Specified",
            "UHID / IP Number": "Not Specified",
            "Admission Date": "Not Specified",
            "Discharge Date": "Not Specified",
            "Diagnosis": "Not Specified",
            "Procedure Performed": "Not Specified",
            "Treating Doctor": "Not Specified",
            "Hospital Name": "Not Specified",
            "Hospital Address": "Not Specified"
        },
        "Final Bill": {
            "Patient Name": "Not Specified",
            "Hospital Name": "Not Specified",
            "Bill Number": "Not Specified",
            "Bill Date": "Not Specified",
            "Admission Date": "Not Specified",
            "Discharge Date": "Not Specified",
            "Total Amount": "Not Specified",
            "Amount Paid": "Not Specified",
            "Amount Due": "Not Specified",
            "Room Charges": "Not Specified",
            "Doctor Charges": "Not Specified",
            "Pharmacy Charges": "Not Specified",
            "Diagnostics Charges": "Not Specified"
        },
        "Radiology Report": {
            "Patient Name": "Not Specified",
            "Age": "Not Specified",
            "Gender": "Not Specified",
            "Test Type": "Not Specified",
            "Examination Date": "Not Specified",
            "Clinical Indication": "Not Specified",
            "Findings": "Not Specified",
            "Impression": "Not Specified",
            "Radiologist Name": "Not Specified",
            "Hospital Name": "Not Specified"
        },
        "Claim Form": {
            "Insured Name": "Not Specified",
            "Policy Number": "Not Specified",
            "Claim Number": "Not Specified",
            "Hospital Name": "Not Specified",
            "Admission Date": "Not Specified",
            "Discharge Date": "Not Specified",
            "Diagnosis": "Not Specified",
            "Claimed Amount": "Not Specified",
            "Bank Account Details": "Not Specified"
        },
        "Cashless Authorization Letter": {
            "Patient Name": "Not Specified",
            "Policy Number": "Not Specified",
            "Authorization Number": "Not Specified",
            "Approved Amount": "Not Specified",
            "Validity Period": "Not Specified",
            "Hospital Name": "Not Specified",
            "Treatment Details": "Not Specified"
        }
    }
    
    return fallback_templates.get(doc_type, {
        "error": f"No fallback template available for {doc_type}",
        "Patient Name": "Not Specified",
        "Document Type": doc_type
    })
