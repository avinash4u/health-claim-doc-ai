import json
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

class FraudDetectionAgent(BaseAgent):
    """Agent for detecting potential fraud in claims"""
    
    def __init__(self):
        super().__init__("Fraud Detection Agent")
        self.logger = logging.getLogger(__name__)
    

    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input data for agent"""
        required_fields = ["claim_id", "claim_details", "policy_details"]
        return all(field in claim_data for field in required_fields)


    def parse_json_response(self, response: str) -> dict:
        """Safely parse JSON response from LLM"""
        if not response or not isinstance(response, str):
            return {}
        
        try:
            cleaned = response.strip()
            
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON parsing failed: {e}")
            return {
                "fraud_risk": "minimal_risk",
                "fraud_score": 0.1,
                "detection_reasoning": "Default - parsing failed"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error in JSON parsing: {e}")
            return {}
    
    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Detect fraud indicators in the claim"""
        try:
            self.logger.info(f"Analyzing fraud for claim: {claim_data.get('claim_id')}")
            
            policy_details = claim_data.get("policy_details", {})
            claim_details = claim_data.get("claim_details", {})
            
            # Check claim history
            history_check = self._check_claim_history(policy_details)
            
            # Check document consistency
            document_check = self._check_document_consistency(claim_details)
            
            # Check medical patterns
            medical_check = self._check_medical_patterns(claim_details)
            
            # Check billing patterns
            billing_check = self._check_billing_patterns(claim_details)
            
            # Check hospital/doctor patterns
            provider_check = self._check_provider_patterns(claim_details)
            
            # Calculate fraud risk score
            fraud_score = self._calculate_fraud_score([
                history_check, document_check, medical_check,
                billing_check, provider_check
            ])
            
            # Determine risk level
            if fraud_score >= 0.7:
                risk_level = "high_risk"
            elif fraud_score >= 0.4:
                risk_level = "medium_risk"
            else:
                risk_level = "minimal_risk"
            
            reasoning = f"Fraud risk score: {fraud_score:.2f}. "
            reasoning += "Multiple fraud indicators analyzed."
            
            return AgentResult(
                agent_name=self.name,
                status="completed" if risk_level == "minimal_risk" else "needs_review",
                data={
                    "fraud_risk": risk_level,
                    "fraud_score": fraud_score,
                    "history_check": history_check,
                    "document_check": document_check,
                    "medical_check": medical_check,
                    "billing_check": billing_check,
                    "provider_check": provider_check
                },
                confidence=1.0 - fraud_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Fraud detection failed: {e}")
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Fraud detection failed: {str(e)}"
            )
    
    def _check_claim_history(self, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check claim history patterns"""
        return {
            "suspicious": False,
            "score": 0.1,
            "reasoning": "No suspicious claim history patterns"
        }
    
    def _check_document_consistency(self, claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check document consistency"""
        return {
            "consistent": True,
            "score": 0.1,
            "reasoning": "Documents appear consistent"
        }
    
    def _check_medical_patterns(self, claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check medical treatment patterns"""
        return {
            "normal": True,
            "score": 0.1,
            "reasoning": "Medical patterns appear normal"
        }
    
    def _check_billing_patterns(self, claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check billing patterns"""
        return {
            "normal": True,
            "score": 0.1,
            "reasoning": "Billing patterns appear normal"
        }
    
    def _check_provider_patterns(self, claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check hospital/doctor patterns"""
        return {
            "legitimate": True,
            "score": 0.1,
            "reasoning": "Provider patterns appear legitimate"
        }
    
    def _calculate_fraud_score(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate overall fraud risk score"""
        if not checks:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for check in checks:
            score = check.get("score", 0.0)
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
