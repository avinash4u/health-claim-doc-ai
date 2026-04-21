#!/usr/bin/env python3
"""
Debug PPC classification scores
"""

import os
from utils.ocr import extract_text
from utils.classifier import rule_based_classification

def debug_ppc_scores():
    print("🔍 Debugging PPC Classification Scores")
    print("=" * 50)
    
    # Find PPC file
    uploads_dir = "uploads"
    files = [f for f in os.listdir(uploads_dir) if "PPC_ff3b5bb4" in f]
    if not files:
        print("❌ PPC file not found")
        return
    
    file = files[0]
    file_path = os.path.join(uploads_dir, file)
    
    print(f"📁 File: {file}")
    print()
    
    # Extract text
    text = extract_text(file_path)
    print(f"📝 Text length: {len(text)} characters")
    print()
    
    # Show text preview
    print("📝 Text Preview:")
    print(text[:800] + "..." if len(text) > 800 else text)
    print()
    
    # Manual classification with debug
    from utils.classifier import DOCUMENT_RULES, rule_based_classification
    text_lower = text.lower()
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
            if kw in text_lower:
                score += 1
                print(f"   ✅ {doc_type}: '{kw}' (+1)")
        scores[doc_type] = score
    
    # Additional indicators
    cashless_indicators = [
        "cashless authorization", "cashless approval", "authorization letter",
        "pre-authorization", "pre auth", "approved amount",
        "authorization number", "validity period", "final authorization",
        "tpa approval", "insurance approval", "network hospital"
    ]
    
    print("\n💰 Cashless Authorization Indicators:")
    for phrase in cashless_indicators:
        if phrase in text_lower:
            scores["Cashless Authorization Letter"] = scores.get("Cashless Authorization Letter", 0) + 5
            print(f"   ✅ '{phrase}' (+5)")
    
    claim_form_indicators = [
        "claim form", "health insurance claim", "insured name", 
        "authorization letter", "pre-authorization", "pre auth",
        "policy holder", "claim amount", "reimbursement", "insurance company"
    ]
    
    print("\n📋 Claim Form Indicators:")
    for phrase in claim_form_indicators:
        if phrase in text_lower:
            scores["Claim Form"] = scores.get("Claim Form", 0) + 5
            print(f"   ✅ '{phrase}' (+5)")
    
    print("\n📊 Final Scores:")
    for doc_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            print(f"   {doc_type}: {score}")
    
    print(f"\n🏆 Winner: {max(scores, key=scores.get)} ({scores[max(scores, key=scores.get)]} points)")

if __name__ == "__main__":
    debug_ppc_scores()
