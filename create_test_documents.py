#!/usr/bin/env python3
"""
Create Test Documents for Document Processing Agent
"""

import os
import json

def create_test_documents():
    """Create test documents for testing"""
    print("📄 Creating Test Documents")
    print("-" * 40)
    
    # Create uploads directory
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create test discharge summary (text file)
    discharge_summary = """
PATIENT DISCHARGE SUMMARY

Patient Name: John Doe
Age: 45 Years
Gender: Male
UHID/IP Number: IP123456

Admission Date: 15/03/2024
Discharge Date: 18/03/2024
Number of Days: 3

Attending Doctor: Dr. Smith Johnson
Department: General Surgery

Diagnosis:
- Acute Appendicitis
- Peritonitis

Procedures Performed:
- Appendectomy (Laparoscopic)
- Antibiotic Therapy

Treating Doctor: Dr. Smith Johnson
Hospital: Metro General Hospital
Hospital Address: 123 Medical Street, City, State - 123456

Discharge Condition: Stable
Advice: Follow up after 7 days
Medications: Antibiotics, Pain killers
Next Review Date: 25/03/2024
"""
    
    discharge_file = os.path.join(uploads_dir, "test_discharge.txt")
    with open(discharge_file, "w") as f:
        f.write(discharge_summary)
    print(f"✅ Created: {discharge_file}")
    
    # Create test final bill (text file)
    final_bill = """
HOSPITAL FINAL BILL

Patient Name: John Doe
IP Number: IP123456
Admission Date: 15/03/2024
Discharge Date: 18/03/2024

Room Charges:
- Private Room (3 days @ 3000/day): 9000.00

Doctor Charges:
- Surgeon Fees: 15000.00
- Anesthetist Fees: 5000.00
- Consultant Fees: 8000.00

Pharmacy Charges:
- Medicines: 12000.00
- Consumables: 3000.00

Diagnostics Charges:
- Blood Tests: 2000.00
- X-Ray: 1500.00
- Ultrasound: 2500.00

Procedure Charges:
- Appendectomy: 25000.00
- OT Charges: 8000.00

Other Charges:
- Nursing: 6000.00
- Administrative: 2000.00

Gross Total: 100000.00
Discount: 0.00
Net Amount: 100000.00

Payment Status: Pending
"""
    
    bill_file = os.path.join(uploads_dir, "test_bill.txt")
    with open(bill_file, "w") as f:
        f.write(final_bill)
    print(f"✅ Created: {bill_file}")
    
    # Create claim form (text file)
    claim_form = """
HEALTH INSURANCE CLAIM FORM

Policy Number: POL123456
Policy Holder Name: John Doe
Patient Name: John Doe
Relationship: Self
Age: 45 Years
Gender: Male

Contact Information:
Mobile: 9876543210
Email: john.doe@email.com
Address: 123 Main Street, City, State - 123456

Hospitalization Details:
Hospital Name: Metro General Hospital
Hospital Address: 123 Medical Street, City, State - 123456
Admission Date: 15/03/2024
Discharge Date: 18/03/2024
Reason for Admission: Acute Appendicitis

Claim Amount: 100000.00
Claim Intimation: Yes
Intimation Date: 14/03/2024

Documents Attached:
1. Discharge Summary
2. Final Bill
3. Doctor Prescription
4. Investigation Reports

Declaration:
I hereby declare that the information provided is true and correct.
I authorize the insurance company to verify the details.

Signature: _________________
Date: 18/03/2024
"""
    
    claim_file = os.path.join(uploads_dir, "test_claim.txt")
    with open(claim_file, "w") as f:
        f.write(claim_form)
    print(f"✅ Created: {claim_file}")
    
    # Create radiology report (text file)
    radiology_report = """
RADIOLOGY REPORT

Patient Name: Jane Smith
Age: 58 Years
Gender: Female
Referring Doctor: Dr. Robert Brown
Examination Date: 15/04/2022

Clinical Indication:
Suspected lung mass based on chest X-ray. Patient presents with persistent cough and weight loss.

Examination:
- Chest X-Ray (PA and Lateral view)
- CT Scan of Chest with contrast
- Blood investigations

Findings:
A round, well-defined opacity is observed in right lower lobe of lung. 
Measurements suggest a size of approximately 3 cm. 
The density is consistent with solid tissue. No evidence of cavitation.
No pleural effusion. Cardiac silhouette is normal.
No mediastinal lymphadenopathy.

Impression:
Likely malignant pulmonary nodule. Recommend biopsy for definitive diagnosis.
Differential diagnosis includes granuloma and hamartoma.

Recommendations:
1. CT-guided biopsy of the lung lesion
2. PET scan for metabolic activity assessment
3. Surgical consultation for further management

Radiologist: Dr. Jane Smith
Qualification: MD, DNB (Radiology)
Registration Number: A12345

Hospital: St. Mary's Medical Center
Report Date: 16/04/2022
"""
    
    radiology_file = os.path.join(uploads_dir, "test_radiology.txt")
    with open(radiology_file, "w") as f:
        f.write(radiology_report)
    print(f"✅ Created: {radiology_file}")
    
    print(f"\n📊 Created {len(os.listdir(uploads_dir))} test documents in '{uploads_dir}' directory")
    
    # List created files
    print("\n📋 Created Files:")
    for filename in sorted(os.listdir(uploads_dir)):
        filepath = os.path.join(uploads_dir, filename)
        size = os.path.getsize(filepath)
        print(f"   - {filename} ({size} bytes)")
    
    return True

def main():
    """Create all test documents"""
    print("🚀 Creating Test Documents for Document Processing Agent")
    print("=" * 60)
    
    try:
        success = create_test_documents()
        
        if success:
            print("\n🟢 TEST DOCUMENTS CREATED SUCCESSFULLY")
            print("\n📋 Ready for testing:")
            print("   1. Document Processing Agent")
            print("   2. OCR and Classification")
            print("   3. Field Extraction")
            print("   4. End-to-End Claim Processing")
            
            print("\n🔧 Test commands:")
            print("   python test_radiology_extraction.py")
            print("   python test_document_agent.py")
            print("   python quick_test.py")
        else:
            print("\n🔴 FAILED TO CREATE TEST DOCUMENTS")
            
    except Exception as e:
        print(f"\n❌ Error creating test documents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
