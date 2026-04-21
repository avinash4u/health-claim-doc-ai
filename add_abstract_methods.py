#!/usr/bin/env python3
"""
Add Missing Abstract Methods to All Agents
"""

import os
import sys

def add_validate_input_method():
    """Add validate_input method to all agents"""
    print("🔧 Adding validate_input method to all agents...")
    
    validate_input_method = '''
    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input data for agent"""
        required_fields = ["claim_id", "claim_details", "policy_details"]
        return all(field in claim_data for field in required_fields)
'''
    
    agents_to_fix = [
        "agents/medical_agent.py",
        "agents/coverage_agent.py", 
        "agents/fraud_agent.py",
        "agents/calculation_agent.py"
    ]
    
    for agent_file in agents_to_fix:
        if os.path.exists(agent_file):
            with open(agent_file, "r") as f:
                content = f.read()
            
            if "def validate_input" not in content:
                print(f"  ✅ Adding to {os.path.basename(agent_file)}")
                
                # Find the class and add method after __init__
                class_end = content.find("def __init__(self):")
                if class_end > 0:
                    # Find the end of __init__ method
                    init_start = class_end
                    init_end = content.find("\n    def ", init_start + 1)
                    if init_end == -1:
                        init_end = len(content)
                    
                    # Insert validate_input method
                    new_content = content[:init_end] + "\n" + validate_input_method + "\n" + content[init_end:]
                    
                    with open(agent_file, "w") as f:
                        f.write(new_content)
                else:
                    print(f"  ❌ Could not find __init__ in {agent_file}")
            else:
                print(f"  ✅ Already exists in {os.path.basename(agent_file)}")
        else:
            print(f"  ❌ File not found: {agent_file}")

def main():
    """Add missing abstract methods"""
    print("🔧 ABSTRACT METHODS ADDER")
    print("=" * 50)
    
    try:
        add_validate_input_method()
        
        print("\n🎉 ABSTRACT METHODS ADDED")
        print("=" * 50)
        print("✅ validate_input method added to all agents")
        
        print("\n🚀 Next Steps:")
        print("  1. Run: python3 quick_test.py")
        print("  2. Run: python3 test_minimal_llm.py")
        print("  3. Run: python3 claim_adjudication_api.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to add methods: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
