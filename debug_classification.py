#!/usr/bin/env python3
"""
Debug classification to see scoring details
"""

import os
import re
from utils.ocr import extract_text
from utils.classifier import DOCUMENT_RULES

def debug_classification():
    print("🔍 Classification Debug Script")
    print("=" * 50)
    
    # Find the specific DCS file
    uploads_dir = "uploads"
    files = [f for f in os.listdir(uploads_dir) if f.startswith("69fc0a79") and "DCS_afecaa69" in f]
    if not files:
        print("❌ DCS file not found")
        return
    
    latest_file = files[0]
    file_path = os.path.join(uploads_dir, latest_file)
    
    print(f"📁 Analyzing: {latest_file}")
    print()
    
    # Extract text
    text = extract_text(file_path)
    text_lower = text.lower()
    
    print("📝 Text Preview:")
    print(text[:1000] + "..." if len(text) > 1000 else text)
    print("\n" + "=" * 50 + "\n")
    
    # Classification scoring
    scores = {}
    
    # Exact phrase matches
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
    
    print("🎯 Exact Phrase Matches:")
    for doc_type, phrases in exact_matches.items():
        for phrase in phrases:
            if phrase in text_lower:
                scores[doc_type] = scores.get(doc_type, 0) + 3
                print(f"   ✅ {doc_type}: '{phrase}' (+3)")
    
    print("\n🔍 Keyword Matches:")
    for doc_type, keywords in DOCUMENT_RULES.items():
        score = scores.get(doc_type, 0)
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                score += 1
                print(f"   ✅ {doc_type}: '{kw}' (+1)")
        scores[doc_type] = score
    
    # Additional indicators - match exact logic from classifier
    discharge_indicators = [
        "discharge summary", "date of admission", "date of discharge", 
        "final diagnosis", "course in hospital", "advice on discharge",
        "discharge advice", "hospital course", "patient discharged",
        "medical bill", "bill for payment", "hospital bill",
        "admission date", "consultant", "procedure", "on admission",
        "hospital course:", "physical examination", "pulse rate"
    ]
    
    claim_form_indicators = [
        "claim form", "health insurance claim", "insured name", 
        "authorization letter", "pre-authorization", "pre auth"
    ]
    
    print("\n🏥 Discharge Indicators:")
    for phrase in discharge_indicators:
        if phrase in text_lower:
            scores["Discharge Summary"] = scores.get("Discharge Summary", 0) + 5
            print(f"   ✅ '{phrase}' (+5)")
    
    print("\n📋 Claim Form Indicators:")
    for phrase in claim_form_indicators:
        if phrase in text_lower:
            scores["Claim Form"] = scores.get("Claim Form", 0) + 5
            print(f"   ✅ '{phrase}' (+5)")
    
    # Distinguish between claim forms and medical bills with claim references
    if "claim no" in text_lower or "policy no" in text_lower:
        if any(phrase in text_lower for phrase in ["medical bill", "bill for payment", "hospital bill", "bill no", "bill date"]):
            # This is likely a medical bill, not a claim form
            scores["Final Bill"] = scores.get("Final Bill", 0) + 3
            scores["Discharge Summary"] = scores.get("Discharge Summary", 0) + 2
            print(f"\n💰 Medical Bill with Claim Reference: Final Bill (+3), Discharge Summary (+2)")
        else:
            # This might be a claim form
            scores["Claim Form"] = scores.get("Claim Form", 0) + 3
            print(f"\n📋 Claim Form Indicators: Claim Form (+3)")
    
    # Additional checks for final bills - but reduce weight if discharge indicators present
    final_bill_indicators = ["final bill", "hospital bill", "invoice", "bill date", "medical bill"]
    if any(phrase in text_lower for phrase in final_bill_indicators):
        # If discharge indicators are strong, don't add much weight to final bill
        if scores.get("Discharge Summary", 0) >= 5:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 1  # Minimal weight
            print(f"\n💰 Final Bill Indicators (reduced): Final Bill (+1)")
        else:
            scores["Final Bill"] = scores.get("Final Bill", 0) + 5  # Full weight
            print(f"\n💰 Final Bill Indicators (full): Final Bill (+5)")
    
    print("\n📊 Final Scores:")
    for doc_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            print(f"   {doc_type}: {score}")
    
    best_match = max(scores, key=scores.get)
    print(f"\n🏆 Winner: {best_match} ({scores[best_match]} points)")

if __name__ == "__main__":
    debug_classification()
