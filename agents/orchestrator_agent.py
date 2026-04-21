"""
Claim Orchestrator Agent - Agent 7
Coordinates all agents and makes final claim decision
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult
from .document_agent import DocumentProcessingAgent
from .policy_agent import PolicyValidationAgent
from .medical_agent import MedicalNecessityAgent
from .coverage_agent import CoverageVerificationAgent
from .fraud_agent import FraudDetectionAgent
from .calculation_agent import AmountCalculationAgent

class ClaimOrchestratorAgent(BaseAgent):
    """Master orchestrator agent for end-to-end claim adjudication"""
    
    def __init__(self):
        super().__init__("Claim Orchestrator Agent")
        
        # Initialize all agents
        self.document_agent = DocumentProcessingAgent()
        self.policy_agent = PolicyValidationAgent()
        self.medical_agent = MedicalNecessityAgent()
        self.coverage_agent = CoverageVerificationAgent()
        self.fraud_agent = FraudDetectionAgent()
        self.calculation_agent = AmountCalculationAgent()
        
        self.agents = {
            "document_agent": self.document_agent,
            "policy_agent": self.policy_agent,
            "medical_agent": self.medical_agent,
            "coverage_agent": self.coverage_agent,
            "fraud_agent": self.fraud_agent,
            "calculation_agent": self.calculation_agent
        }
    
    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input contains required claim information"""
        required_fields = ["claim_id", "documents", "policy_details"]
        return all(field in claim_data for field in required_fields)
    
    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate end-to-end claim adjudication process"""
        try:
            self.logger.info(f"Starting claim adjudication for claim_id: {claim_data.get('claim_id')}")
            
            # Step 1: Document Processing
            doc_result = self._process_documents(claim_data)
            if doc_result.status == "error":
                return doc_result
            
            # Step 2: Extract claim details from documents
            claim_details = self._extract_claim_details(doc_result.data)
            claim_data["claim_details"] = claim_details
            claim_data["extracted_data"] = doc_result.data
            
            # Debug: Log claim details being passed to calculation
            self.logger.info(f"Passing to calculation agent - Claim details: {claim_details}")
            
            # Step 3: Parallel processing of validation agents
            validation_results = self._run_validation_agents(claim_data)
            
            # Step 4: Amount calculation
            calc_result = self._calculate_amounts(claim_data, validation_results)
            
            # Add calculation agent to validation results for reporting
            validation_results["calculation_agent"] = calc_result
            
            # Step 5: Final decision making
            final_decision = self._make_final_decision(validation_results, calc_result)
            
            # Step 6: Generate comprehensive report
            adjudication_report = self._generate_adjudication_report(
                claim_data, doc_result, validation_results, calc_result, final_decision
            )
            
            return AgentResult(
                agent_name=self.name,
                status=final_decision["decision"],
                data=adjudication_report,
                confidence=final_decision["confidence"],
                reasoning=final_decision["reasoning"]
            )
            
        except Exception as e:
            self.logger.error(f"Claim orchestration failed: {e}")
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Claim orchestration failed: {str(e)}"
            )
    
    def _process_documents(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Process all documents in the claim"""
        self.logger.info("Step 1: Processing documents")
        return self.document_agent.process(claim_data)
    
    def _extract_claim_details(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured claim details from processed documents"""
        self.logger.info(f"Starting claim details extraction from: {extracted_data}")
        
        # Handle error case
        if not isinstance(extracted_data, dict) or "error" in extracted_data:
            self.logger.info("Error case in extracted data, returning empty claim details")
            return {
                "claim_id": "",
                "patient_name": "",
                "age": "",
                "gender": "",
                "hospital_name": "",
                "admission_date": "",
                "discharge_date": "",
                "diagnosis": "",
                "procedure_performed": "",
                "claimed_amount": 0,
                "room_charges": 0,
                "doctor_charges": 0,
                "pharmacy_charges": 0,
                "diagnostics_charges": 0
            }
        
        claim_details = {
            "claim_id": extracted_data.get("claim_id", ""),
            "patient_name": "",
            "age": "",
            "gender": "",
            "hospital_name": "",
            "admission_date": "",
            "discharge_date": "",
            "diagnosis": "",
            "procedure_performed": "",
            "claimed_amount": 0,
            "room_charges": 0,
            "doctor_charges": 0,
            "pharmacy_charges": 0,
            "diagnostics_charges": 0
        }
        
        # Extract from documents
        documents = extracted_data.get("documents", [])
        for doc in documents:
            # Parse extracted_fields from JSON string
            fields_str = doc.get("extracted_fields", "{}")
            if isinstance(fields_str, str):
                try:
                    import json
                    fields = json.loads(fields_str)
                except json.JSONDecodeError:
                    fields = {}
            else:
                fields = fields_str
            
            doc_type = doc.get("document_type", "")
            
            # Extract patient information
            if not claim_details["patient_name"]:
                claim_details["patient_name"] = fields.get("Patient Name", "")
            if not claim_details["age"]:
                claim_details["age"] = fields.get("Age", "")
            if not claim_details["gender"]:
                claim_details["gender"] = fields.get("Gender", "")
            
            # Extract hospital information
            if not claim_details["hospital_name"]:
                claim_details["hospital_name"] = fields.get("Hospital Name", "")
            
            # Extract dates
            if not claim_details["admission_date"]:
                claim_details["admission_date"] = fields.get("Admission Date", "")
            if not claim_details["discharge_date"]:
                claim_details["discharge_date"] = fields.get("Discharge Date", "")
            
            # Extract medical information
            if not claim_details["diagnosis"]:
                claim_details["diagnosis"] = fields.get("Diagnosis", "")
            if not claim_details["procedure_performed"]:
                claim_details["procedure_performed"] = fields.get("Procedure Performed", "")
            
            # Extract financial information from bills and discharge summaries
            if doc_type in ["Final Bill", "Interim Bill", "Discharge Summary"]:
                room_amount = self._parse_amount(fields.get("Room Charges", "0"))
                doctor_amount = self._parse_amount(fields.get("Doctor Charges", "0"))
                pharmacy_amount = self._parse_amount(fields.get("Pharmacy Charges", "0"))
                diagnostics_amount = self._parse_amount(fields.get("Diagnostics Charges", "0"))
                total_amount = self._parse_amount(fields.get("Total Amount", "0"))
                
                self.logger.info(f"Document {doc_type} - Room: {room_amount}, Doctor: {doctor_amount}, Pharmacy: {pharmacy_amount}, Diagnostics: {diagnostics_amount}, Total: {total_amount}")
                
                claim_details["room_charges"] += room_amount
                claim_details["doctor_charges"] += doctor_amount
                claim_details["pharmacy_charges"] += pharmacy_amount
                claim_details["diagnostics_charges"] += diagnostics_amount
                claim_details["claimed_amount"] += total_amount
        
        return claim_details
    
    def _run_validation_agents(self, claim_data: Dict[str, Any]) -> Dict[str, AgentResult]:
        """Run all validation agents in parallel"""
        self.logger.info("Step 2: Running validation agents")
        
        validation_results = {}
        
        # Run agents that don't depend on each other
        independent_agents = ["policy_agent", "medical_agent", "coverage_agent", "fraud_agent"]
        
        for agent_name in independent_agents:
            agent = self.agents[agent_name]
            try:
                result = agent.process(claim_data)
                validation_results[agent_name] = result
                self.logger.info(f"{agent_name} completed with status: {result.status}")
            except Exception as e:
                self.logger.error(f"{agent_name} failed: {e}")
                validation_results[agent_name] = AgentResult(
                    agent_name=agent_name,
                    status="error",
                    data={"error": str(e)},
                    confidence=0.0,
                    reasoning=f"Agent failed: {str(e)}"
                )
        
        return validation_results
    
    def _calculate_amounts(self, claim_data: Dict[str, Any], validation_results: Dict[str, AgentResult]) -> AgentResult:
        """Calculate final amounts"""
        self.logger.info("Step 3: Calculating amounts")
        
        calc_data = claim_data.copy()
        calc_data["agent_results"] = {name: result.to_dict() for name, result in validation_results.items()}
        
        return self.calculation_agent.process(calc_data)
    
    def _make_final_decision(self, validation_results: Dict[str, AgentResult], calc_result: AgentResult) -> Dict[str, Any]:
        """Make final claim decision based on all agent results"""
        self.logger.info("Step 4: Making final decision")
        
        decision_factors = {
            "policy_valid": validation_results.get("policy_agent", AgentResult("", "", {}, 0.0, "")).status != "rejected",
            "medically_necessary": validation_results.get("medical_agent", AgentResult("", "", {}, 0.0, "")).status != "rejected",
            "coverage_available": validation_results.get("coverage_agent", AgentResult("", "", {}, 0.0, "")).status != "rejected",
            "fraud_risk_acceptable": validation_results.get("fraud_agent", AgentResult("", "", {}, 0.0, "")).status != "high_risk",
            "amount_calculable": calc_result.status != "error"
        }
        
        # Calculate overall confidence
        confidences = [
            validation_results.get("policy_agent", AgentResult("", "", {}, 0.0, "")).confidence,
            validation_results.get("medical_agent", AgentResult("", "", {}, 0.0, "")).confidence,
            validation_results.get("coverage_agent", AgentResult("", "", {}, 0.0, "")).confidence,
            calc_result.confidence
        ]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Make decision
        if not all(decision_factors.values()):
            decision = "rejected"
            reasoning = "Claim rejected due to policy violations"
        elif any(result.status in ["needs_review", "partial_coverage"] for result in validation_results.values()):
            decision = "needs_review"
            reasoning = "Claim requires manual review"
        else:
            decision = "approved"
            reasoning = "Claim approved for payment"
        
        # Check for high fraud risk
        fraud_result = validation_results.get("fraud_agent")
        if fraud_result and fraud_result.status == "high_risk":
            decision = "rejected"
            reasoning = "Claim rejected due to high fraud risk"
            overall_confidence *= 0.5
        
        return {
            "decision": decision,
            "confidence": overall_confidence,
            "reasoning": reasoning,
            "decision_factors": decision_factors,
            "agent_statuses": {name: result.status for name, result in validation_results.items()}
        }
    
    def _generate_adjudication_report(self, claim_data: Dict[str, Any], doc_result: AgentResult, 
                                     validation_results: Dict[str, AgentResult], calc_result: AgentResult, 
                                     final_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive adjudication report"""
        self.logger.info("Step 5: Generating adjudication report")
        
        # Debug: Log claim details being used for report
        claim_details = claim_data.get("claim_details", {})
        self.logger.info(f"Report generation - Claim details: {claim_details}")
        
        report = {
            "claim_summary": {
                "claim_id": claim_data.get("claim_id", ""),
                "patient_name": claim_details.get("patient_name", ""),
                "hospital_name": claim_details.get("hospital_name", ""),
                "admission_date": claim_details.get("admission_date", ""),
                "discharge_date": claim_details.get("discharge_date", ""),
                "claimed_amount": claim_details.get("claimed_amount", 0)
            },
            "claim_details": claim_details,
            "document_processing": {
                "status": doc_result.status,
                "documents_processed": len(doc_result.data.get("documents", [])),
                "document_types": doc_result.data.get("summary", {}),
                "confidence": doc_result.confidence
            },
            "validation_results": {
                name: {
                    "status": result.status,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "data": result.data if hasattr(result, 'data') else {}
                }
                for name, result in validation_results.items()
            },
            "financial_calculation": {
                "status": calc_result.status,
                "gross_amount": calc_result.data.get("final_calculation", {}).get("gross_amount", 0),
                "approved_amount": calc_result.data.get("final_calculation", {}).get("final_payable_amount", 0),
                "payable_amount": calc_result.data.get("final_calculation", {}).get("final_payable_amount", 0),
                "settlement_ratio": calc_result.data.get("final_calculation", {}).get("final_payable_amount", 0) / max(calc_result.data.get("final_calculation", {}).get("gross_amount", 1), 1)
            },
            "final_decision": final_decision,
            "processing_timeline": self._generate_processing_timeline(),
            "recommendations": self._generate_recommendations(validation_results, calc_result),
            "next_steps": self._generate_next_steps(final_decision["decision"])
        }
        
        return report
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount from string"""
        try:
            # Remove currency symbols and handle comma-separated numbers
            cleaned = amount_str.replace("₹", "").replace("$", "").strip()
            
            # Handle Indian number format with commas (e.g., "Rs. 2,50,000")
            if "Rs." in cleaned:
                # Remove "Rs." prefix first
                cleaned = cleaned.replace("Rs.", "")
            
            if "," in cleaned:
                # Remove all commas and convert to float
                cleaned = cleaned.replace(",", "")
            
            return float(cleaned) if cleaned else 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def _generate_processing_timeline(self) -> List[Dict[str, str]]:
        """Generate processing timeline"""
        from datetime import datetime
        return [
            {"step": "Document Upload", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Document Processing", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Policy Validation", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Medical Necessity Check", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Coverage Verification", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Fraud Detection", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Amount Calculation", "status": "Completed", "timestamp": datetime.now().isoformat()},
            {"step": "Final Decision", "status": "Completed", "timestamp": datetime.now().isoformat()}
        ]
    
    def _generate_recommendations(self, validation_results: Dict[str, AgentResult], calc_result: AgentResult) -> List[str]:
        """Generate recommendations based on agent results"""
        recommendations = []
        
        # Policy recommendations
        policy_result = validation_results.get("policy_agent")
        if policy_result and policy_result.status == "needs_review":
            recommendations.append("Verify policy terms and waiting periods")
        
        # Medical recommendations
        medical_result = validation_results.get("medical_agent")
        if medical_result and medical_result.status == "needs_review":
            recommendations.append("Obtain medical expert opinion on treatment necessity")
        
        # Coverage recommendations
        coverage_result = validation_results.get("coverage_agent")
        if coverage_result and coverage_result.status == "partial_coverage":
            recommendations.append("Explain coverage limitations to policyholder")
        
        # Fraud recommendations
        fraud_result = validation_results.get("fraud_agent")
        if fraud_result and fraud_result.status in ["medium_risk", "high_risk"]:
            recommendations.append("Conduct detailed fraud investigation")
        
        return recommendations
    
    def _generate_next_steps(self, decision: str) -> List[str]:
        """Generate next steps based on decision"""
        if decision == "approved":
            return [
                "Initiate payment processing",
                "Send approval notification to policyholder",
                "Update claim management system",
                "Archive claim documents"
            ]
        elif decision == "needs_review":
            return [
                "Assign to senior claims officer",
                "Request additional documentation if needed",
                "Schedule review meeting",
                "Notify policyholder of review status"
            ]
        else:  # rejected
            return [
                "Send rejection letter with detailed reasons",
                "Provide appeal process information",
                "Update claim management system",
                "Archive claim documents"
            ]
