"""
Policy Validation Agent - Agent 2
Validates claim against insurance policy terms and conditions
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult
from utils.icd_coder import validate_icd_coverage

class PolicyValidationAgent(BaseAgent):
    """Agent for validating claims against insurance policy terms"""
    
    def __init__(self):
        super().__init__("Policy Validation Agent")
    
    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input contains policy information"""
        required_fields = ["policy_details", "claim_details"]
        return all(field in claim_data for field in required_fields)
    
    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Validate claim against policy terms and conditions"""
        try:
            policy_details = claim_data.get("policy_details", {})
            claim_details = claim_data.get("claim_details", {})
            extracted_data = claim_data.get("extracted_data", {})
            
            validation_results = {
                "policy_active": self._check_policy_status(policy_details),
                "coverage_active": self._check_coverage_dates(policy_details, claim_details),
                "sum_insured": self._get_sum_insured(policy_details),
                "policy_type": self._get_policy_type(policy_details),
                "waiting_period": self._check_waiting_period(policy_details, claim_details),
                "pre_existing_conditions": self._check_pre_existing_conditions(policy_details, claim_details),
                "room_rent_limits": self._check_room_rent_limits(policy_details, claim_details),
                "co_payment": self._check_co_payment(policy_details),
                "deductible": self._check_deductible(policy_details),
                "policy_exclusions": self._check_policy_exclusions(policy_details, claim_details),
                "icd_coverage": self._check_icd_coverage(extracted_data, policy_details)
            }
            
            # Calculate overall validation score
            validation_score = self._calculate_validation_score(validation_results)
            
            # Determine validation status
            status = self._determine_validation_status(validation_results)
            
            # Generate reasoning
            reasoning = self._generate_validation_reasoning(validation_results)
            
            return AgentResult(
                agent_name=self.name,
                status=status,
                data=validation_results,
                confidence=validation_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Policy validation failed: {e}")
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Policy validation failed: {str(e)}"
            )
    
    def _check_policy_status(self, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check if policy is active and in good standing"""
        policy_status = policy_details.get("status", "active")
        premium_status = policy_details.get("premium_status", "paid")
        
        # Default to active/paid if not specified
        if policy_status == "unknown":
            policy_status = "active"
        if premium_status == "unknown":
            premium_status = "paid"
        
        return {
            "is_active": policy_status.lower() == "active",
            "premium_paid": premium_status.lower() == "paid",
            "status": policy_status,
            "premium_status": premium_status
        }
    
    def _check_coverage_dates(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check if claim dates fall within policy coverage period"""
        policy_start = policy_details.get("start_date")
        policy_end = policy_details.get("end_date")
        claim_date = claim_details.get("admission_date") or claim_details.get("claim_date")
        
        return {
            "policy_start": policy_start,
            "policy_end": policy_end,
            "claim_date": claim_date,
            "within_coverage": self._is_date_within_range(claim_date, policy_start, policy_end)
        }
    
    def _get_sum_insured(self, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sum insured information"""
        sum_insured = policy_details.get("sum_insured", 0)
        remaining_sum_insured = policy_details.get("remaining_sum_insured", sum_insured)
        
        return {
            "total_sum_insured": sum_insured,
            "remaining_sum_insured": remaining_sum_insured,
            "utilized_amount": sum_insured - remaining_sum_insured
        }
    
    def _get_policy_type(self, policy_details: Dict[str, Any]) -> str:
        """Get policy type (individual, family, corporate, etc.)"""
        return policy_details.get("policy_type", "individual")
    
    def _check_waiting_period(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check if claim is within waiting period for specific conditions"""
        waiting_periods = policy_details.get("waiting_periods", {})
        policy_start = policy_details.get("start_date")
        claim_date = claim_details.get("admission_date") or claim_details.get("claim_date")
        
        # Check specific condition waiting periods
        diagnosis = claim_details.get("diagnosis", "").lower()
        applicable_waiting = 0
        
        for condition, days in waiting_periods.items():
            if condition.lower() in diagnosis:
                applicable_waiting = max(applicable_waiting, days)
        
        days_since_start = self._calculate_days_between(policy_start, claim_date)
        
        return {
            "applicable_waiting_days": applicable_waiting,
            "days_since_policy_start": days_since_start,
            "waiting_period_satisfied": days_since_start >= applicable_waiting if applicable_waiting > 0 else True
        }
    
    def _check_pre_existing_conditions(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check for pre-existing condition coverage"""
        ped_covered = policy_details.get("pre_existing_conditions_covered", False)
        waiting_period_ped = policy_details.get("ped_waiting_period", 0)
        
        diagnosis = claim_details.get("diagnosis", "")
        policy_start = policy_details.get("start_date")
        claim_date = claim_details.get("admission_date") or claim_details.get("claim_date")
        
        days_since_start = self._calculate_days_between(policy_start, claim_date)
        
        return {
            "ped_covered": ped_covered,
            "ped_waiting_period": waiting_period_ped,
            "days_since_start": days_since_start,
            "ped_waiting_satisfied": days_since_start >= waiting_period_ped if waiting_period_ped > 0 else True
        }
    
    def _check_room_rent_limits(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check room rent limits"""
        room_rent_limit = policy_details.get("room_rent_limits", {}).get("general_ward", 0)
        actual_room_rent = claim_details.get("room_charges", 0)
        
        # Ensure room_rent_limit is a number
        if isinstance(room_rent_limit, dict):
            room_rent_limit = 0
        
        return {
            "room_rent_limit": room_rent_limit,
            "actual_room_rent": actual_room_rent,
            "within_limit": actual_room_rent <= room_rent_limit if room_rent_limit > 0 else True
        }
    
    def _check_co_payment(self, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check co-payment requirements"""
        co_payment_percentage = policy_details.get("co_payment_percentage", 0)
        co_payment_amount = policy_details.get("co_payment_amount", 0)
        
        # Ensure numeric values
        try:
            co_payment_percentage = float(co_payment_percentage) if co_payment_percentage else 0
        except (ValueError, TypeError):
            co_payment_percentage = 0
        
        try:
            co_payment_amount = float(co_payment_amount) if co_payment_amount else 0
        except (ValueError, TypeError):
            co_payment_amount = 0
        
        return {
            "co_payment_percentage": co_payment_percentage,
            "co_payment_amount": co_payment_amount,
            "has_co_payment": co_payment_percentage > 0 or co_payment_amount > 0
        }
    
    def _check_deductible(self, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check deductible requirements"""
        deductible = policy_details.get("deductible_amount", 0)
        deductible_met = policy_details.get("deductible_met", False)
        
        # Ensure numeric values
        try:
            deductible = float(deductible) if deductible else 0
        except (ValueError, TypeError):
            deductible = 0
        
        return {
            "deductible_amount": deductible,
            "deductible_met": deductible_met,
            "has_deductible": deductible > 0
        }
    
    def _check_policy_exclusions(self, policy_details: Dict[str, Any], claim_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check for policy exclusions"""
        exclusions = policy_details.get("exclusions", [])
        diagnosis = claim_details.get("diagnosis", "")
        procedures = claim_details.get("procedure_performed", "")
        
        excluded_items = []
        
        for exclusion in exclusions:
            if exclusion.lower() in diagnosis.lower() or exclusion.lower() in procedures.lower():
                excluded_items.append(exclusion)
        
        return {
            "policy_exclusions": exclusions,
            "excluded_items": excluded_items,
            "has_exclusions": len(excluded_items) > 0
        }
    
    def _calculate_validation_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        score = 1.0
        
        # Deduct points for failed validations
        if not validation_results["policy_active"]["is_active"]:
            score -= 0.3
        
        if not validation_results["coverage_active"]["within_coverage"]:
            score -= 0.3
        
        if not validation_results["waiting_period"]["waiting_period_satisfied"]:
            score -= 0.2
        
        if not validation_results["pre_existing_conditions"]["ped_waiting_satisfied"]:
            score -= 0.2
        
        if validation_results["policy_exclusions"]["has_exclusions"]:
            score -= 0.3
        
        return max(0.0, score)
    
    def _determine_validation_status(self, validation_results: Dict[str, Any]) -> str:
        """Determine overall validation status"""
        critical_failures = []
        
        if not validation_results["policy_active"]["is_active"]:
            critical_failures.append("Policy not active")
        
        if not validation_results["coverage_active"]["within_coverage"]:
            critical_failures.append("Claim outside coverage period")
        
        if validation_results["policy_exclusions"]["has_exclusions"]:
            critical_failures.append("Claim contains excluded items")
        
        if critical_failures:
            return "rejected"
        
        # Check for issues that need review
        review_issues = []
        
        if not validation_results["waiting_period"]["waiting_period_satisfied"]:
            review_issues.append("Waiting period not satisfied")
        
        if not validation_results["pre_existing_conditions"]["ped_waiting_satisfied"]:
            review_issues.append("PED waiting period not satisfied")
        
        if review_issues:
            return "needs_review"
        
        return "approved"
    
    def _generate_validation_reasoning(self, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for validation results"""
        reasons = []
        
        if validation_results["policy_active"]["is_active"]:
            reasons.append("Policy is active and premiums paid")
        else:
            reasons.append("Policy issue detected")
        
        if validation_results["coverage_active"]["within_coverage"]:
            reasons.append("Claim within coverage period")
        else:
            reasons.append("Claim outside coverage period")
        
        if validation_results["policy_exclusions"]["has_exclusions"]:
            reasons.append(f"Exclusions found: {', '.join(validation_results['policy_exclusions']['excluded_items'])}")
        
        return "; ".join(reasons)
    
    def _is_date_within_range(self, date: str, start_date: str, end_date: str) -> bool:
        """Check if date is within range (simplified implementation)"""
        # In real implementation, use proper date parsing
        return True  # Simplified for demo
    
    def _calculate_days_between(self, start_date: str, end_date: str) -> int:
        """Calculate days between two dates (simplified implementation)"""
        # In real implementation, use proper date calculations
        return 30  # Simplified for demo
    
    def _check_icd_coverage(self, extracted_data: Dict[str, Any], policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check ICD code coverage against policy"""
        try:
            # Extract ICD codes from documents
            icd_codes = []
            documents = extracted_data.get("documents", [])
            
            for doc in documents:
                fields_str = doc.get("extracted_fields", "{}")
                if isinstance(fields_str, str):
                    try:
                        import json
                        fields = json.loads(fields_str)
                        icd_codes_data = fields.get("ICD_Codes", {})
                        if icd_codes_data.get("all_codes"):
                            icd_codes.extend(icd_codes_data["all_codes"])
                    except json.JSONDecodeError:
                        continue
            
            # Remove duplicates
            icd_codes = list(set(icd_codes))
            
            # Get policy coverage configuration
            policy_coverage = policy_details.get("coverage_details", {})
            if not policy_coverage:
                # Create default coverage if not specified
                policy_coverage = {
                    "covered_icd_codes": ["K35", "J18", "I21", "E11", "C80"],  # Common conditions
                    "excluded_icd_codes": [],
                    "limited_coverage_icd_codes": {}
                }
            
            # Validate coverage
            coverage_result = validate_icd_coverage(icd_codes, policy_coverage)
            
            return {
                "extracted_icd_codes": icd_codes,
                "coverage_validation": coverage_result,
                "overall_status": coverage_result["overall_status"],
                "coverage_percentage": coverage_result["coverage_percentage"],
                "detailed_results": coverage_result["detailed_results"]
            }
            
        except Exception as e:
            return {
                "extracted_icd_codes": [],
                "coverage_validation": {"error": str(e)},
                "overall_status": "unknown",
                "coverage_percentage": 0,
                "detailed_results": []
            }
