#!/usr/bin/env python3
"""
Test LLM extraction directly
"""

import json
import ollama

def test_llm_extraction():
    print("🔍 Testing LLM Extraction Directly")
    print("=" * 50)
    
    # Simple test text
    test_text = """
    Patient Name: John Doe
    Age: 45 years
    Gender: Male
    Hospital: General Hospital
    Diagnosis: Hypertension
    """
    
    # Simple prompt
    prompt = f"""
Extract patient information from this text and return ONLY JSON:

{{
  "Patient Name": "extract name",
  "Age": "extract age",
  "Gender": "extract gender",
  "Hospital": "extract hospital",
  "Diagnosis": "extract diagnosis"
}}

Text:
{test_text}

JSON Response:
"""
    
    try:
        print("📝 Sending prompt to Ollama...")
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        result = response['message']['content'].strip()
        print(f"📄 Raw response: {repr(result)}")
        print(f"📄 Response length: {len(result)}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            print("✅ Successfully parsed JSON:")
            for key, value in parsed.items():
                print(f"   {key}: {value}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
            # Try to extract JSON from response
            if '{' in result and '}' in result:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_candidate = result[start:end]
                    print(f"🔍 Extracted JSON candidate: {repr(json_candidate)}")
                    try:
                        parsed = json.loads(json_candidate)
                        print("✅ Successfully parsed extracted JSON:")
                        for key, value in parsed.items():
                            print(f"   {key}: {value}")
                    except json.JSONDecodeError:
                        print("❌ Still failed to parse extracted JSON")
        
    except Exception as e:
        print(f"❌ Ollama error: {e}")

if __name__ == "__main__":
    test_llm_extraction()
