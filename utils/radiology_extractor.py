import re
import json

def extract_radiology_fields(text: str) -> dict:
    """
    Extract radiology report fields using regex patterns
    """
    text_lower = text.lower()
    
    # Initialize result
    result = {
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
    }
    
    # Extract Patient Name
    name_patterns = [
        r"name[:\s]+([a-z\s]+?)(?:\n|age|sex|mr|mrs|dr)",
        r"patient[:\s]+([a-z\s]+?)(?:\n|age|sex|mr|mrs|dr)",
        r"mr\.?\s+([a-z\s]+?)(?:\n|age|sex|mr|mrs|dr)",
        r"mrs\.?\s+([a-z\s]+?)(?:\n|age|sex|mr|mrs|dr)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            name = match.group(1).strip().title()
            if len(name) > 2 and len(name.split()) >= 2:
                result["Patient Name"] = name
                break
    
    # Extract Age
    age_patterns = [
        r"age[:\s]+(\d{1,3})\s*(?:years|yrs|y)?",
        r"(\d{1,3})\s*(?:years|yrs|y)\s*old",
        r"age\s*[:\-]?\s*(\d{1,3})",
        r"(\d{1,3})\s*years?\s*old",
        r"age\s*(\d{1,3})"
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, text_lower)
        if match:
            age = match.group(1)
            # Filter out unrealistic ages
            if 0 < int(age) < 120:
                result["Age"] = age
                break
    
    # Extract Gender
    if re.search(r"\b(male|male patient|m)\b", text_lower):
        result["Gender"] = "Male"
    elif re.search(r"\b(female|female patient|f)\b", text_lower):
        result["Gender"] = "Female"
    
    # Extract Test Type
    test_types = {
        "x-ray": "X-ray",
        "xr": "X-ray",
        "mri": "MRI",
        "magnetic resonance": "MRI",
        "ct": "CT Scan",
        "cat scan": "CT Scan",
        "ultrasound": "Ultrasound",
        "usg": "Ultrasound",
        "sonography": "Ultrasound",
        "echo": "Echocardiogram",
        "ecg": "ECG",
        "ekg": "EKG"
    }
    
    for key, value in test_types.items():
        if re.search(rf"\b{key}\b", text_lower):
            result["Test Type"] = value
            break
    
    # Extract Date
    date_patterns = [
        r"date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{2,4}[-/]\d{1,2}[-/]\d{1,2})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["Examination Date"] = match.group(1)
            break
    
    # Extract Hospital Name
    hospital_patterns = [
        r"hospital[:\s]+([a-z\s]+?)(?:\n|address|phone)",
        r"institute[:\s]+([a-z\s]+?)(?:\n|address|phone)",
        r"([a-z\s]+?hospital)(?:\n|address|phone)",
        r"([a-z\s]+?institute)(?:\n|address|phone)",
        r"metro heart institute with multispeciality",
        r"([a-z\s]+?heart\s+[a-z\s]+?institute)",
        r"([a-z\s]+?medical\s+[a-z\s]+?center)"
    ]
    
    # First try specific hospital names
    if "metro heart institute" in text_lower:
        result["Hospital Name"] = "Metro Heart Institute with Multispeciality"
    elif "metro heart" in text_lower:
        result["Hospital Name"] = "Metro Heart Institute"
    else:
        # Try general patterns
        for pattern in hospital_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                hospital = match.group(1).strip().title()
                if len(hospital) > 3:
                    result["Hospital Name"] = hospital
                    break
    
    # Extract Findings (look for detailed text sections)
    findings_patterns = [
        r"findings[:\s\n]+(.*?)(?:impression|conclusion|report|\n\n)",
        r"report[:\s\n]+(.*?)(?:impression|conclusion|\n\n)",
        r"examination[:\s\n]+(.*?)(?:impression|conclusion|\n\n)"
    ]
    
    for pattern in findings_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            findings = match.group(1).strip()
            if len(findings) > 20:
                result["Findings"] = findings[:500] + "..." if len(findings) > 500 else findings
                break
    
    # Extract Impression/Conclusion
    impression_patterns = [
        r"impression[:\s\n]+(.*?)(?:\n\n|report|findings|$)",
        r"conclusion[:\s\n]+(.*?)(?:\n\n|report|findings|$)",
        r"diagnosis[:\s\n]+(.*?)(?:\n\n|report|findings|$)"
    ]
    
    for pattern in impression_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            impression = match.group(1).strip()
            if len(impression) > 10:
                result["Impression"] = impression[:300] + "..." if len(impression) > 300 else impression
                break
    
    # Extract Clinical Indication
    indication_patterns = [
        r"indication[:\s\n]+(.*?)(?:findings|report|examination|\n\n)",
        r"clinical[:\s\n]+(.*?)(?:findings|report|examination|\n\n)",
        r"reason[:\s\n]+(.*?)(?:findings|report|examination|\n\n)"
    ]
    
    for pattern in indication_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            indication = match.group(1).strip()
            if len(indication) > 10:
                result["Clinical Indication"] = indication[:300] + "..." if len(indication) > 300 else indication
                break
    
    # Extract Radiologist Name
    doctor_patterns = [
        r"radiologist[:\s]+([a-z\s]+?)(?:\n|sign|date)",
        r"dr\.?\s+([a-z\s]+?)(?:\n|sign|date|md)",
        r"physician[:\s]+([a-z\s]+?)(?:\n|sign|date)"
    ]
    
    for pattern in doctor_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            doctor = match.group(1).strip().title()
            if len(doctor) > 3:
                result["Radiologist Name"] = doctor
                break
    
    return json.dumps(result)
