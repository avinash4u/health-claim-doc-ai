"""
Agentic AI Claim Adjudication API
FastAPI endpoints for end-to-end claim processing
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import os
import json
from datetime import datetime

from agents.orchestrator_agent import ClaimOrchestratorAgent

app = FastAPI(
    title="Agentic AI Claim Adjudication API",
    description="Multi-agent system for end-to-end insurance claim processing",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ClaimOrchestratorAgent()

# Pydantic models
class ClaimSubmission(BaseModel):
    claim_id: str
    policy_number: str
    patient_name: str
    documents: List[Dict[str, Any]]
    policy_details: Dict[str, Any]

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    decision: str
    confidence: float
    payable_amount: float
    processing_time: float
    adjudication_report: Dict[str, Any]

class PolicyDetails(BaseModel):
    policy_number: str
    policy_holder_name: str
    sum_insured: float
    start_date: str
    end_date: str
    policy_type: str
    premium_status: str
    waiting_periods: Dict[str, int]
    exclusions: List[str]
    room_rent_limit: float
    co_payment_percentage: float
    deductible_amount: float

# Storage for claims (in production, use database)
claims_storage = {}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Agentic AI Claim Adjudication System",
        "version": "2.0.0",
        "agents": [
            "Document Processing Agent",
            "Policy Validation Agent", 
            "Medical Necessity Agent",
            "Coverage Verification Agent",
            "Fraud Detection Agent",
            "Amount Calculation Agent",
            "Claim Orchestrator Agent"
        ]
    }

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return {
        "orchestrator": "active",
        "document_agent": "active",
        "policy_agent": "active", 
        "medical_agent": "active",
        "coverage_agent": "active",
        "fraud_agent": "active",
        "calculation_agent": "active"
    }

@app.post("/claim/submit", response_model=ClaimResponse)
async def submit_claim(claim_submission: ClaimSubmission):
    """Submit a claim for adjudication"""
    try:
        start_time = datetime.now()
        
        # Process claim through orchestrator
        claim_data = {
            "claim_id": claim_submission.claim_id,
            "documents": claim_submission.documents,
            "policy_details": claim_submission.policy_details
        }
        
        result = orchestrator.process(claim_data)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract payable amount
        payable_amount = 0
        if result.data and "financial_calculation" in result.data:
            payable_amount = result.data["financial_calculation"].get("payable_amount", 0)
        
        # Store claim result
        claims_storage[claim_submission.claim_id] = {
            "submission": claim_submission.dict(),
            "result": result.to_dict(),
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
        return ClaimResponse(
            claim_id=claim_submission.claim_id,
            status=result.status,
            decision=result.data.get("final_decision", {}).get("decision", "unknown"),
            confidence=result.confidence,
            payable_amount=payable_amount,
            processing_time=processing_time,
            adjudication_report=result.data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claim processing failed: {str(e)}")

@app.post("/claim/upload-and-process")
async def upload_and_process_claim(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    policy_number: str = "",
    policy_holder_name: str = "",
    sum_insured: float = 0,
    start_date: str = "",
    end_date: str = "",
    policy_type: str = "individual",
    premium_status: str = "paid",
    co_payment_percentage: float = 0,
    deductible_amount: float = 0
):
    """Upload documents and process claim in one step"""
    try:
        # Generate claim ID
        claim_id = f"CLAIM_{uuid.uuid4().hex[:8].upper()}"
        
        # Save uploaded files
        documents = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, f"{claim_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            documents.append({
                "file_name": file.filename,
                "file_path": file_path,
                "file_size": len(content)
            })
        
        # Create policy details
        policy_details = {
            "policy_number": policy_number,
            "policy_holder_name": policy_holder_name,
            "sum_insured": sum_insured,
            "start_date": start_date,
            "end_date": end_date,
            "policy_type": policy_type,
            "premium_status": premium_status,
            "waiting_periods": {},
            "exclusions": [],
            "room_rent_limit": 0,
            "co_payment_percentage": co_payment_percentage,
            "deductible_amount": deductible_amount
        }
        
        # Process claim
        claim_data = {
            "claim_id": claim_id,
            "documents": documents,
            "policy_details": policy_details
        }
        
        result = orchestrator.process(claim_data)
        
        # Extract payable amount
        payable_amount = 0
        if result.data and "financial_calculation" in result.data:
            payable_amount = result.data["financial_calculation"].get("payable_amount", 0)
        
        # Store claim result
        claims_storage[claim_id] = {
            "documents": documents,
            "policy_details": policy_details,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "claim_id": claim_id,
            "status": result.status,
            "decision": result.data.get("final_decision", {}).get("decision", "unknown"),
            "confidence": result.confidence,
            "payable_amount": payable_amount,
            "adjudication_report": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claim processing failed: {str(e)}")

@app.get("/claim/{claim_id}")
async def get_claim_status(claim_id: str):
    """Get claim status and details"""
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_data = claims_storage[claim_id]
    return {
        "claim_id": claim_id,
        "status": claim_data["result"]["status"],
        "decision": claim_data["result"]["data"].get("final_decision", {}).get("decision", "unknown"),
        "confidence": claim_data["result"]["confidence"],
        "payable_amount": claim_data["result"]["data"].get("financial_calculation", {}).get("payable_amount", 0),
        "timestamp": claim_data["timestamp"],
        "adjudication_report": claim_data["result"]["data"]
    }

@app.get("/claims")
async def list_claims():
    """List all processed claims"""
    claims_summary = []
    
    for claim_id, claim_data in claims_storage.items():
        result = claim_data["result"]
        claims_summary.append({
            "claim_id": claim_id,
            "status": result["status"],
            "decision": result["data"].get("final_decision", {}).get("decision", "unknown"),
            "confidence": result["confidence"],
            "payable_amount": result["data"].get("financial_calculation", {}).get("payable_amount", 0),
            "timestamp": claim_data["timestamp"]
        })
    
    return {
        "total_claims": len(claims_summary),
        "claims": claims_summary
    }

@app.delete("/claim/{claim_id}")
async def delete_claim(claim_id: str):
    """Delete a claim"""
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Delete associated files
    claim_data = claims_storage[claim_id]
    if "documents" in claim_data:
        for doc in claim_data["documents"]:
            file_path = doc.get("file_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
    
    del claims_storage[claim_id]
    return {"message": f"Claim {claim_id} deleted successfully"}

@app.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get analytics dashboard data"""
    if not claims_storage:
        return {
            "total_claims": 0,
            "approved_claims": 0,
            "rejected_claims": 0,
            "review_claims": 0,
            "total_amount_claimed": 0,
            "total_amount_paid": 0,
            "average_processing_time": 0,
            "decision_distribution": {}
        }
    
    total_claims = len(claims_storage)
    approved_claims = 0
    rejected_claims = 0
    review_claims = 0
    total_claimed = 0
    total_paid = 0
    processing_times = []
    
    decision_distribution = {}
    
    for claim_id, claim_data in claims_storage.items():
        result = claim_data["result"]
        decision = result["data"].get("final_decision", {}).get("decision", "unknown")
        
        if decision == "approved":
            approved_claims += 1
        elif decision == "rejected":
            rejected_claims += 1
        elif decision in ["needs_review", "partial_coverage"]:
            review_claims += 1
        
        decision_distribution[decision] = decision_distribution.get(decision, 0) + 1
        
        # Financial calculations
        financial_data = result["data"].get("financial_calculation", {})
        total_claimed += financial_data.get("gross_claim_amount", 0)
        total_paid += financial_data.get("payable_amount", 0)
        
        # Processing time
        if "processing_time" in claim_data:
            processing_times.append(claim_data["processing_time"])
    
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    return {
        "total_claims": total_claims,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "review_claims": review_claims,
        "total_amount_claimed": total_claimed,
        "total_amount_paid": total_paid,
        "average_processing_time": avg_processing_time,
        "decision_distribution": decision_distribution,
        "approval_rate": (approved_claims / total_claims * 100) if total_claims > 0 else 0,
        "rejection_rate": (rejected_claims / total_claims * 100) if total_claims > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
