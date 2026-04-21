from typing import Dict, List
import re
import os
import ollama
from dotenv import load_dotenv

load_dotenv()

DOCUMENT_RULES: Dict[str, List[str]] = {
    "Discharge Summary": [
        "discharge summary", "date of admission", "date of discharge",
        "final diagnosis", "course in hospital", "advice on discharge"
    ],
    "Final Bill": [
        "final bill", "hospital bill", "invoice", "bill no", "bill date",
        "gross amount", "net amount", "amount payable", "room charges"
    ],
    "Interim Bill": [
        "interim bill", "provisional bill", "this is not a final bill"
    ],
    "Pharmacy Bill": [
        "pharmacy", "medical store", "batch no", "expiry date", "medicine name"
    ],
    "Diagnostic Report": [
        "lab report", "investigation report", "pathology", "test name",
        "reference range", "sample type"
    ],
    "Radiology Report": [
        "radiology", "x-ray", "mri", "ct scan", "ultrasound", "impression", "findings"
    ],
    "Claim Form": [
        "claim form", "health insurance claim", "policy number", "insured name",
        "hospital details", "declaration by insured"
    ],
    "Pre-Authorization Form": [
        "pre-authorization", "pre auth", "proposed treatment", "estimated cost",
        "expected date of admission"
    ],
    "Cashless Authorization Letter": [
        "cashless authorization", "approval letter", "approved amount",
        "authorization number", "validity period"
    ],
    "OPD Prescription": [
        "prescription", "rx", "take once daily", "follow-up after",
        "doctor signature", "patient complaints"
    ],
    "ID Proof": [
        "aadhaar", "uidai", "pan", "passport", "government of india", "photo id"
    ],
    "Policy Document": [
        "policy schedule", "policy document", "sum insured",
        "policy period", "nominee", "irdai"
    ],
    "Death Certificate": [
        "death certificate", "cause of death", "date of death",
        "registrar of births and deaths"
    ],
    "FIR / MLC Report": [
        "first information report", "fir", "mlc", "medico legal case",
        "police station", "accident", "assault"
    ],
    "ICU Chart / Nursing Notes": [
        "icu chart", "nursing notes", "vitals", "bp", "pulse",
        "temperature", "hourly monitoring"
    ],
    "OT Notes / Surgery Notes": [
        "operation theatre", "ot notes", "procedure performed",
        "surgeon", "anesthesia", "incision", "closure"
    ],
    "Implant Invoice": [
        "implant", "prosthesis", "serial number", "manufacturer", "batch number"
    ],
    "Lab Test Bill": [
        "lab bill", "diagnostic bill", "test charges", "invoice number", "gstin"
    ]
}

def rule_based_classification(text: str) -> str:
    text_lower = text.lower()
    scores = {}

    # First check for exact phrase matches with higher weights
    exact_matches = {
        "Discharge Summary": ["discharge summary"],
        "Final Bill": ["final bill", "hospital bill"],
        "Pharmacy Bill": ["pharmacy bill", "medical store"],
        "Diagnostic Report": ["lab report", "diagnostic report"],
        "Radiology Report": ["radiology report", "x-ray", "mri", "ct scan"],
        "Claim Form": ["claim form", "health insurance claim", "claim no", "medical bill for payment", "policy no", "insured name"],
        "Pre-Authorization Form": ["pre-authorization", "pre auth"],
        "Cashless Authorization Letter": ["cashless authorization", "approval letter"],
        "OPD Prescription": ["prescription", "rx"],
        "ID Proof": ["aadhaar", "pan", "passport"],
        "Policy Document": ["policy document", "policy schedule"],
        "Death Certificate": ["death certificate"],
        "FIR / MLC Report": ["first information report", "fir", "mlc"],
        "ICU Chart / Nursing Notes": ["icu chart", "nursing notes"],
        "OT Notes / Surgery Notes": ["ot notes", "surgery notes"],
        "Implant Invoice": ["implant", "prosthesis"],
        "Lab Test Bill": ["lab bill", "diagnostic bill"]
    }

    # Score exact phrase matches higher
    for doc_type, phrases in exact_matches.items():
        for phrase in phrases:
            if phrase in text_lower:
                scores[doc_type] = scores.get(doc_type, 0) + 3  # Higher weight for exact phrases

    # Then check individual keywords with lower weights
    for doc_type, keywords in DOCUMENT_RULES.items():
        score = scores.get(doc_type, 0)
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                score += 1
        scores[doc_type] = score

    # Additional checks for discharge summaries
    discharge_indicators = [
        "discharge summary", "date of admission", "date of discharge", 
        "final diagnosis", "course in hospital", "advice on discharge",
        "discharge advice", "hospital course", "patient discharged",
        "medical bill", "bill for payment", "hospital bill",
        "admission date", "consultant", "procedure", "on admission",
        "hospital course:", "physical examination", "pulse rate"
    ]
    
    if any(phrase in text_lower for phrase in discharge_indicators):
        # Don't match if it's clearly an authorization letter
        if not any(word in text_lower for word in ["authorization", "pre-authorization", "cashless"]):
            scores["Discharge Summary"] = scores.get("Discharge Summary", 0) + 5  # Extra weight for discharge summary indicators
    
    # Additional checks for final bills
    final_bill_indicators = [
        "final bill", "hospital bill", "invoice", "bill date", "medical bill",
        "gross amount", "net amount", "total amount", "amount payable",
        "room charges", "doctor charges", "nursing charges", "medicine charges",
        "hospital charges", "billing details", "payment due", "amount paid"
    ]
    
    if any(phrase in text_lower for phrase in final_bill_indicators):
        # If discharge indicators are strong, don't add much weight to final bill
        if scores.get("Discharge Summary", 0) >= 5:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 1  # Minimal weight
        else:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 5  # Full weight
    
    # Additional checks for pharmacy bills
    pharmacy_indicators = [
        "pharmacy", "medical store", "batch no", "expiry date", "medicine name",
        "drug name", "tablet", "capsule", "syrup", "injection", "ointment",
        "pharmacist", "dispensing", "prescription filled", "medicine charges"
    ]
    
    if any(phrase in text_lower for phrase in pharmacy_indicators):
        scores["Pharmacy Bill"] = scores.get("Pharmacy Bill", 0) + 5
    
    # Additional checks for diagnostic reports
    diagnostic_indicators = [
        "lab report", "investigation report", "pathology", "test name",
        "reference range", "sample type", "specimen", "blood test", "urine test",
        "hematology", "biochemistry", "microbiology", "serology", "histopathology"
    ]
    
    if any(phrase in text_lower for phrase in diagnostic_indicators):
        scores["Diagnostic Report"] = scores.get("Diagnostic Report", 0) + 5
    
    # Additional checks for radiology reports
    radiology_indicators = [
        "radiology", "x-ray", "mri", "ct scan", "ultrasound", "impression", "findings",
        "radiologist", "contrast", "scan", "imaging", "magnetic resonance", "computed tomography"
    ]
    
    if any(phrase in text_lower for phrase in radiology_indicators):
        scores["Radiology Report"] = scores.get("Radiology Report", 0) + 5
    
    # Additional checks for claim forms (more specific)
    claim_form_indicators = [
        "claim form", "health insurance claim", "insured name", 
        "authorization letter", "pre-authorization", "pre auth",
        "policy holder", "claim amount", "reimbursement", "insurance company"
    ]
    
    if any(phrase in text_lower for phrase in claim_form_indicators):
        scores["Claim Form"] = scores.get("Claim Form", 0) + 5  # Extra weight for claim form indicators
    
    # Additional checks for pre-authorization forms
    pre_auth_indicators = [
        "pre-authorization", "pre auth", "proposed treatment", "estimated cost",
        "expected date of admission", "treatment plan", "medical necessity",
        "prior authorization", "approval required", "estimated expenses"
    ]
    
    if any(phrase in text_lower for phrase in pre_auth_indicators):
        scores["Pre-Authorization Form"] = scores.get("Pre-Authorization Form", 0) + 5
    
    # Additional checks for cashless authorization letters
    cashless_indicators = [
        "cashless authorization", "cashless approval", "authorization letter",
        "pre-authorization", "pre auth", "approved amount",
        "authorization number", "validity period", "final authorization",
        "tpa approval", "insurance approval", "network hospital"
    ]
    
    if any(phrase in text_lower for phrase in cashless_indicators):
        scores["Cashless Authorization Letter"] = scores.get("Cashless Authorization Letter", 0) + 5  # Extra weight for cashless authorization
    
    # Additional checks for OPD prescriptions
    prescription_indicators = [
        "prescription", "rx", "take once daily", "follow-up after",
        "doctor signature", "patient complaints", "dosage", "frequency",
        "medicine", "drug", "tablet", "capsule", "syrup", "ointment"
    ]
    
    if any(phrase in text_lower for phrase in prescription_indicators):
        scores["OPD Prescription"] = scores.get("OPD Prescription", 0) + 5
    
    # Additional checks for ID proofs
    id_proof_indicators = [
        "aadhaar", "uidai", "pan", "passport", "government of india", "photo id",
        "identity card", "voter id", "driving license", "ration card"
    ]
    
    if any(phrase in text_lower for phrase in id_proof_indicators):
        scores["ID Proof"] = scores.get("ID Proof", 0) + 5
    
    # Additional checks for policy documents
    policy_indicators = [
        "policy schedule", "policy document", "sum insured", "policy period",
        "nominee", "irdai", "insurance policy", "terms and conditions",
        "premium", "coverage", "benefits", "exclusions"
    ]
    
    if any(phrase in text_lower for phrase in policy_indicators):
        scores["Policy Document"] = scores.get("Policy Document", 0) + 5
    
    # Additional checks for death certificates
    death_cert_indicators = [
        "death certificate", "cause of death", "date of death",
        "registrar of births and deaths", "deceased", "post mortem",
        "time of death", "place of death", "attending physician"
    ]
    
    if any(phrase in text_lower for phrase in death_cert_indicators):
        scores["Death Certificate"] = scores.get("Death Certificate", 0) + 5
    
    # Additional checks for FIR/MLC reports
    fir_mlc_indicators = [
        "first information report", "fir", "mlc", "medico legal case",
        "police station", "accident", "assault", "injury",
        "medicolegal", "police report", "criminal case"
    ]
    
    if any(phrase in text_lower for phrase in fir_mlc_indicators):
        scores["FIR / MLC Report"] = scores.get("FIR / MLC Report", 0) + 5
    
    # Additional checks for ICU charts
    icu_indicators = [
        "icu chart", "nursing notes", "vitals", "bp", "pulse",
        "temperature", "hourly monitoring", "intensive care", "critical care",
        "ventilator", "monitoring", "icu stay", "hourly chart"
    ]
    
    if any(phrase in text_lower for phrase in icu_indicators):
        scores["ICU Chart / Nursing Notes"] = scores.get("ICU Chart / Nursing Notes", 0) + 5
    
    # Additional checks for OT/surgery notes
    ot_indicators = [
        "operation theatre", "ot notes", "procedure performed",
        "surgeon", "anesthesia", "incision", "closure",
        "surgery", "operative", "surgical procedure", "operation"
    ]
    
    if any(phrase in text_lower for phrase in ot_indicators):
        scores["OT Notes / Surgery Notes"] = scores.get("OT Notes / Surgery Notes", 0) + 5
    
    # Additional checks for implant invoices
    implant_indicators = [
        "implant", "prosthesis", "serial number", "manufacturer", "batch number",
        "medical device", "artificial limb", "pacemaker", "stent", "valve"
    ]
    
    if any(phrase in text_lower for phrase in implant_indicators):
        scores["Implant Invoice"] = scores.get("Implant Invoice", 0) + 5
    
    # Additional checks for lab test bills
    lab_bill_indicators = [
        "lab bill", "diagnostic bill", "test charges", "invoice number", "gstin",
        "laboratory charges", "pathology charges", "diagnostic fees"
    ]
    
    if any(phrase in text_lower for phrase in lab_bill_indicators):
        scores["Lab Test Bill"] = scores.get("Lab Test Bill", 0) + 5
    
    # Distinguish between claim forms and medical bills with claim references
    # "claim no" or "policy no" alone shouldn't make it a claim form
    if "claim no" in text_lower or "policy no" in text_lower:
        if any(phrase in text_lower for phrase in ["medical bill", "bill for payment", "hospital bill", "bill no", "bill date"]):
            # This is likely a medical bill, not a claim form
            scores["Final Bill"] = scores.get("Final Bill", 0) + 3
            scores["Discharge Summary"] = scores.get("Discharge Summary", 0) + 2
        else:
            # This might be a claim form
            scores["Claim Form"] = scores.get("Claim Form", 0) + 3
    
    # Additional checks for final bills - but reduce weight if discharge indicators present
    final_bill_indicators = ["final bill", "hospital bill", "invoice", "bill date", "medical bill"]
    if any(phrase in text_lower for phrase in final_bill_indicators):
        # If discharge indicators are strong, don't add much weight to final bill
        if scores.get("Discharge Summary", 0) >= 5:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 1  # Minimal weight
        else:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 5  # Full weight

    best_match = max(scores, key=scores.get)
    
    # Tie-breaking: prioritize specific document types
    if scores.get("Cashless Authorization Letter", 0) > 0:
        # If cashless authorization has any score, prioritize it over claim form
        if best_match == "Claim Form" and scores["Cashless Authorization Letter"] >= scores["Claim Form"]:
            return "Cashless Authorization Letter"
    
    # Tie-breaking logic: prefer discharge summary when indicators conflict
    # Only run this if both have scores AND best match is one of them
    if scores["Discharge Summary"] > 0 and scores["Claim Form"] > 0 and best_match in ["Discharge Summary", "Claim Form"]:
        # Both have scores, check which has stronger indicators
        discharge_score = 0
        claim_score = 0
        
        # Count discharge indicators
        for phrase in discharge_indicators:
            if phrase in text_lower:
                discharge_score += 2  # Strong weight for discharge phrases
        
        # Count claim form indicators  
        for phrase in claim_form_indicators:
            if phrase in text_lower:
                claim_score += 2  # Strong weight for claim phrases
        
        if discharge_score > claim_score:
            return "Discharge Summary"
        elif claim_score > discharge_score:
            return "Claim Form"
    
    # Return the best match if no special tie-breaking applies
    if scores[best_match] >= 1:
        return best_match
    
    # Default to a common document type if no matches found
    if any(word in text_lower for word in ['medical', 'hospital', 'patient', 'doctor', 'health']):
        return "Discharge Summary"
    
    return "Unknown"

def ai_classification(text: str) -> str:
    prompt = f"""
You are a health insurance document classifier in India.

Classify this document into one of the following types:
{list(DOCUMENT_RULES.keys())}

Document text:
{text[:4000]}

Return only the document type.
"""
    try:
        response = ollama.chat(
            model='mistral',  # Using the model you have installed
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return "Unknown"

def classify_document(text: str) -> str:
    doc_type = rule_based_classification(text)
    if doc_type != "Unknown":
        return doc_type
    return ai_classification(text)
