import json
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult

class AmountCalculationAgent(BaseAgent):
    """Agent for calculating payable amounts and deductions"""
    
    def __init__(self):
        super().__init__("Amount Calculation Agent")
        self.logger = logging.getLogger(__name__)
    

    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input data for agent"""
        required_fields = ["claim_id", "claim_details", "policy_details"]
        return all(field in claim_data for field in required_fields)


    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Calculate payable amount for claim"""
        try:
            self.logger.info(f"Calculating amount for claim: {claim_data.get('claim_id')}")
            
            policy_details = claim_data.get("policy_details", {})
            claim_details = claim_data.get("claim_details", {})
            agent_results = claim_data.get("agent_results", {})
            
            # Calculate gross claim amount
            gross_amount = self._calculate_gross_amount(claim_details)
            
            # Calculate policy-based deductions
            policy_deductions = self._calculate_policy_deductions(policy_details, gross_amount)
            
            # Calculate network adjustments
            network_adjustments = self._calculate_network_adjustments(policy_details, claim_details)
            
            # Calculate fraud adjustments
            fraud_adjustments = self._calculate_fraud_adjustments(
                agent_results.get("fraud_agent", {}).get("data", {})
            )
            
            # Ensure all are dictionaries
            if not isinstance(policy_deductions, dict):
                policy_deductions = {"total_deductions": 0}
            if not isinstance(network_adjustments, dict):
                network_adjustments = {"total_adjustment": 0}
            if not isinstance(fraud_adjustments, dict):
                fraud_adjustments = {"fraud_adjustment": 0}
            
            # Calculate final payable amount
            final_calculation = self._calculate_final_amount(
                gross_amount, policy_deductions, network_adjustments, fraud_adjustments
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence({
                "gross_claim_amount": gross_amount,
                "final_calculation": final_calculation
            }, agent_results)
            
            # Determine status
            status = "approved" if confidence >= 0.7 else "needs_review"
            if confidence < 0.4:
                status = "rejected"
            
            reasoning = f"Amount calculation completed with confidence: {confidence:.2f}. "
            reasoning += "All deductions and adjustments applied."
            
            return AgentResult(
                agent_name=self.name,
                status=status,
                data={
                    "gross_claim_amount": gross_amount,
                    "policy_deductions": policy_deductions,
                    "network_adjustments": network_adjustments,
                    "fraud_adjustments": fraud_adjustments,
                    "final_calculation": final_calculation
                },
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Amount calculation failed: {e}")
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Amount calculation failed: {str(e)}"
            )
    
    def _calculate_gross_amount(self, claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate gross claim amount from claim details"""
        room_charges = claim_details.get("room_charges", 0)
        doctor_charges = claim_details.get("doctor_charges", 0)
        pharmacy_charges = claim_details.get("pharmacy_charges", 0)
        diagnostics_charges = claim_details.get("diagnostics_charges", 0)
        claimed_amount = claim_details.get("claimed_amount", 0)
        
        self.logger.info(f"Calculation input - Room: {room_charges}, Doctor: {doctor_charges}, Pharmacy: {pharmacy_charges}, Diagnostics: {diagnostics_charges}, Claimed: {claimed_amount}")
        
        # Use claimed amount if available, otherwise sum components
        total_gross = claimed_amount if claimed_amount > 0 else (
            room_charges + doctor_charges + pharmacy_charges + diagnostics_charges
        )
        
        self.logger.info(f"Calculated gross amount: {total_gross}")
        
        return {
            "total_gross_amount": total_gross,
            "room_charges": room_charges,
            "doctor_charges": doctor_charges,
            "pharmacy_charges": pharmacy_charges,
            "diagnostics_charges": diagnostics_charges,
            "claimed_amount": claimed_amount
        }
    
    def _calculate_policy_deductions(self, policy_details: Dict[str, Any], gross_amount: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate policy-based deductions"""
        total_gross = gross_amount.get("total_gross_amount", 0)
        
        # Co-payment
        co_payment_percentage = policy_details.get("co_payment_percentage", 0)
        co_payment_amount = total_gross * (co_payment_percentage / 100)
        
        # Deductible
        deductible_amount = policy_details.get("deductible_amount", 0)
        
        total_deductions = co_payment_amount + deductible_amount
        
        return {
            "co_payment_percentage": co_payment_percentage,
            "co_payment_amount": co_payment_amount,
            "deductible_amount": deductible_amount,
            "total_deductions": total_deductions
        }
    
    def _calculate_network_adjustments(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate network-based adjustments"""
        # Simple implementation - in real system, check hospital network status
        return {
            "network_hospital": True,
            "adjustment_percentage": 0,
            "total_adjustment": 0
        }
    
    def _calculate_fraud_adjustments(self, fraud_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate adjustments based on fraud detection"""
        if not fraud_result:
            return {
                "fraud_risk_level": "minimal_risk",
                "fraud_adjustment": 0,
                "fraud_penalty": 0
            }
        
        fraud_status = fraud_result.get("fraud_risk", "minimal_risk")
        fraud_penalty = 0
        
        if fraud_status == "high_risk":
            fraud_penalty = 100  # Reject claim
        elif fraud_status == "medium_risk":
            fraud_penalty = 0.5  # 50% reduction
        
        return {
            "fraud_risk_level": fraud_status,
            "fraud_adjustment": fraud_penalty,
            "fraud_penalty": fraud_penalty
        }
    
    def _calculate_final_amount(self, gross_amount: Dict[str, Any], 
                            policy_deductions: Dict[str, Any],
                            network_adjustments: Dict[str, Any],
                            fraud_adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final payable amount"""
        gross_total = gross_amount.get("total_gross_amount", 0)
        total_deductions = policy_deductions.get("total_deductions", 0) if isinstance(policy_deductions, dict) else 0
        network_adj = network_adjustments.get("total_adjustment", 0)
        fraud_adj = fraud_adjustments.get("fraud_adjustment", 0)
        
        # Calculate covered amount
        covered_amount = gross_total - total_deductions
        
        # Apply network adjustments
        fraud_penalty = fraud_adjustments.get("fraud_penalty", 0) if isinstance(fraud_adjustments, dict) else 0
        if fraud_penalty >= 100:
            covered_amount = 0  # Claim rejected
        elif fraud_penalty > 0:
            covered_amount *= (1 - fraud_penalty)
        
        # Ensure non-negative amount
        final_amount = max(0, covered_amount)
        
        return {
            "gross_amount": gross_total,
            "total_deductions": total_deductions,
            "total_co_payment": policy_deductions.get("co_payment_amount", 0),
            "total_deductible": policy_deductions.get("deductible_amount", 0),
            "network_adjustment": network_adj,
            "fraud_adjustment": fraud_adj,
            "final_payable_amount": final_amount,
            "amount_saved": gross_total - final_amount
        }
    
    def _calculate_confidence(self, calculation: Dict[str, Any], agent_results: Dict[str, Any]) -> float:
        """Calculate confidence in amount calculation"""
        confidence = 1.0
        
        # Check if all agents completed successfully
        for agent_name, agent_result in agent_results.items():
            if isinstance(agent_result, dict):
                if agent_result.get("status") == "error":
                    confidence -= 0.2
                elif agent_result.get("status") in ["rejected", "needs_review"]:
                    confidence -= 0.1
            elif hasattr(agent_result, 'status'):
                if agent_result.status == "error":
                    confidence -= 0.2
                elif agent_result.status in ["rejected", "needs_review"]:
                    confidence -= 0.1
        
        # Check calculation consistency
        final_amount = calculation.get("final_calculation", {}).get("final_payable_amount", 0)
        gross_amount = calculation.get("gross_claim_amount", {}).get("total_gross_amount", 0)
        
        if gross_amount > 0:
            settlement_ratio = final_amount / gross_amount
            if settlement_ratio > 1.0 or settlement_ratio < 0:
                confidence -= 0.3
        elif gross_amount == 0 and final_amount == 0:
            # Both zero amounts is expected for rejected claims
            pass
        elif gross_amount == 0:
            # Gross zero but final non-zero - inconsistent
            confidence -= 0.3
        else:
            # Normal case
            settlement_ratio = final_amount / gross_amount
            if settlement_ratio > 1.0 or settlement_ratio < 0:
                confidence -= 0.3
        
        return max(0.0, confidence)
